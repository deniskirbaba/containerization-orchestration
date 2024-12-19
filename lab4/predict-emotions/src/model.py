import logging

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline


class EmotionModel:
    def __init__(self) -> None:
        logging.info("Initializing EmotionModel for emotion classification.")
        self.model_name: str = "SamLowe/roberta-base-go_emotions"
        logging.info(f"Model selected: {self.model_name}")

        self.local_volume_path = "/src/model"
        logging.info(f"Loading model and tokenizer from local volume: {self.local_volume_path}")

        try:
            logging.info("Starting load model")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                pretrained_model_name_or_path=self.local_volume_path
            )
            logging.info("Model successfully loaded")

            logging.info("Starting load tokenizer")
            self.tokenizer = AutoTokenizer.from_pretrained(
                pretrained_model_name_or_path=self.local_volume_path
            )
            logging.info("Tokenizer successfully loaded")

            self.classifier = pipeline(
                task="text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                top_k=None,
                device="cpu",
                framework="pt",
                trust_remote_code=True,
            )
            logging.info("Successfully initialize pipeline.")
        except Exception as e:
            logging.error(f"Failed to initialize model and tokenizer: {e}")
            raise

    def predict(self, query: str):
        logging.info(f"Predicting emotions for query: {query}")
        try:
            output = self.classifier(query)
            logging.info(f"Prediction result: {output}")
            return output
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            raise
