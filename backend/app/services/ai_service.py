import json
import logging
from typing import List, Dict, Optional
from openai import AzureOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
    
    def generate_summary(self, content: str, content_type: str = "article") -> str:
        """Generate a concise summary of the content"""
        try:
            prompt = f"""Generate a concise summary (2-3 paragraphs) of the following {content_type} content.
            
Content:
{content[:4000]}

Summary:"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates clear, concise summaries of technical and industry content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def generate_tags(self, content: str, summary: str) -> List[str]:
        """Generate relevant tags for the content"""
        try:
            prompt = f"""Based on the following content and summary, generate 3-5 relevant tags (single words or short phrases).
            
Summary: {summary}

Tags (comma-separated):"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates relevant tags for content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            tags = response.choices[0].message.content.strip().split(",")
            return [tag.strip() for tag in tags]
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return []
    
    def generate_quiz(self, content: str, summary: str, content_type: str = "article") -> List[Dict]:
        """Generate 5 multiple-choice questions based on the content"""
        try:
            prompt = f"""Generate 5 multiple-choice questions based on the following content summary.
            
Summary: {summary}

For each question, provide:
- question: The question text
- options: List of 4 answer options
- correct_answer: Index (0-3) of the correct answer
- explanation: Brief explanation of why this answer is correct

Return the response as a JSON object with a "questions" array. Each question should have:
- question: string
- options: array of 4 strings
- correct_answer: integer (0-3)
- explanation: string

Example format:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": 0,
      "explanation": "..."
    }}
  ]
}}"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates educational quizzes. Always return valid JSON with a 'questions' array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            # Try to parse as JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    logger.error(f"Could not parse quiz JSON: {content}")
                    return []
            
            # Handle both direct array and wrapped in object
            if isinstance(result, dict) and "questions" in result:
                return result["questions"]
            elif isinstance(result, list):
                return result
            else:
                # Try to extract questions from the response
                return list(result.values()) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            raise
    
    def generate_review_hints(
        self, 
        summary: str, 
        transcript: Optional[str],
        content_type: str,
        wrong_answers: List[int],
        original_quiz: List[Dict]
    ) -> Dict:
        """Generate review hints (paragraph indices or timestamps) for missed concepts"""
        try:
            prompt = f"""The user answered {len(wrong_answers)} questions incorrectly in a quiz about this content.
            
Summary: {summary}

Content Type: {content_type}

Wrong Answer Indices: {wrong_answers}

Original Quiz Questions: {json.dumps(original_quiz, indent=2)}

Based on the concepts they missed, generate:
1. For articles: List of paragraph indices (0-based) they should re-read
2. For videos/podcasts: List of timestamp ranges (format: "MM:SS-MM:SS") they should re-watch/re-listen

Return JSON with:
{{
  "articleHighlights": [{{"paragraphIndex": 2}}, {{"paragraphIndex": 4}}],  // For articles
  "timestamps": ["00:45-01:20", "03:10-03:40"],  // For videos/podcasts
  "concepts": ["concept1", "concept2"]  // Key concepts they missed
}}"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides targeted learning feedback. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating review hints: {e}")
            return {"articleHighlights": [], "timestamps": [], "concepts": []}
    
    def generate_retry_quiz(
        self,
        summary: str,
        transcript: Optional[str],
        content_type: str,
        wrong_concepts: List[str],
        original_quiz: List[Dict]
    ) -> List[Dict]:
        """Generate a new quiz focusing on the concepts the user missed"""
        try:
            prompt = f"""Generate 5 new multiple-choice questions focusing on the concepts the user missed.
            
Summary: {summary}

Missed Concepts: {', '.join(wrong_concepts)}

The user struggled with these concepts from the original quiz. Create NEW questions that test understanding of these specific concepts.

Return a JSON object with a "questions" array. Each question should have:
- question: string
- options: array of 4 strings
- correct_answer: integer (0-3)
- explanation: string

Example format:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": 0,
      "explanation": "..."
    }}
  ]
}}"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates educational quizzes focusing on specific concepts. Always return valid JSON with a 'questions' array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    logger.error(f"Could not parse retry quiz JSON: {content}")
                    return []
            
            if isinstance(result, dict) and "questions" in result:
                return result["questions"]
            elif isinstance(result, list):
                return result
            else:
                return list(result.values()) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Error generating retry quiz: {e}")
            raise
    
    def generate_storyboard(self, summary: str) -> List[Dict]:
        """Generate a storyboard for animated summary"""
        try:
            prompt = f"""Create a step-by-step storyboard for an animated diagram that explains the key points from this summary.
            
Summary: {summary}

Return a JSON array of storyboard steps. Each step should have:
- step: Step number (1, 2, 3, ...)
- type: Type of step ("event", "impact", "concept", "conclusion")
- title: Short title for this step
- description: Brief description of what to show in this step

Format:
[
  {{
    "step": 1,
    "type": "event",
    "title": "...",
    "description": "..."
  }},
  ...
]

Limit to 5-8 steps."""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates visual storyboards for educational content. Always return valid JSON with a 'steps' array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    logger.error(f"Could not parse storyboard JSON: {content}")
                    return []
            
            if isinstance(result, dict) and "steps" in result:
                return result["steps"]
            elif isinstance(result, list):
                return result
            else:
                return list(result.values()) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Error generating storyboard: {e}")
            return []
    
    def calculate_priority_score(self, content: str, role_tags: List[str]) -> float:
        """Calculate relevance score for a role"""
        try:
            prompt = f"""Rate the relevance of this content (0.0 to 1.0) for the following roles: {', '.join(role_tags)}

Content: {content[:1000]}

Return a JSON object with scores for each role:
{{
  "scores": {{
    "role1": 0.85,
    "role2": 0.60
  }},
  "average": 0.725
}}"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that rates content relevance. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            if "average" in result:
                return result["average"]
            elif "scores" in result and result["scores"]:
                scores = list(result["scores"].values())
                return sum(scores) / len(scores) if scores else 0.5
            return 0.5
        except Exception as e:
            logger.error(f"Error calculating priority score: {e}")
            return 0.5

# Singleton instance
ai_service = AIService()

