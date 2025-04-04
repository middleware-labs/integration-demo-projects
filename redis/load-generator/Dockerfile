FROM python:3.9-slim

WORKDIR /app

COPY load_generator.py .
COPY entrypoint.sh .

RUN pip install redis && \
    chmod +x entrypoint.sh

ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV LOAD_INTERVAL=0.1
ENV MAX_KEYS=10000
ENV BATCH_SIZE=100

ENTRYPOINT ["/app/entrypoint.sh"]
