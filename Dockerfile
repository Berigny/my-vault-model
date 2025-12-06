# Use the official lightweight server image from llama.cpp
FROM ghcr.io/ggml-org/llama.cpp:server

# Install curl (needed to download the model to the volume)
USER root
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a directory for the persistent volume
RUN mkdir -p /models

# Copy our startup script
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# When the app starts, run our script
ENTRYPOINT ["/app/run.sh"]
