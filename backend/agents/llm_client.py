import requests
import json
from config import settings

class LLMClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = "llama3"

    def generate(self, prompt: str, system_prompt: str = ""):
        """
        Generate text using local Llama 3 via Ollama.
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return f"Error: Could not connect to AI Brain at {self.base_url}"

    def map_csv_columns(self, columns: list):
        """
        Intelligently map broad range of CSV headers to our standardized schema.
        """
        prompt = f"""
        Map these CSV columns to the target fields: 'npi', 'first_name', 'last_name'.
        Return JSON only. keys = target fields, values = input columns.
        If no match found, use null.
        
        Input Columns: {columns}
        """
        response = self.generate(prompt, system_prompt="You are a data mapping assistant. Output valid JSON only.")
        try:
            # Simple cleanup for JSON parsing
            clean_json = response.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_json)
        except:
            return {}
