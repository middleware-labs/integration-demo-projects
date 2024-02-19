import json
import random
import time

from kafka import KafkaProducer


def main():
    producer = KafkaProducer(
        bootstrap_servers='localhost:9192',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        security_protocol='SASL_PLAINTEXT',
        sasl_mechanism='PLAIN',
        sasl_plain_username='mwkafkausername',
        sasl_plain_password='mwkafkapassword'
    )
    while True:
        producer.send(
            'mw-kafka-topic',
            {
                'message': 'Hello Middleware!'
            }
        )
        time.sleep(random.randint(1, 10))

    producer.close()


if __name__ == '__main__':
    main()
