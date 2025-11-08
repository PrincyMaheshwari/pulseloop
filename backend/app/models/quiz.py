from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option
    explanation: Optional[str] = None

class Quiz(BaseModel):
    id: Optional[str] = None
    content_id: str
    questions: List[QuizQuestion]
    version: int = 1  # Version number for retry quizzes
    created_at: datetime = datetime.utcnow()

class QuizAttempt(BaseModel):
    id: Optional[str] = None
    user_id: str
    content_id: str
    quiz_id: str
    attempt_number: int = 1
    answers: List[int]  # Selected option indices
    correct_count: int = 0
    wrong_count: int = 0
    passed: bool = False
    tech_score_change: int = 0  # Points gained/lost
    review_hints: Optional[Dict] = None  # Paragraph indices or timestamps
    next_quiz_id: Optional[str] = None  # If retry needed
    created_at: datetime = datetime.utcnow()


