FROM python:3.12.7-slim

ENV \
    # Disable buffers in stdout and stderr
    PYTHONUNBUFFERED=1 \
    # Prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # PIP optimization
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Set up folder for Transformers caching
    TRANSFORMERS_CACHE=/app/model_cache \
    # Set up the maximum length of generation parameter
    GEN_MAX_LEN=128

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker's layer caching
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application files
COPY storyteller storyteller

# Load model weights to the predefined dir
RUN python storyteller/preload.py

# Port on which app interface will be provided
EXPOSE 8501

# Define a volume for storing persistent chat history
VOLUME /app/data

# Run the application
CMD ["streamlit", "run", "storyteller/app.py"]
