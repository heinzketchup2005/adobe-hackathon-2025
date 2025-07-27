# Dockerfile
FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Create input/output directories
RUN mkdir -p /app/input /app/output

# Copy source code (only what's needed)
COPY src/round1a ./src/round1a
COPY src/utils ./src/utils
COPY main.py ./

# Set Python path and optimize Python
ENV PYTHONPATH=/app
ENV PYTHONOPTIMIZE=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "-O", "main.py"]