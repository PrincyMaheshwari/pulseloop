import logging
import re
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.services.ai_service import ai_service
from app.services.content_service import content_service

logger = logging.getLogger(__name__)

class QuizService:
    def __init__(self):
        self.db = get_database()
    
    def get_or_create_quiz(self, content_id: str, version: int = 1) -> Optional[dict]:
        """Get existing quiz or create a new one"""
        try:
            # Try to get existing quiz
            quiz = self.db.quizzes.find_one({
                "content_id": content_id,
                "version": version
            })
            
            if quiz:
                quiz["id"] = str(quiz["_id"])
                return quiz
            
            # Create new quiz
            content_item = content_service.get_content_item(content_id)
            if not content_item:
                return None
            
            summary = content_item.get("summary", "")
            transcript = content_item.get("transcript", "")
            content_type = content_item.get("type", "article")
            transcript_segments = content_item.get("transcript_segments", []) or []
            
            # Generate quiz questions
            if content_type in ("video", "podcast") and transcript:
                quiz_source_text = transcript
            else:
                quiz_source_text = content_item.get("description", "") or summary

            questions_data = ai_service.generate_quiz(
                quiz_source_text,
                summary,
                content_type,
                transcript_segments=transcript_segments,
            )
            
            # Convert to QuizQuestion format
            questions = []
            for q in questions_data:
                questions.append({
                    "question": q.get("question", ""),
                    "options": q.get("options", []),
                    "correct_answer": q.get("correct_answer", 0),
                    "explanation": q.get("explanation", "")
                })
            
            # Create quiz document
            quiz_data = {
                "content_id": content_id,
                "questions": questions,
                "version": version,
                "created_at": datetime.utcnow()
            }
            
            result = self.db.quizzes.insert_one(quiz_data)
            quiz_data["id"] = str(result.inserted_id)
            quiz_data["_id"] = str(result.inserted_id)
            
            return quiz_data
        except Exception as e:
            logger.error(f"Error getting or creating quiz: {e}")
            return None
    
    def submit_quiz(
        self,
        user_id: str,
        content_id: str,
        quiz_id: str,
        answers: List[int],
        attempt_number: int = 1
    ) -> Dict:
        """Submit quiz answers and return results"""
        try:
            # Get quiz
            quiz = self.db.quizzes.find_one({"_id": ObjectId(quiz_id)})
            if not quiz:
                return {"error": "Quiz not found"}
            
            questions = quiz.get("questions", [])
            if len(answers) != len(questions):
                return {"error": "Invalid number of answers"}
            
            # Check answers
            correct_count = 0
            wrong_count = 0
            wrong_indices = []
            
            for i, (question, answer) in enumerate(zip(questions, answers)):
                if answer == question.get("correct_answer"):
                    correct_count += 1
                else:
                    wrong_count += 1
                    wrong_indices.append(i)
            
            # Get content item for review hints
            content_item = content_service.get_content_item(content_id)
            summary = content_item.get("summary", "") if content_item else ""
            transcript = content_item.get("transcript", "") if content_item else ""
            transcript_segments = content_item.get("transcript_segments", []) if content_item else []
            content_type = content_item.get("type", "article") if content_item else "article"
            
            # Calculate tech score change
            tech_score_change = 0
            passed = wrong_count <= 2  # Pass if 3+ correct (2 or fewer wrong)
            
            if passed:
                if attempt_number == 1:
                    tech_score_change = 10  # First try bonus
                elif attempt_number == 2:
                    tech_score_change = 6   # Second try
                else:
                    tech_score_change = 3   # Multiple retries
            else:
                tech_score_change = -2  # Penalty for failed attempt
            
            # Create quiz attempt record
            attempt_data = {
                "user_id": user_id,
                "content_id": content_id,
                "quiz_id": quiz_id,
                "attempt_number": attempt_number,
                "answers": answers,
                "correct_count": correct_count,
                "wrong_count": wrong_count,
                "passed": passed,
                "tech_score_change": tech_score_change,
                "created_at": datetime.utcnow()
            }
            
            # If failed, generate review hints and new quiz
            if not passed:
                # Generate review hints
                if content_type in ("video", "podcast") and transcript_segments:
                    review_hints = self._generate_timestamp_review_hints(
                        wrong_indices,
                        questions,
                        transcript_segments,
                    )
                else:
                    review_hints = ai_service.generate_review_hints(
                        summary,
                        transcript,
                        content_type,
                        wrong_indices,
                        questions,
                        transcript_segments=transcript_segments,
                    )
                attempt_data["review_hints"] = review_hints
                
                # Generate retry quiz
                wrong_concepts = review_hints.get("concepts", [])
                new_quiz_questions = ai_service.generate_retry_quiz(
                    summary,
                    transcript,
                    content_type,
                    wrong_concepts,
                    questions,
                    transcript_segments=transcript_segments,
                )
                
                # Create new quiz version
                new_version = quiz.get("version", 1) + 1
                new_quiz_data = {
                    "content_id": content_id,
                    "questions": new_quiz_questions,
                    "version": new_version,
                    "created_at": datetime.utcnow()
                }
                new_quiz_result = self.db.quizzes.insert_one(new_quiz_data)
                new_quiz_id = str(new_quiz_result.inserted_id)
                
                attempt_data["next_quiz_id"] = new_quiz_id
            
            # Save attempt
            self.db.quiz_attempts.insert_one(attempt_data)
            
            # Update user tech score (both positive and negative)
            self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"tech_score": tech_score_change}}
            )
            
            return {
                "status": "passed" if passed else "retry",
                "correct_count": correct_count,
                "wrong_count": wrong_count,
                "tech_score_change": tech_score_change,
                "review_hints": attempt_data.get("review_hints"),
                "next_quiz_id": attempt_data.get("next_quiz_id")
            }
        except Exception as e:
            logger.error(f"Error submitting quiz: {e}")
            return {"error": str(e)}

    def _generate_timestamp_review_hints(
        self,
        wrong_indices: List[int],
        questions: List[Dict],
        transcript_segments: List[Dict],
    ) -> Dict:
        hints: List[str] = []
        concepts: List[str] = []
        used_ranges = set()

        for idx in wrong_indices:
            if idx >= len(questions):
                continue
            question = questions[idx]
            query_text = f"{question.get('question', '')} {question.get('explanation', '')}"
            concepts.append(question.get("question", "").strip())

            for segment in self._find_relevant_segments(query_text, transcript_segments):
                start_ms = segment.get("start_ms", 0)
                end_ms = segment.get("end_ms", start_ms)
                range_str = self._format_ms_range(start_ms, end_ms)
                if range_str not in used_ranges:
                    hints.append(range_str)
                    used_ranges.add(range_str)

        # Ensure we always return something, even if no matches were found
        if not hints and transcript_segments:
            fallback_segment = transcript_segments[0]
            hints.append(self._format_ms_range(fallback_segment.get("start_ms", 0), fallback_segment.get("end_ms", 0)))

        concepts = list(dict.fromkeys([c for c in concepts if c]))

        return {
            "timestamps": hints,
            "articleHighlights": [],
            "concepts": concepts,
        }

    def _find_relevant_segments(
        self,
        query_text: str,
        segments: List[Dict],
        limit: int = 2,
    ) -> List[Dict]:
        if not segments:
            return []

        query_tokens = self._tokenise(query_text)
        if not query_tokens:
            return segments[:limit]

        scored_segments: List[Dict] = []
        for segment in segments:
            text = segment.get("text", "")
            if not text:
                continue
            segment_tokens = self._tokenise(text)
            if not segment_tokens:
                continue
            overlap = len(query_tokens.intersection(segment_tokens))
            if overlap > 0:
                scored_segments.append({"segment": segment, "score": overlap})

        if not scored_segments:
            return segments[:limit]

        scored_segments.sort(key=lambda item: item["score"], reverse=True)
        return [item["segment"] for item in scored_segments[:limit]]

    @staticmethod
    def _tokenise(text: str) -> set:
        tokens = set()
        for token in re.findall(r"\b\w+\b", text.lower()):
            if len(token) > 3:
                tokens.add(token)
        return tokens

    @staticmethod
    def _format_ms_range(start_ms: int, end_ms: int) -> str:
        def _fmt(ms: int) -> str:
            minutes = ms // 60000
            seconds = (ms % 60000) // 1000
            return f"{minutes:02d}:{seconds:02d}"

        return f"{_fmt(start_ms)}-{_fmt(end_ms)}"

# Singleton instance
quiz_service = QuizService()


