FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create pdf directory if it doesn't exist
RUN mkdir -p pdf

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose the application port
EXPOSE 8000

# Start the FastAPI application with uvicorn
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT}