import logging
import os

import gradio as gr
from emotions import Emotions

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Starting the Emotion Prediction interface.")

em = Emotions()

logging.info("Setting up Gradio interface.")
with gr.Blocks() as demo:
    gr.Markdown("Emotion prediction")
    with gr.Row(equal_height=True):
        textbox = gr.Textbox(lines=1, show_label=False, placeholder="Type something here...")
        button = gr.Button("Predict", variant="primary")
    prediction = gr.Textbox(show_label=False, placeholder="Predicted emotions...")

    def handle_prediction(query):
        logging.info(f"Received input for prediction: {query}")
        try:
            result = em.get_emotions(query)
            return result
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            return "An error occurred during prediction."

    button.click(handle_prediction, inputs=textbox, outputs=prediction)

interface_port = os.getenv("INTERFACE_PORT")
if interface_port is None:
    logging.fatal("INTERFACE_PORT environment variable not set.")
    raise EnvironmentError

logging.info(f"Launching Gradio interface on port: {interface_port}.")
demo.launch(server_port=int(interface_port))
