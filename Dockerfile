FROM ghcr.io/ggml-org/llama.cpp:server

# Install curl to download the model
USER root
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create the folder for the volume
RUN mkdir -p /models

# Copy the startup script
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Run the script on boot
ENTRYPOINT ["/app/run.sh"]
