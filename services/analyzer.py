import json
from services.gemini_service import GeminiClient
from utils.helpers import extract_json_from_text

class ResumeAnalyzer:
    """Handles all AI analysis tasks related to the candidate's resume and role."""
    
    def __init__(self, client: GeminiClient):
        self.client = client
        
    def analyze_resume(self, resume_text: str, role: str, experience: str) -> dict:
        """Generates a comprehensive resume analysis."""
        prompt = f"""
        You are an expert technical recruiter and AI career coach.
        Analyze the following resume for the target role of "{role}" at the "{experience}" level.
        
        Provide your response in JSON format exactly matching this structure:
        {{
            "summary": "A 3-4 sentence professional summary of the candidate's fit.",
            "strengths": ["Strength 1", "Strength 2", "Strength 3"],
            "weaknesses": ["Weakness 1", "Weakness 2"],
            "missing_skills": ["Skill 1", "Skill 2", "Skill 3"],
            "recruiter_feedback": "A direct, constructive paragraph of feedback from a recruiter's perspective.",
            "reasoning": "Explain why these specific strengths, weaknesses, and gaps were identified."
        }}
        
        Resume text:
        {resume_text}
        """
        response_text = self.client.generate_json(prompt)
        return extract_json_from_text(response_text)
        
    def generate_interview_questions(self, resume_text: str, role: str, experience: str) -> dict:
        """Generates tailored interview questions."""
        prompt = f"""
        You are a hiring manager interviewing a candidate for a "{role}" role at the "{experience}" level.
        Based on their resume, generate tailored interview questions. Provide exactly 10 questions for each category.
        
        Provide your response in JSON format exactly matching this structure:
        {{
            "hr_questions": ["Q1", ..., "Q10"],
            "technical_questions": ["Q1", ..., "Q10"],
            "behavioral_questions": ["Q1", ..., "Q10"],
            "project_based_questions": ["Q1", ..., "Q10"],
            "reasoning": "Explain why these specific questions are relevant for this candidate."
        }}
        
        Resume text:
        {resume_text}
        """
        response_text = self.client.generate_json(prompt)
        return extract_json_from_text(response_text)
        
    def generate_readiness_score(self, resume_text: str, role: str, experience: str) -> dict:
        """Calculates a readiness score and provides improvement suggestions."""
        prompt = f"""
        You are a highly analytical AI scoring system. 
        Evaluate this resume for the role of "{role}" ({experience} level).
        Score the candidate from 0 to 100 on four categories, and provide an overall score.
        Also, provide actionable suggestions for improvement.
        
        Provide your response in JSON format exactly matching this structure:
        {{
            "scores": {{
                "overall": 85,
                "technical_skills": 80,
                "project_quality": 90,
                "resume_quality": 75,
                "industry_readiness": 85
            }},
            "suggestions": {{
                "resume_improvements": ["Tip 1", "Tip 2"],
                "project_suggestions": ["Project Idea 1", "Project Idea 2"],
                "certifications": ["Cert 1", "Cert 2"],
                "portfolio": ["Portfolio Tip 1"]
            }},
            "reasoning": "Explain exactly how the scores were calculated and why these improvements are suggested."
        }}
        
        Resume text:
        {resume_text}
        """
        response_text = self.client.generate_json(prompt)
        return extract_json_from_text(response_text)
