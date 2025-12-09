from agents.llm_client import LLMClient

class EnrichmentAgent:
    def __init__(self):
        self.llm = LLMClient()
        
    def enrich_provider(self, provider_data):
        """
        Simulates gathering extra data via LLM (web search simulation).
        """
        # In a real scenario, this would use SerpAPI. 
        # For Hackathon, we use LLM "knowledge" to hallucinate plausible details or extract from unstructured text.
        prompt = f"""
        Given this provider: {provider_data}
        Suggest 3 likely medical specialties and 1 board certification based on their taxonomy.
        Return as JSON: {{ "specialties": [], "certification": "" }}
        """
        response = self.llm.generate(prompt, system_prompt="You are a medical data assistant. Output JSON only.")
        return response

class QAAgent:
    def __init__(self):
        pass
        
    def score_provider(self, validation_result):
        """
        Calculates a confidence score.
        """
        if not validation_result.get("valid"):
            return 0.0, ["Invalid NPI or API Error"]
            
        score = 1.0
        issues = []
        
        # Check Match Score (Name match)
        match_score = validation_result.get("match_score", 1.0)
        if match_score < 1.0:
            score -= (1.0 - match_score)
            issues.append("Name mismatch with Registry")
            
        # Check Active Status
        if validation_result.get("status") != "A": # A = Active
            score -= 0.5
            issues.append(f"Provider Inactive (Status: {validation_result.get('status')})")
            
        return max(0.0, round(score, 2)), issues
