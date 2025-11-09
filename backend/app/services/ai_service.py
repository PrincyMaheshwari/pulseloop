import json
import logging
from typing import List, Dict, Optional
from openai import AzureOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.deepseek_key,
            azure_endpoint=settings.deepseek_endpoint,
            api_version=settings.openai_api_version,
        )
        self.model = settings.deepseek_model
    
    def generate_summary(
        self,
        content: str,
        content_type: str = "article",
        transcript_segments: Optional[List[Dict]] = None,
    ) -> str:
        """Generate a concise summary of the content"""
        try:
            trimmed_content = content[:8000] if content else ""

            if content_type in ("video", "podcast"):
                prompt = (
                    "You are summarizing an audio/video transcript that teaches industry news. "
                    "Write 2-3 short paragraphs highlighting the most important takeaways, "
                    "key people or companies mentioned, and recommended actions for the listener. "
                    "Avoid referencing timestamps directly in the summary.\n\n"
                    f"Transcript excerpt:\n{trimmed_content}\n\nSummary:"
                )
            else:
                prompt = (
                    "Generate a concise summary (2-3 paragraphs) of the following article content.\n\n"
                    f"Content:\n{trimmed_content}\n\nSummary:"
                )

            response = self.client.chat.completions.create(
                model=self.model,
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
                model=self.model,
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
    
    def generate_quiz(
        self,
        content: str,
        summary: str,
        content_type: str = "article",
        transcript_segments: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """Generate 5 multiple-choice questions based on the content"""
        try:
            trimmed_content = content[:10000] if content else ""

            if content_type in ("video", "podcast"):
                formatted_segments = self._format_segments_for_prompt(transcript_segments)
                prompt = (
                    "You are creating a quiz for learners who watched or listened to the following transcript excerpts. "
                    "Generate 5 multiple-choice questions that test understanding of the key ideas. "
                    "Questions should be specific enough that the correct answer can be found in the transcript. "
                    "If possible, note in the explanation which time range covers the answer.\n\n"
                    f"Transcript excerpts with timestamps:\n{formatted_segments}\n\n"
                    f"Transcript excerpt:\n{trimmed_content}\n\n"
                    f"Summary:\n{summary}\n\n"
                    "Return JSON with a 'questions' array. Each question must include 'question', 'options' (4 strings), "
                    "'correct_answer' (0-3), and 'explanation'."
                )
            else:
                prompt = (
                    "Generate 5 multiple-choice questions based on the article summary below. "
                    "Each question must have 4 answer options, identify the correct option by index (0-3), "
                    "and include a short explanation citing the key idea.\n\n"
                    f"Summary:\n{summary}\n\n"
                    f"Article excerpt:\n{trimmed_content}\n"
                )

            response = self.client.chat.completions.create(
                model=self.model,
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
        original_quiz: List[Dict],
        transcript_segments: Optional[List[Dict]] = None,
        candidate_segments: Optional[List[Dict]] = None,
    ) -> Dict:
        """Generate review hints (paragraph indices or timestamps) for missed concepts"""
        try:
            if content_type in ("video", "podcast") and (transcript_segments or candidate_segments):
                formatted_segments = self._format_segments_for_prompt(
                    candidate_segments or transcript_segments,
                    limit=60,
                    max_chars=220,
                )
                prompt = (
                    f"The learner missed {len(wrong_answers)} questions in a quiz about this {content_type}. "
                    "Identify the most relevant transcript segments to review. "
                    "Return JSON with a 'timestamps' array containing strings formatted as 'MM:SS-MM:SS', "
                    "an optional 'articleHighlights' array (leave empty for audio/video), "
                    "and a 'concepts' array summarising the key ideas they should revisit. "
                    "Prioritise the transcript segments provided below.\n\n"
                    f"Summary:\n{summary}\n\n"
                    f"Questions (with correct answers/explanations):\n{json.dumps(original_quiz, indent=2)}\n\n"
                    f"Transcript segments:\n{formatted_segments}\n"
                )
            else:
                prompt = (
                    f"The user answered {len(wrong_answers)} questions incorrectly in a quiz about this article.\n\n"
                    f"Summary:\n{summary}\n\n"
                    f"Questions (with correct answers/explanations):\n{json.dumps(original_quiz, indent=2)}\n\n"
                    "Return JSON with:\n"
                    "{\n"
                    '  "articleHighlights": [{"paragraphIndex": number}, ...],\n'
                    '  "timestamps": [],\n'
                    '  "concepts": ["concept1", "concept2"]\n'
                    "}\n"
                    "Paragraph indices should be zero-based."
                )

            response = self.client.chat.completions.create(
                model=self.model,
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
        original_quiz: List[Dict],
        transcript_segments: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """Generate a new quiz focusing on the concepts the user missed"""
        try:
            trimmed_transcript = transcript[:9000] if transcript else ""

            if content_type in ("video", "podcast") and transcript_segments:
                formatted_segments = self._format_segments_for_prompt(transcript_segments, limit=40, max_chars=180)
                prompt = (
                    "Generate 5 NEW multiple-choice questions to help the learner revisit the missed concepts in this "
                    f"{content_type} transcript. Focus on the listed concepts and ensure each question can be answered "
                    "using the transcript excerpts provided. Include the correct answer index and a short explanation.\n\n"
                    f"Summary:\n{summary}\n\n"
                    f"Concepts to reinforce: {', '.join(wrong_concepts) if wrong_concepts else 'Refer to transcript'}\n\n"
                    f"Transcript excerpts with timestamps:\n{formatted_segments}\n\n"
                    f"Transcript excerpt:\n{trimmed_transcript}\n"
                )
            else:
                prompt = (
                    "Generate 5 new multiple-choice questions focusing on the concepts the learner missed.\n\n"
                    f"Summary:\n{summary}\n\n"
                    f"Concepts to reinforce: {', '.join(wrong_concepts) if wrong_concepts else 'Refer to article'}\n\n"
                    f"Article excerpt:\n{trimmed_transcript}\n"
                )
            
            response = self.client.chat.completions.create(
                model=self.model,
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
                model=self.model,
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
                model=self.model,
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

    @staticmethod
    def _format_segments_for_prompt(
        segments: Optional[List[Dict]],
        limit: int = 25,
        max_chars: int = 200,
    ) -> str:
        if not segments:
            return "No timestamped transcript segments available."

        formatted_lines = []
        for segment in segments[:limit]:
            text = segment.get("text", "")
            if not text:
                continue
            trimmed_text = text.replace("\n", " ").strip()
            if len(trimmed_text) > max_chars:
                trimmed_text = trimmed_text[: max_chars - 3].rstrip() + "..."
            start_ms = segment.get("start_ms", 0)
            end_ms = segment.get("end_ms", start_ms)
            formatted_lines.append(
                f"- [{AIService._format_time_range(start_ms, end_ms)}] {trimmed_text}"
            )

        return "\n".join(formatted_lines) if formatted_lines else "No timestamped transcript segments available."

    @staticmethod
    def _format_time_range(start_ms: int, end_ms: int) -> str:
        def _fmt(ms: int) -> str:
            minutes = ms // 60000
            seconds = (ms % 60000) // 1000
            return f"{minutes:02d}:{seconds:02d}"

        return f"{_fmt(start_ms)}-{_fmt(end_ms)}"

# Singleton instance
ai_service = AIService()

