import logging

from fastapi import FastAPI, HTTPException
from model import EmotionModel
from transformers import Pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Starting FastAPI application.")
app = FastAPI()

logging.info("Initializing EmotionModel for emotion prediction.")
emotion_model = EmotionModel()


@app.post("/predict")
async def predict(query: str):
    logging.info(f"Received prediction request for query: {query}")
    try:
        preds = emotion_model.predict(query)
        logging.info(f"Prediction successful. Result: {preds}")
        return preds
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return {"error": "An error occurred during prediction."}


@app.get("/health")
async def health():
    try:
        if not isinstance(emotion_model.classifier, Pipeline):
            logging.warning("Health check failed. Classifier is not a Pipeline instance.")
            raise HTTPException(status_code=500, detail="Service unhealthy")
        
        logging.info("Health check passed.")
        return {"status": "healthy"}
    except Exception as e:
        logging.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")
