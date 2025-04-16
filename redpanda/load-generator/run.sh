#!/bin/bash

set -e

# This script runs a producer and consumer to generate load on a Redpanda cluster. 
# Generates 1000 messages (num-messages flag) of 1KB each.

python load_producer.py \
    --brokers redpanda-0:9092 \
    --topic test-topic-6 \
    --num-messages 1000 \
    --message-size 1024 \
    --producer-rate 1000 

python load_consumer.py \
    --brokers redpanda-0:9092 \
    --topic test-topic-6 \
    --num-messages 1000 \
    --message-size 1024 \
    --consumer-rate 1000
