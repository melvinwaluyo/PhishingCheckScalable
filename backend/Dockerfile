# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Ensure .env.development is loaded or use Docker Compose env vars
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]