from services.gemini_service import GeminiClient
from utils.helpers import extract_json_from_text

class LearningRoadmap:
    """Generates personalized 30-60-90 day learning plans."""
    
    def __init__(self, client: GeminiClient):
        self.client = client
        
    def generate_roadmap(self, missing_skills: list, role: str, experience: str) -> dict:
        """Generates a structured roadmap based on identified skill gaps."""
        
        skills_str = ", ".join(missing_skills) if missing_skills else "General industry best practices and advanced topics"
        
        prompt = f"""
        You are an elite career coach and technical mentor. 
        A candidate aiming for a "{role}" role ({experience} level) is missing the following key skills: {skills_str}.
        
        Create a practical, actionable 30-60-90 day learning roadmap for them to master these skills and become interview-ready.
        
        Provide your response in JSON format exactly matching this structure:
        {{
            "day_30": {{
                "focus": "High-level goal for first 30 days",
                "tasks": ["Task 1", "Task 2", "Task 3"]
            }},
            "day_60": {{
                "focus": "High-level goal for next 30 days",
                "tasks": ["Task 1", "Task 2", "Task 3"]
            }},
            "day_90": {{
                "focus": "High-level goal for final 30 days",
                "tasks": ["Task 1", "Task 2", "Task 3"]
            }},
            "reasoning": "Explain why this progression is optimal for learning the missing skills."
        }}
        """
        response_text = self.client.generate_json(prompt)
        return extract_json_from_text(response_text)
