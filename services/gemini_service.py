import os
import google.generativeai as genai
from typing import Optional

class GeminiClient:
    """Wrapper for interacting with the Google Gemini API."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please check your .env file.")
        
        genai.configure(api_key=api_key)
        # Using gemini-flash-latest based on available models for your API key
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_content(self, prompt: str) -> str:
        """
        Sends a prompt to Gemini and returns the text response.
        """
        try:
            response = self.model.generate_content(prompt)
            # Some responses might be blocked by safety settings
            if not response.parts:
                raise Exception("Response was empty or blocked by safety filters.")
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")
            
    def generate_json(self, prompt: str) -> str:
        """
        Sends a prompt emphasizing a JSON return format.
        (Note: Gemini 1.5 Pro natively supports JSON output if specified in the prompt/config, 
        but we explicitly ask for it in the prompt for simplicity and robustness).
        """
        json_prompt = prompt + "\n\nCRITICAL INSTRUCTION: Your entire response MUST be a valid JSON object. Do not include markdown formatting like ```json or any conversational text outside the JSON block."
        
        try:
            # Optionally we could use generation_config={"response_mime_type": "application/json"}
            # but setting it explicitly in prompt often works well enough with helpers.
            response = self.model.generate_content(
                json_prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API JSON Error: {str(e)}")
