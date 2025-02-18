import pika
import json
from faker import Faker
import time
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE

fake = Faker()

def create_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    return connection, channel

def publish_message():
    connection, channel = create_connection()
    
    try:
        while True:
            # Generate fake order data
            order = {
                'order_id': fake.uuid4(),
                'customer': fake.name(),
                'product': fake.word(),
                'quantity': fake.random_int(min=1, max=10),
                'timestamp': str(time.time())
            }
            
            channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(order),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            print(f" [x] Sent order: {order['order_id']}")
            time.sleep(2)  # Wait 2 seconds between messages
            
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        connection.close()

if __name__ == '__main__':
    publish_message()
