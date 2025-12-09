import requests

class ValidationAgent:
    def __init__(self):
        self.api_url = "https://npiregistry.cms.hhs.gov/api/"

    def validate_npi(self, npi_number: str, first_name: str = None, last_name: str = None):
        """
        Validates a provider against the CMS NPI Registry.
        """
        if not npi_number:
            return {"valid": False, "reason": "No NPI provided"}
            
        params = {
            "version": "2.1",
            "number": npi_number
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("result_count", 0) > 0:
                    provider = data["results"][0]
                    basic = provider.get("basic", {})
                    
                    # Basic Name Match Logic
                    api_first = basic.get("first_name", "").lower()
                    api_last = basic.get("last_name", "").lower()
                    
                    match_score = 1.0
                    if first_name and first_name.lower() not in api_first:
                        match_score -= 0.3
                    if last_name and last_name.lower() not in api_last:
                        match_score -= 0.3
                        
                    return {
                        "valid": True,
                        "npi": npi_number,
                        "primary_taxonomy": self._get_primary_taxonomy(provider),
                        "status": basic.get("status"),
                        "last_updated": basic.get("last_updated"),
                        "match_score": max(0, match_score),
                        "api_data": basic
                    }
                else:
                    return {"valid": False, "reason": "NPI not found in registry"}
            else:
                return {"valid": False, "reason": f"API Error {response.status_code}"}
        except Exception as e:
            return {"valid": False, "reason": f"Connection Error: {str(e)}"}

    def validate_website(self, url: str, expected_phone: str = None):
        """
        Scrapes the provider's website to verify contact info.
        """
        if not url:
            return {"valid": False, "reason": "No URL provided"}
            
        try:
            # In a real production agent, we would use Selenium or Playwright here.
            # For this prototype, we'll use requests + BeautifulSoup to check for the phone number.
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                text = response.text
                found_phone = False
                if expected_phone and expected_phone.replace('-', '') in text.replace('-', ''):
                     found_phone = True
                     
                return {
                    "valid": True,
                    "url_reachable": True,
                    "phone_on_page": found_phone
                }
            else:
                 return {"valid": False, "reason": f"Website unreachable (Status {response.status_code})"}
        except Exception as e:
            return {"valid": False, "reason": f"Scraping Error: {str(e)}"}

    def _get_primary_taxonomy(self, provider_data):
        taxonomies = provider_data.get("taxonomies", [])
        for tax in taxonomies:
            if tax.get("primary") == True:
                return tax.get("desc")
        return "Unknown"
