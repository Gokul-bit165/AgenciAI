FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for PaddleOCR & PDF Processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
