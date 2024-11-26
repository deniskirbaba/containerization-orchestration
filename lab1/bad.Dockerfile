FROM python:3.12

ENV \
    # Set up folder for Transformers caching
    TRANSFORMERS_CACHE=/app/model_cache \
    # Set up the maximum length of generation parameter
    GEN_MAX_LEN=128

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# Load model weights to the predefined dir
RUN python storyteller/preload.py

# Run the application
CMD ["streamlit", "run", "storyteller/app.py"]
