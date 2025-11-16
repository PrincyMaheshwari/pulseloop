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
            if content_type == "podcast" and transcript:
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
                candidate_segments = self._select_relevant_segments(
                    wrong_indices,
                    questions,
                    transcript_segments,
                )
                review_hints = ai_service.generate_review_hints(
                    summary,
                    transcript,
                    content_type,
                    wrong_indices,
                    questions,
                    transcript_segments=transcript_segments,
                    candidate_segments=candidate_segments,
                ) or {}
                if not isinstance(review_hints, dict):
                    review_hints = {"articleHighlights": [], "timestamps": [], "concepts": []}
                if content_type == "podcast" and candidate_segments:
                    timestamps = review_hints.get("timestamps") or []
                    if not timestamps:
                        fallback_ranges = []
                        for segment in candidate_segments[:5]:
                            start_ms = segment.get("start_ms", 0)
                            end_ms = segment.get("end_ms", start_ms)
                            fallback_ranges.append(self._format_ms_to_mmss(start_ms) + "-" + self._format_ms_to_mmss(end_ms))
                        if fallback_ranges:
                            review_hints["timestamps"] = fallback_ranges
                if "concepts" not in review_hints or not review_hints["concepts"]:
                    inferred_concepts = [
                        questions[idx].get("question", "").strip()
                        for idx in wrong_indices
                        if 0 <= idx < len(questions)
                    ]
                    review_hints["concepts"] = [c for c in inferred_concepts if c]

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

            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            current_tech_score = user_doc.get("tech_score", 0) if user_doc else 0
            current_streak = user_doc.get("current_streak", 0) if user_doc else 0
            longest_streak = user_doc.get("longest_streak", 0) if user_doc else 0

            return {
                "status": "passed" if passed else "retry",
                "correct_count": correct_count,
                "wrong_count": wrong_count,
                "tech_score_change": tech_score_change,
                "tech_score": current_tech_score,
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "review_hints": attempt_data.get("review_hints"),
                "next_quiz_id": attempt_data.get("next_quiz_id")
            }
        except Exception as e:
            logger.error(f"Error submitting quiz: {e}")
            return {"error": str(e)}

    def _select_relevant_segments(
        self,
        wrong_indices: List[int],
        questions: List[Dict],
        transcript_segments: Optional[List[Dict]],
        max_segments: int = 20,
    ) -> List[Dict]:
        if not transcript_segments:
            return []

        keyword_sets: List[set] = []
        for idx in wrong_indices:
            if 0 <= idx < len(questions):
                q = questions[idx]
                text = f"{q.get('question', '')} {q.get('explanation', '')}"
                tokens = {token for token in re.findall(r"[A-Za-z]{4,}", text.lower())}
                if tokens:
                    keyword_sets.append(tokens)

        scored_segments: List[tuple[int, Dict]] = []
        for segment in transcript_segments:
            segment_text = segment.get("text", "")
            if not segment_text:
                continue
            lower_segment = segment_text.lower()
            score = 0
            for keywords in keyword_sets:
                score += sum(1 for kw in keywords if kw in lower_segment)
            if score > 0:
                scored_segments.append((score, segment))

        if not scored_segments:
            return transcript_segments[:max_segments]

        scored_segments.sort(key=lambda pair: pair[0], reverse=True)

        selected: List[Dict] = []
        seen_ranges = set()
        for score, segment in scored_segments:
            if len(selected) >= max_segments:
                break
            start_ms = segment.get("start_ms", 0)
            end_ms = segment.get("end_ms", start_ms)
            bucket = (start_ms // 10000, end_ms // 10000)
            if bucket in seen_ranges:
                continue
            seen_ranges.add(bucket)
            selected.append(segment)

        return selected

    @staticmethod
    def _format_ms_to_mmss(ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02}:{remaining_seconds:02}"

# Singleton instance
quiz_service = QuizService()


