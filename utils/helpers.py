import json
import re

def extract_json_from_text(text: str) -> dict:
    """
    Extracts a JSON object from a string that might contain markdown formatting
    or extra text around the JSON.
    """
    try:
        # First try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in markdown
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
            
    # Try to find anything that looks like a JSON object or array
    try:
        # This regex tries to find the first '{' or '[' and the last '}' or ']'
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass

    # Return empty dict if all fails
    print("Failed to parse JSON from response.")
    return {}
    
def clean_markdown(text: str) -> str:
    """Removes common markdown artifacts if plain text is needed."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    return text
