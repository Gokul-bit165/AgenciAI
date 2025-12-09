from celery import Celery
from config import settings
from agents.llm_client import LLMClient
from agents.validation_agent import ValidationAgent
from agents.ocr_agent import OCRAgent
from agents.qa_enrichment import EnrichmentAgent, QAAgent
from agents.directory_agent import DirectoryManagementAgent
import pandas as pd
import json
import os

celery_app = Celery(
    "agenciai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(bind=True)
def process_upload_task(self, file_path: str, input_type: str = "csv"):
    """
    Orchestrates the Multi-Agent Pipeline.
    input_type: "csv" or "pdf"
    """
    self.update_state(state='STARTED', meta={'step': 'Initializing Agents'})
    
    llm = LLMClient()
    validator = ValidationAgent()
    enricher = EnrichmentAgent()
    qa = QAAgent()
    directory_agent = DirectoryManagementAgent()
    
    records = []
    
    # --- STEP 1: Ingestion & OCR ---
    if input_type == "pdf":
        self.update_state(state='PROGRESS', meta={'step': 'OCR Processing (Scanning PDF)...'})
        ocr = OCRAgent()
        # For Hackathon, assuming single page or converting first page to image
        # In Docker we use pdf2image or just assume the 'pdf' is actually an image for simplicity if pdf2image missing
        # BUT we installed system deps, so let's try direct OCR on path if Paddle supports it, or assume it's an image
        # PaddleOCR supports PDF paths directly.
        
        raw_text = ocr.extract_text(file_path)
        
        self.update_state(state='PROGRESS', meta={'step': 'Extracting Data from OCR Text...'})
        # Use LLM to parse unstructured text into JSON list
        prompt = f"""
        Extract provider information from this OCR text into a JSON list.
        Fields: npi (string), first_name, last_name, website (optional).
        Text:
        {raw_text[:3000]}
        """
        response = llm.generate(prompt, system_prompt="Output JSON list of objects only.")
        try:
            clean_json = response.strip().replace("```json", "").replace("```", "")
            records = json.loads(clean_json)
        except:
             records = [] # Fail gracefully
             
    else: # CSV
        self.update_state(state='PROGRESS', meta={'step': 'Mapping CSV Columns...'})
        df = pd.read_csv(file_path)
        col_map = llm.map_csv_columns(list(df.columns))
        
        # Sanitize col_map: ensure values are strings
        sanitized_map = {}
        for k, v in col_map.items():
            if isinstance(v, str):
                sanitized_map[k] = v
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                sanitized_map[k] = v[0] # Take first if list
            else:
                 sanitized_map[k] = None

        col_map = sanitized_map
        
        raw_records = df.head(50).to_dict(orient='records')
        for r in raw_records:
            # Handle NPI or Registration Number
            npi_val = str(r.get(col_map.get('npi')) or '')
            
            # If NPI is missing/mapped to None, try finding 'registration_number' or similar in raw columns if LLM failed
            if not npi_val or npi_val == 'nan' or npi_val == 'None':
                 # Heuristic backup: look for 'registration' in keys
                 for key in r.keys():
                     if 'registration' in key.lower() or 'reg_no' in key.lower():
                         npi_val = str(r[key])
                         break

            # Handle Name Parsing (Full Name -> First/Last)
            first_name = r.get(col_map.get('first_name'))
            last_name = r.get(col_map.get('last_name'))
            
            if not first_name and not last_name:
                 # Check for 'full_name' or 'name' column
                 full_name_val = ""
                 for key in r.keys():
                     if 'full_name' in key.lower() or 'provider_name' in key.lower():
                         full_name_val = str(r[key])
                         break
                 
                 if full_name_val:
                     parts = full_name_val.replace("Dr.", "").strip().split(' ')
                     if len(parts) > 0:
                         first_name = parts[0]
                         last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

            records.append({
                "npi": npi_val,
                "first_name": first_name,
                "last_name": last_name,
                "website": r.get(col_map.get('website'))
            })

    results = []
    
    # --- STEP 2: Validation Loop ---
    for idx, record in enumerate(records):
        npi = str(record.get('npi', '')).replace('.0', '') # Clean float strings
        fname = record.get('first_name')
        lname = record.get('last_name')
        website = record.get('website')
        
        self.update_state(state='PROGRESS', meta={
            'step': 'Validating Provider', 
            'current': idx + 1, 
            'total': len(records),
            'provider': f"{fname} {lname}"
        })
        
        # Agent 1: Validation (Real API + Scraping)
        val_res = validator.validate_npi(npi, fname, lname)
        
        website_res = {}
        if website:
             website_res = validator.validate_website(website)
        
        # Agent 2: Enrichment (LLM Hallucination/Search)
        enrich_res = {}
        if val_res['valid']:
            enrich_res = enricher.enrich_provider(val_res['api_data'])
            
        # Agent 3: QA Scoring
        score, issues = qa.score_provider(val_res)
        if not website_res.get('valid', True) and website: # if website check failed
             score -= 0.1
             issues.append(f"Website unreachable: {website}")
        
        results.append({
            "record": record,
            "validation_status": "Valid" if score > 0.8 else "Needs Review",
            "confidence_score": score,
            "issues": issues,
            "api_data": val_res,
            "website_validation": website_res,
            "enriched": enrich_res
        })
        
    # --- STEP 3: Directory Management (Reporting) ---
    self.update_state(state='PROGRESS', meta={'step': 'Generating Directory Report...'})
    metrics = {"accuracy": 0.95} # Mock metric or calculate real one
    final_report = directory_agent.generate_report(results, metrics)
        
    return {"processed": len(records), "data": results, "report": final_report}
