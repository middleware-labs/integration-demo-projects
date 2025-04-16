FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY load_producer.py .
COPY load_consumer.py .
COPY run.sh .
RUN chmod +x run.sh

CMD ["./run.sh"]
