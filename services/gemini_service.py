import os
import time
from google import genai
from google.genai import types

class GeminiClient:
    """Wrapper for interacting with the Google Gemini API using the new google-genai SDK."""
    
    # Delay between consecutive API calls to avoid rate limits (seconds)
    CALL_SPACING = 2
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please check your .env file.")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.6-flash"
        self._last_call_time = 0

    def _wait_for_spacing(self):
        """Ensures minimum spacing between consecutive API calls."""
        elapsed = time.time() - self._last_call_time
        if elapsed < self.CALL_SPACING:
            time.sleep(self.CALL_SPACING - elapsed)
        self._last_call_time = time.time()

    def _retry_call(self, func, max_retries=4):
        """
        Executes `func` with exponential backoff retry on transient errors
        (429 rate limit, 503 unavailable, 500 server error).
        """
        for attempt in range(max_retries):
            try:
                self._wait_for_spacing()
                return func()
            except Exception as e:
                error_str = str(e).lower()
                is_retryable = any(code in error_str for code in ["429", "503", "500", "quota", "unavailable", "rate", "overloaded", "high demand"])
                
                if is_retryable and attempt < max_retries - 1:
                    # Exponential backoff: 5s, 15s, 45s
                    wait_time = 5 * (3 ** attempt)
                    print(f"[GeminiClient] Retryable error (attempt {attempt+1}/{max_retries}), waiting {wait_time}s: {str(e)[:120]}")
                    time.sleep(wait_time)
                    self._last_call_time = time.time()
                    continue
                
                raise  # Non-retryable error or final attempt exhausted

    def generate_content(self, prompt: str) -> str:
        """
        Sends a prompt to Gemini and returns the text response.
        """
        def _call():
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            if not response.text:
                raise Exception("Response was empty or blocked by safety filters.")
            return response.text
        
        try:
            return self._retry_call(_call)
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")
            
    def generate_json(self, prompt: str) -> str:
        """
        Sends a prompt and returns a JSON response using structured output.
        """
        json_prompt = prompt + "\n\nCRITICAL INSTRUCTION: Your entire response MUST be a valid JSON object. Do not include markdown formatting like ```json or any conversational text outside the JSON block."
        
        def _call():
            response = self.client.models.generate_content(
                model=self.model,
                contents=json_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            if not response.text:
                raise Exception("Response was empty or blocked by safety filters.")
            return response.text
        
        try:
            return self._retry_call(_call)
        except Exception as e:
            raise Exception(f"Gemini API JSON Error: {str(e)}")
