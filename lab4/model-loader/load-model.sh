#!/bin/sh 

# Check if /model directory exists and not empty
# Otherwise download model in it
if [[ -d /loader/model && -n "$(ls -A /loader/model)" ]]; then 
  echo "Model already loaded."
else
  echo "Start to load model from HF"
  git clone https://huggingface.co/SamLowe/roberta-base-go_emotions /loader/model
fi
