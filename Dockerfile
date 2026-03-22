FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy project files
COPY pyproject.toml .
COPY vaultmind/ vaultmind/
COPY config/ config/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create data directories
RUN mkdir -p data/pdfs data/zim data/tiles data/vault_index

# Expose ports: web UI + Kiwix
EXPOSE 8080
EXPOSE 8888

# Default: start the web server
CMD ["vaultmind", "serve", "--port", "8080"]
