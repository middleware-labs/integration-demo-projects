import json
import multiprocessing

from kafka import KafkaConsumer

stop_event = multiprocessing.Event()


def main():
    consumer = KafkaConsumer(
        bootstrap_servers='localhost:9192',
        group_id='mw-consumer-group',
        security_protocol='SASL_PLAINTEXT',
        sasl_mechanism='PLAIN',
        sasl_plain_username='mwkafkausername',
        sasl_plain_password='mwkafkapassword'
    )
    consumer.subscribe(['mw-kafka-topic'])

    while not stop_event.is_set():
        for message in consumer:
            json_data = json.loads(message.value)
            print(json.dumps(json_data, indent=2))
            if stop_event.is_set():
                break

    consumer.close()


if __name__ == '__main__':
    main()
