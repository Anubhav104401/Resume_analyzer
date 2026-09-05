import os
import time
from google import genai
from google.genai import types

class GeminiClient:
    """Wrapper for interacting with the Google Gemini API using the new google-genai SDK.
    
    Uses a model fallback chain to handle 503 'high demand' errors by automatically
    switching to the next available model instead of waiting on an overloaded one.
    """
    
    # Ordered by reliability and speed. If one fails with 503, try the next.
    MODEL_CHAIN = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]
    
    # Minimum delay between consecutive API calls (seconds)
    CALL_SPACING = 3
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please check your .env file.")
        
        self.client = genai.Client(api_key=api_key)
        self._last_call_time = 0

    def _wait_for_spacing(self):
        """Ensures minimum spacing between consecutive API calls."""
        elapsed = time.time() - self._last_call_time
        if elapsed < self.CALL_SPACING:
            time.sleep(self.CALL_SPACING - elapsed)

    def _call_with_fallback(self, make_request, max_retries_per_model=2):
        """
        Tries each model in the fallback chain. For each model, retries up to
        max_retries_per_model times with exponential backoff on transient errors.
        On 503/429, moves to the next model in the chain after retries are exhausted.
        """
        last_error = None
        
        for model_name in self.MODEL_CHAIN:
            for attempt in range(max_retries_per_model):
                try:
                    self._wait_for_spacing()
                    self._last_call_time = time.time()
                    return make_request(model_name)
                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    is_transient = any(
                        keyword in error_str
                        for keyword in ["503", "429", "500", "unavailable", "quota", "high demand", "overloaded", "capacity"]
                    )
                    
                    if is_transient:
                        if attempt < max_retries_per_model - 1:
                            wait_time = 5 * (2 ** attempt)  # 5s, 10s
                            print(f"[GeminiClient] {model_name} attempt {attempt+1} failed (transient), retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # Exhausted retries for this model, try next model
                            print(f"[GeminiClient] {model_name} exhausted retries, falling back to next model...")
                            break
                    else:
                        # Non-transient error (e.g. 400 bad request) — don't retry
                        raise
        
        # All models and retries exhausted
        raise Exception(f"All models in fallback chain failed. Last error: {str(last_error)}")

    def generate_content(self, prompt: str) -> str:
        """Sends a prompt to Gemini and returns the text response."""
        def make_request(model_name):
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if not response.text:
                raise Exception("Response was empty or blocked by safety filters.")
            return response.text
        
        try:
            return self._call_with_fallback(make_request)
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")
            
    def generate_json(self, prompt: str) -> str:
        """Sends a prompt and returns a JSON response using structured output."""
        json_prompt = prompt + "\n\nCRITICAL INSTRUCTION: Your entire response MUST be a valid JSON object. Do not include markdown formatting like ```json or any conversational text outside the JSON block."
        
        def make_request(model_name):
            response = self.client.models.generate_content(
                model=model_name,
                contents=json_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            if not response.text:
                raise Exception("Response was empty or blocked by safety filters.")
            return response.text
        
        try:
            return self._call_with_fallback(make_request)
        except Exception as e:
            raise Exception(f"Gemini API JSON Error: {str(e)}")
