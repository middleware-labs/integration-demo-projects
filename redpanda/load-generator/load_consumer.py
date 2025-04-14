import argparse
import time
from confluent_kafka import Consumer, KafkaException

parser = argparse.ArgumentParser()
parser.add_argument('--brokers', required=True)
parser.add_argument('--topic', required=True)
parser.add_argument('--num-messages', type=int, default=1000)
parser.add_argument('--message-size', type=int, default=1024)
parser.add_argument('--consumer-rate', type=int, default=1000)
args = parser.parse_args()

consumer = Consumer({
    'bootstrap.servers': args.brokers,
    'group.id': 'loadgen-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe([args.topic])
print("👂 Consuming messages...")

count = 0
interval = 1.0 / args.consumer_rate

try:
    while count < args.num_messages:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        print(f"📥 Received: Hello Redpanda ~ {msg.value().decode('utf-8')[:50]}...")
        count += 1
        time.sleep(interval)
finally:
    consumer.close()
    print("🎉 Finished consuming messages.")
