#!/bin/sh 

# Check if /model directory exists and not empty
# Otherwise download model in it using git clone
if [[ -d /loader/model && -n "$(ls -A /loader/model)" ]]; then 
  echo "Model and tokenizer already loaded."
else
  echo "Start to load model and tokenizer from HF"
  git clone https://huggingface.co/deniskirbaba/tinyllama-110M-F16-GGUF /loader/model
fi
