import json
import logging
import os

import requests


class Emotions:
    def __init__(self) -> None:
        logging.info("Initializing Emotions object")

        self.model_port = os.getenv("MODEL_PORT")
        if self.model_port is None:
            logging.fatal("Can't find MODEL_PORT env var")
            raise EnvironmentError

        self.model_url = f"http://predict-emotions-service:{self.model_port}"
        logging.info(f"Url for getting predictions from model server is: {self.model_url}")

        logging.info("Setting up the emotion output parameters...")
        try:
            self.n_emotions = int(os.getenv("MAX_EMOTIONS"))
            logging.info(f"Successfully set MAX_EMOTION={self.n_emotions}")
        except Exception:
            logging.warning("MAX_EMOTION set to 5 by default, because it wasn't setted or setted not preperly")
            self.n_emotions = 5

        try:
            self.lower_bound = int(os.getenv("EMOTION_THRESHOLD"))
            logging.info(f"Successfully set EMOTION_THRESHOLD={self.lower_bound}")
        except Exception:
            logging.warning("EMOTION_THRESHOLD set to 0 by default, because it wasn't setted or setted not preperly")
            self.lower_bound = 0

        logging.info(
            f"Parameters for visualizing emotions is: n_emotions={self.n_emotions}, lower_bound={self.lower_bound}"
        )

    def predict(self, query: str):
        logging.info(f"Predicting emotions for query: {query}")
        try:
            response = requests.post(self.model_url + "/predict", params={"query": query})
            response.raise_for_status()
            logging.info(f"Prediction response status: {response.status_code}")
            return json.loads(response.content)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during prediction request: {e}")
            raise

    def prettify(self, predictions):
        logging.info("Prettifying predictions")
        try:
            result = list()
            for pred in predictions[0][: self.n_emotions]:
                score = round(pred["score"] * 100)
                if score > self.lower_bound:
                    result.append(pred["label"].title() + ": " + str(score) + "%")
            prettified_result = "\n".join(result)
            logging.info(f"Prettified predictions: {prettified_result}")
            return prettified_result
        except (IndexError, KeyError, TypeError) as e:
            logging.error(f"Error while prettifying predictions: {e}")
            raise

    def get_emotions(self, query: str):
        logging.info(f"Getting emotions for query: {query}")
        try:
            predictions = self.predict(query)
            result = self.prettify(predictions)
            logging.info(f"Final emotion result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error in get_emotions: {e}")
            raise
