import os

from transformers import AutoModelForCausalLM, AutoTokenizer


class StoryModel:
    def __init__(self) -> None:
        self.model_name: str = "nickypro/tinyllama-110M"
        self.config = {"max_length": int(os.getenv("GEN_MAX_LEN"))}

    def load(self, pretrained_model_name_or_path: str) -> None:
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path)
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path)

    def generate(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")
        logits = self.model.generate(**inputs, **self.config)
        return (
            self.tokenizer.decode(
                logits[0], skip_special_tokens=True, clean_up_tokenization_spaces=True
            )
            + "..."
        )
