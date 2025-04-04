#!/bin/bash
set -e

python -u load_generator.py \
  --host "${REDIS_HOST}" \
  --port "${REDIS_PORT}" \
  --interval "${LOAD_INTERVAL}" \
  --max-keys "${MAX_KEYS}" \
  --batch-size "${BATCH_SIZE}"
