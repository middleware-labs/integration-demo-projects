FROM python:3.10-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy load generator scripts
COPY elasticsearch_load_generator.py .
COPY entrypoint.sh .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Set environment variables
ENV ES_HOST=http://elasticsearch:9200 \
    ES_USER=elastic \
    ES_PASS=changeme \
    DURATION=0 \
    THREADS=4 \
    BATCH_SIZE=100 \
    INDEX_COUNT=3 \
    INTERVAL=2

# Run the load generator
ENTRYPOINT ["/app/entrypoint.sh"]
