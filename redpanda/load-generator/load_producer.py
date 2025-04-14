import argparse
import time
import random
from confluent_kafka import Producer

def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

parser = argparse.ArgumentParser()
parser.add_argument('--brokers', required=True)
parser.add_argument('--topic', required=True)
parser.add_argument('--num-messages', type=int, default=1000)
parser.add_argument('--message-size', type=int, default=1024)
parser.add_argument('--producer-rate', type=int, default=1000)
args = parser.parse_args()

producer = Producer({'bootstrap.servers': args.brokers})

interval = 1.0 / args.producer_rate

for i in range(args.num_messages):
    message = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=args.message_size))
    producer.produce(args.topic, value=message, callback=delivery_report)
    producer.poll(0)
    time.sleep(interval)

producer.flush()
print("🎉 Finished producing messages.")
