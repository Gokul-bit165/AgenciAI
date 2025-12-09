from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from celery_worker import process_upload_task
import pandas as pd
import io
import shutil
import uuid

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AgenciAI Backend Running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts CSV or PDF/Image, saves it, and triggers the Agent Pipeline.
    """
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        file_id = str(uuid.uuid4())
        
        input_type = "csv"
        
        # Save to disk
        os.makedirs("/app/uploads", exist_ok=True)
        save_path = f"/app/uploads/{file_id}.{file_ext}"
        
        with open(save_path, "wb") as f:
            f.write(content)
            
        if file_ext in ['pdf', 'png', 'jpg', 'jpeg']:
            input_type = "pdf"
        elif file_ext == 'csv':
             # Validate CSV simple read
             pd.read_csv(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
            
        # Trigger Celery Task
        task = process_upload_task.delay(save_path, input_type)
        
        return {
            "message": "Upload successful", 
            "file_id": file_id,
            "task_id": task.id,
            "type": input_type
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/task/{task_id}")
def get_task_status(task_id: str):
    from celery.result import AsyncResult
    from celery_worker import celery_app
    
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result
    }

@app.get("/download/{task_id}")
def download_results(task_id: str):
    """
    Generates a CSV from the validation results.
    """
    from celery.result import AsyncResult
    from celery_worker import celery_app
    from fastapi.responses import StreamingResponse
    import csv
    
    result = AsyncResult(task_id, app=celery_app)
    if result.status != 'SUCCESS':
         raise HTTPException(status_code=400, detail="Task not completed")
         
    data = result.result.get('data', [])
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
        
    # Flatten data for CSV
    flat_data = []
    for item in data:
        record = item.get('record', {})
        api_data = item.get('api_data', {})
        enriched = item.get('enriched', {})
        
        row = {
            "Original NPI": record.get('npi'),
            "Original Name": f"{record.get('first_name')} {record.get('last_name')}",
            "Validation Status": item.get('validation_status'),
            "Confidence Score": item.get('confidence_score'),
            "Issues": ", ".join(item.get('issues', [])),
            "Registered Name": f"{api_data.get('first_name', '')} {api_data.get('last_name', '')}",
            "Taxonomy": item.get('api_data', {}).get('primary_taxonomy'),
            "Enriched Specialties": ", ".join(enriched.get('specialties', [])) if enriched else ""
        }
        flat_data.append(row)
        
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=flat_data[0].keys())
    writer.writeheader()
    writer.writerows(flat_data)
    stream.seek(0)
    
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=validated_providers.csv"
    return response

class ChatRequest(BaseModel):
    task_id: str
    message: str

@app.post("/chat")
def chat_with_data(req: ChatRequest):
    """
    Simple RAG: Fetches task context and answers user question.
    """
    from celery.result import AsyncResult
    from celery_worker import celery_app
    from agents.llm_client import LLMClient
    
    result = AsyncResult(req.task_id, app=celery_app)
    if result.status != 'SUCCESS':
         return {"response": "I can only answer questions once the data analysis is complete."}
         
    data = result.result.get('data', [])
    report = result.result.get('report', {})
    
    # Create context (summarized to fit context window)
    context = f"""
    Dataset Summary:
    Total Records: {len(data)}
    Valid Providers: {report.get('valid_providers')}
    Flagged: {report.get('flagged_providers')}
    Accuracy: {report.get('accuracy_rate')}
    
    Sample Issues Found:
    {[d['issues'] for d in data if d['issues']][:5]}
    """
    
    llm = LLMClient()
    prompt = f"""
    Context: {context}
    
    User Question: {req.message}
    
    Answer as a helpful data assistant.
    """
    
    response = llm.generate(prompt, system_prompt="You are AgenciAI, a provider data specialist.")
    return {"response": response}
    
import os
