# RabbitMQ Redis Project

This project demonstrates a simple message queue system using RabbitMQ with Redis as a storage backend.

## Prerequisites

- Python 3.8+
- RabbitMQ server running locally
- Redis server running locally

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure RabbitMQ and Redis servers are running locally on default ports.

3. Start the consumer in one terminal:
   ```bash
   python consumer.py
   ```

4. Start the producer in another terminal:
   ```bash
   python producer.py
   ```

5. Start the API server in a third terminal:
   ```bash
   python api.py
   ```

## Features

- Producer generates fake order data and publishes to RabbitMQ queue
- Consumer processes messages and stores them in Redis with 1-hour expiration
- REST API to retrieve orders from Redis
- Message persistence in RabbitMQ
- Fair dispatch for multiple consumers
- Error handling and message acknowledgment
- Automatic message requeuing on failure

## API Endpoints

- GET /orders - Retrieve all orders
- GET /orders/<order_id> - Retrieve specific order

## Architecture

```
Producer -> RabbitMQ Queue -> Consumer -> Redis
                                         ^
                                         |
                                      API Server
```
