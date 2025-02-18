import pika
import json
import redis
from config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE,
    REDIS_HOST, REDIS_PORT
)

# Initialize Redis connection
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

def process_message(ch, method, properties, body):
    try:
        order = json.loads(body)
        order_id = order['order_id']
        
        # Store order in Redis with 1 hour expiration
        redis_client.setex(
            f"order:{order_id}",
            3600,  # 1 hour expiration
            json.dumps(order)
        )
        
        print(f" [x] Processed order {order_id}")
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f" [!] Error processing message: {e}")
        # Negative acknowledgment, message will be requeued
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )
    channel = connection.channel()
    
    # Declare queue
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    
    # Fair dispatch - don't give more than one message to a worker at a time
    channel.basic_qos(prefetch_count=1)
    
    # Set up consumer
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=process_message
    )
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        start_consuming()
    except KeyboardInterrupt:
        print("\nStopping consumer...")
