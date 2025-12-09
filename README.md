# Healthcare Provider Validation System

## Prerequisites

- Python 3.8+
- Node.js & npm
- Redis (for background tasks)

## Setup & Running

### 1. Backend

The backend is a FastAPI application.

**Install Dependencies:**

```bash
pip install -r requirements.txt
# Note: If 'paddleocr' fails to install due to long paths, you can ignore it. 
# The app will run without OCR features.
```

**Start the API Server:**

```bash
# Run from the root directory using python -m to avoid PATH issues
python -m uvicorn backend.main:app --reload
```
The API will be available at http://localhost:8000.
API Documentation: http://localhost:8000/docs

**Start the Celery Worker:**

A Celery worker is needed for background tasks. Ensure Redis is running.

```bash
# Run from the root directory
python -m celery -A backend.celery_worker.celery_app worker --loglevel=info --pool=solo
```
*Note: `--pool=solo` is required on Windows.*

### 2. Frontend

The frontend is a React application.

**Install Dependencies:**

```bash
cd frontend
npm install
```

**Start the Development Server:**

```bash
npm run dev
```
The frontend will be available at http://localhost:5173 (usually).

## Project Structure

- `backend/`: FastAPI application code.
- `frontend/`: React frontend code.
- `scripts/`: Utility scripts (e.g., for generating data).

## Troubleshooting

### "ModuleNotFoundError" when running scripts
If you see `ModuleNotFoundError: No module named 'backend'`, always run scripts as modules from the root directory:
```bash
python -m scripts.generate_data
python -m scripts.generate_pdfs
```

### "uvicorn" or "celery" not recognized
This happens if Python scripts folder isn't in your system PATH. Use `python -m` to run them:
```bash
python -m uvicorn ...
python -m celery ...
```

### PaddleOCR / Long Path Error
If `pip install` fails on `paddleocr` or related packages with a "path too long" error, you can safely ignore it if you don't need OCR capabilities. The application will detect the missing library and disable OCR features automatically.
