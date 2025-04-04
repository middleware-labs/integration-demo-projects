#!/bin/bash

echo "Starting Elasticsearch load generator"

# Wait for Elasticsearch to become available
max_retries=30
retry_interval=5
retry_count=0

echo "Waiting for Elasticsearch to be available at $ES_HOST..."
until curl -s -u "${ES_USER}:${ES_PASS}" "${ES_HOST}" > /dev/null 2>&1; do
    retry_count=$((retry_count+1))
    if [ $retry_count -ge $max_retries ]; then
        echo "Failed to connect to Elasticsearch after $max_retries attempts. Exiting."
        exit 1
    fi
    echo "Elasticsearch not available yet. Retrying in $retry_interval seconds... (Attempt $retry_count/$max_retries)"
    sleep $retry_interval
done

echo "Elasticsearch is available. Starting load generator..."

# Run the load generator
python /app/elasticsearch_load_generator.py \
    --duration "$DURATION" \
    --threads "$THREADS" \
    --batch-size "$BATCH_SIZE" \
    --index-count "$INDEX_COUNT" \
    --interval "$INTERVAL"
