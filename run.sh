#!/bin/bash
set -e

# Config
MODEL_URL="https://huggingface.co/CWClabs/CWC-Mistral-Nemo-12B-V2-q4_k_m/resolve/main/CWC-Mistral-Nemo-12B-v2-GGUF-q4_k_m.gguf"
MODEL_PATH="/models/model.gguf"

# Download Check
if [ ! -f "$MODEL_PATH" ]; then
    echo "🚀 Model not found in volume. Downloading (this happens once)..."
    curl -L "$MODEL_URL" -o "$MODEL_PATH"
    echo "✅ Download complete."
else
    echo "✅ Model found in volume. Skipping download."
fi

# Start Server
echo "🧠 Starting Llama Server..."
exec /app/llama-server \
    --model "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port 8080 \
    --ctx-size 8192 \
    --n-gpu-layers 0
