import logging
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
            
            # Generate quiz questions
            questions_data = ai_service.generate_quiz(
                content_item.get("description", ""),
                summary,
                content_type
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
                review_hints = ai_service.generate_review_hints(
                    summary,
                    transcript,
                    content_type,
                    wrong_indices,
                    questions
                )
                attempt_data["review_hints"] = review_hints
                
                # Generate retry quiz
                wrong_concepts = review_hints.get("concepts", [])
                new_quiz_questions = ai_service.generate_retry_quiz(
                    summary,
                    transcript,
                    content_type,
                    wrong_concepts,
                    questions
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

# Singleton instance
quiz_service = QuizService()


