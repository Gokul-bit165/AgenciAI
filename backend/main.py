from fastapi import FastAPI, UploadFile, File, HTTPException
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
    
import os
