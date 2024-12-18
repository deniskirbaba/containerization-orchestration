FROM python:3.12.8-slim

ENV \
    # Disable buffers in stdout and stderr
    PYTHONUNBUFFERED=1 \
    # Prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # PIP optimization
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /src

# Install system dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker's layer caching
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application files
COPY . .

# Port on which app interface will be provided
EXPOSE ${MODEL_PORT}

# Define volume with model weight (loaded with init container)
VOLUME /src/model

# Run the application
CMD ["sh", "-c", "fastapi run --port ${MODEL_PORT} api.py"]