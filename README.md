# AgenciAI - Healthcare Provider Validation System

AgenciAI is an intelligent agentic system designed to validate and enrich healthcare provider data. It leverages local LLMs (Llama 3 via Ollama) and OCR capabilities to automate the verification of provider credentials from CSV files and PDF documents.

## 🏗️ Architecture

The system follows a modern microservices-inspired architecture, containerized with Docker.

```mermaid
graph TD
    subgraph Frontend [Frontend Layer]
        UI[React + Vite Admin Dashboard]
    end

    subgraph Backend [Backend Layer]
        API[FastAPI Server]
        Worker[Celery Worker]
    end

    subgraph Infrastructure [Data & Messaging]
        Redis[(Redis Message Broker)]
        DB[(SQLite Database)]
        FS[File System /uploads]
    end

    subgraph AI_Services [AI Services]
        Ollama[Ollama (Llama 3)]
        OCR[PaddleOCR]
    end

    UI -->|Uploads File| API
    UI -->|Polls Status| API
    UI -->|Chat Query| API
    API -->|Enqueues Task| Redis
    Redis -->|Consumes Task| Worker
    Worker -->|Reads/Writes| FS
    Worker -->|Validates| DB
    Worker -->|Inference| Ollama
    Worker -->|Extracts Text| OCR
```

### Data Flow
1.  **Ingestion**: Users upload CSV files or PDFs via the React Dashboard.
2.  **Queueing**: The FastAPI backend handles the upload and pushes a validation task to the Redis queue.
3.  **Processing**: The Celery worker picks up the task asynchronously.
    *   **CSV**: Parsed using Pandas; mapped to a standardized schema.
    *   **PDF**: Processed with PaddleOCR to extract text.
4.  **Validation & Enrichment**:
    *   Data is validated against business rules (e.g., NPI format).
    *   Missing fields are enriched using the LLM (Llama 3) to infer details from context or unstructured text.
5.  **Interactive Review**: Users can chat with their data using the RAG-enabled chat interface to ask questions about the validation results.

## 🛠️ Tech Stack

### Frontend
*   **Framework**: React 18 (Vite)
*   **Styling**: TailwindCSS, clsx, tailwind-merge
*   **Animations**: Framer Motion
*   **HTTP Client**: Axios
*   **Icons**: Lucide React

### Backend
*   **API Framework**: FastAPI
*   **Async Task Queue**: Celery
*   **Broker**: Redis
*   **Data Processing**: Pandas, NumPy
*   **Database**: SQLite (via SQLAlchemy)

### AI & Agents
*   **LLM Runtime**: Ollama (running Llama 3)
*   **OCR**: PaddleOCR (PaddlePaddle)
*   **Agent Logic**: Custom Python agents (ValidationAgent, DirectoryAgent)

### DevOps & Infrastructure
*   **Containerization**: Docker, Docker Compose
*   **Environment**: Python 3.9+, Node.js 18+

## 🚀 Setup & Installation

### Option 1: Docker (Recommended)

Ensure you have **Docker Desktop** installed and **Ollama** running on your host machine.

1.  **Clone the repository** (if not already done).
2.  **Start the services**:
    ```bash
    docker-compose up --build
    ```
3.  **Access the Application**:
    *   Frontend: `http://localhost:5173`
    *   Backend API Docs: `http://localhost:8005/docs` (mapped port in docker-compose)

> **Note on Ollama**: The `docker-compose.yml` is configured to connect to `host.docker.internal:11434`. Ensure your local Ollama is listening and has the model pulled (`ollama pull llama3`).

### Option 2: Local Development

If you prefer running services individually without Docker:

**1. Infrastructure**
*   Start Redis locally (default port 6379).
*   Ensure Ollama is running (`ollama serve`).

**2. Backend**
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start API Server
python -m uvicorn backend.main:app --reload --port 8000

# Start Celery Worker (in a separate terminal)
# Windows:
python -m celery -A backend.celery_worker.celery_app worker --loglevel=info --pool=solo
# Unix/Mac:
python -m celery -A backend.celery_worker.celery_app worker --loglevel=info
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev
```
## 📂 Project Structure

```
├── backend/            # FastAPI application & Celery workers
│   ├── agents/         # AI Agent logic (Validation, Directory)
│   ├── main.py         # API entry point
│   ├── celery_worker.py# Background task configuration
│   └── requirements.txt
├── frontend/           # React application
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   └── App.jsx     # Main dashboard layout
├── docker-compose.yml  # Container orchestration
└── README.md           # Project documentation
```
