#!/usr/bin/env python3
import redis
import random
import string
import time
import argparse
import sys
from datetime import datetime

def generate_random_string(length=10):
    """Generate a random string of specified length."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_random_key(prefix='key', length=5):
    """Generate a random key with prefix."""
    return f"{prefix}:{generate_random_string(length)}"

def run_load_generator(host='localhost', port=6379, interval=0.1, max_keys=10000, batch_size=100):
    """
    Run load generator against Redis.
    
    Parameters:
    - host: Redis host
    - port: Redis port
    - interval: Time interval between batches (in seconds)
    - max_keys: Maximum number of keys to keep in Redis
    - batch_size: Number of operations per batch
    """
    print(f"Connecting to Redis at {host}:{port}")
    r = redis.Redis(host=host, port=port, decode_responses=True)
    
    try:
        # Test connection
        r.ping()
        print("Connected to Redis successfully!")
    except redis.ConnectionError:
        print("Failed to connect to Redis. Make sure Redis is running and accessible.")
        sys.exit(1)
    
    operation_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Perform a batch of operations
            for _ in range(batch_size):
                operation = random.choice(['set', 'get', 'hset', 'lpush', 'incr', 'expire', 'delete'])
                
                if operation == 'set':
                    key = generate_random_key('string')
                    value = generate_random_string(random.randint(10, 100))
                    r.set(key, value, ex=random.randint(60, 3600))
                
                elif operation == 'get':
                    # Get random existing key
                    keys = r.keys('string:*')
                    if keys:
                        key = random.choice(keys)
                        r.get(key)
                
                elif operation == 'hset':
                    key = generate_random_key('hash')
                    field = generate_random_string(5)
                    value = generate_random_string(random.randint(10, 50))
                    r.hset(key, field, value)
                
                elif operation == 'lpush':
                    key = generate_random_key('list')
                    value = generate_random_string(random.randint(10, 50))
                    r.lpush(key, value)
                    # Sometimes do a random range query
                    if random.random() < 0.3:
                        r.lrange(key, 0, random.randint(5, 20))
                
                elif operation == 'incr':
                    key = generate_random_key('counter')
                    r.incr(key)
                
                elif operation == 'expire':
                    keys = r.keys('*')
                    if keys:
                        key = random.choice(keys)
                        r.expire(key, random.randint(60, 3600))
                
                elif operation == 'delete':
                    keys = r.keys('*')
                    if keys and len(keys) > max_keys:
                        # Delete some keys if we have too many
                        keys_to_delete = random.sample(keys, min(100, len(keys) - max_keys))
                        for key in keys_to_delete:
                            r.delete(key)
            
            # Periodically run some more expensive operations
            if random.random() < 0.1:
                # Run a scan operation
                cursor, keys = r.scan(0, match='*', count=random.randint(100, 500))
            
            if random.random() < 0.05:
                # Run a sorted set operation
                zkey = generate_random_key('zset')
                for i in range(random.randint(5, 20)):
                    r.zadd(zkey, {generate_random_string(10): random.random() * 100})
                r.zrange(zkey, 0, -1, withscores=True)
            
            # Simulate some memory consumption with large values occasionally
            if random.random() < 0.01:
                big_key = generate_random_key('big')
                big_value = generate_random_string(random.randint(1000, 10000))
                r.set(big_key, big_value, ex=random.randint(10, 60))  # Short TTL to avoid memory issues
            
            operation_count += batch_size
            current_time = time.time()
            elapsed = current_time - start_time
            
            if elapsed >= 5:  # Log stats every 5 seconds
                ops_per_second = operation_count / elapsed
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Operations: {operation_count}, Rate: {ops_per_second:.2f} ops/sec, Keys: {len(r.keys('*'))}")
                start_time = current_time
                operation_count = 0
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\nLoad generator stopped by user.")
    finally:
        r.close()
        print("Connection to Redis closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Redis Load Generator')
    parser.add_argument('--host', default='localhost', help='Redis host')
    parser.add_argument('--port', type=int, default=6379, help='Redis port')
    parser.add_argument('--interval', type=float, default=0.1, help='Interval between batches in seconds')
    parser.add_argument('--max-keys', type=int, default=10000, help='Maximum keys to maintain')
    parser.add_argument('--batch-size', type=int, default=100, help='Operations per batch')
    
    args = parser.parse_args()
    
    run_load_generator(
        host=args.host,
        port=args.port,
        interval=args.interval,
        max_keys=args.max_keys,
        batch_size=args.batch_size
    )
