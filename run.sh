#!/bin/bash
set -e

# Configuration
# The direct download link for your specific GGUF file
MODEL_URL="https://huggingface.co/CWClabs/CWC-Mistral-Nemo-12B-V2-q4_k_m/resolve/main/CWC-Mistral-Nemo-12B-v2-GGUF-q4_k_m-health-nutrition-natural-medicine.gguf?download=true"
MODEL_PATH="/models/model.gguf"

# 1. Download Check (Only happens on first deploy)
if [ ! -f "$MODEL_PATH" ]; then
    echo "🚀 Model not found in volume. Downloading (this may take a few minutes)..."
    curl -L "$MODEL_URL" -o "$MODEL_PATH"
    echo "✅ Download complete."
else
    echo "✅ Model found in volume. Skipping download."
fi

# 2. Start the Llama Server (OpenAI Compatible)
echo "🧠 Starting Sovereign Vault..."
# --ctx-size 8192: 8k Context Window (Standard for Nemo)
# --port 8080: The port Fly.io listens on
exec /app/llama-server \
    --model "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port 8080 \
    --ctx-size 8192 \
    --n-gpu-layers 0
