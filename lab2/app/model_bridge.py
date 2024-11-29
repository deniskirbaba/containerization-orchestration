import json
import os
from typing import Generator

import httpx


class ModelBridge:
    """
    Class handling the generation of stories from llama.cpp server in streaming mode.
    """

    def __init__(self) -> None:
        self.server_url = f"http://model-server:{os.getenv("LLAMA_ARG_PORT")}"  # URL of llama.cpp server

    def response_generator(
        self,
        prompt: str,
        n_predict: int = 64,
        temperature: float = 0.8,
        top_k: int = 40,
        top_p: float = 0.95,
        min_p: float = 0.05,
    ) -> Generator:
        """
        Sends a request to the llama.cpp server and retrieves the response in streaming mode.
        """
        yield prompt

        completion_url = f"{self.server_url}/completion"
        body = {
            "prompt": prompt,
            "n_predict": n_predict,
            "stream": True,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "min_p": min_p,
        }

        with httpx.stream("POST", completion_url, json=body) as response:
            for chunk in response.iter_text():
                if chunk:
                    data = json.loads(chunk.strip()[6:])
                    if not data["stop"]:
                        yield data["content"]
                    else:
                        yield data["content"] + "..."
