#!/usr/bin/env python3
"""
Cassandra Load Generator for Metrics Demo
This script continually generates load on a Cassandra database to create a stream of metrics.
"""

import os
import time
import random
import logging
import uuid
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration from environment variables with defaults
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'localhost')
CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', 9042))
OPERATIONS_PER_SECOND = int(os.getenv('OPERATIONS_PER_SECOND', 100))
KEYSPACE_NAME = 'metrics_demo'
TABLE_NAME = 'user_events'

# Initialize Faker
fake = Faker()

def connect_to_cassandra():
    """Establish connection to Cassandra and set up schema if needed."""
    max_retries = 20
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to Cassandra at {CASSANDRA_HOST}:{CASSANDRA_PORT} (attempt {attempt+1}/{max_retries})")
            cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
            session = cluster.connect()
            
            # Create keyspace if it doesn't exist
            session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {KEYSPACE_NAME}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
            """)
            session.set_keyspace(KEYSPACE_NAME)
            
            # Create table if it doesn't exist
            session.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id uuid PRIMARY KEY,
                    username text,
                    email text,
                    event_type text,
                    event_data text,
                    created_at timestamp
                )
            """)
            
            logger.info("Successfully connected to Cassandra and set up schema")
            return cluster, session
        
        except Exception as e:
            logger.warning(f"Failed to connect to Cassandra: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Could not connect to Cassandra.")
                raise

def generate_random_event():
    """Generate a random user event."""
    event_types = ['login', 'logout', 'purchase', 'view_item', 'add_to_cart', 'remove_from_cart', 'checkout']
    
    return {
        'id': uuid.uuid4(),
        'username': fake.user_name(),
        'email': fake.email(),
        'event_type': random.choice(event_types),
        'event_data': fake.json(data_columns={'item_id': 'random_int', 'price': 'pyfloat'}, num_rows=1),
        'created_at': datetime.now()
    }

def insert_event(session, event):
    """Insert an event into the Cassandra table."""
    query = f"""
        INSERT INTO {TABLE_NAME} (id, username, email, event_type, event_data, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (
        event['id'],
        event['username'],
        event['email'],
        event['event_type'],
        event['event_data'],
        event['created_at']
    ))

def select_random_events(session, limit=10):
    """Select random events from the table."""
    query = SimpleStatement(f"SELECT * FROM {TABLE_NAME} LIMIT {limit}")
    return session.execute(query)

def count_events(session):
    """Count the total number of events in the table."""
    query = SimpleStatement(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    return session.execute(query).one()

def delete_random_events(session, limit=5):
    """Delete random events to create more workload."""
    # First get some IDs to delete
    query = SimpleStatement(f"SELECT id FROM {TABLE_NAME} LIMIT {limit}")
    rows = session.execute(query)
    
    # Then delete them one by one to spread the load
    for row in rows:
        delete_query = f"DELETE FROM {TABLE_NAME} WHERE id = %s"
        session.execute(delete_query, (row.id,))

def run_load_generator():
    """Main function to continuously generate load on Cassandra."""
    cluster, session = connect_to_cassandra()
    
    try:
        operations_counter = 0
        last_log_time = time.time()
        sleep_time = 1.0 / OPERATIONS_PER_SECOND if OPERATIONS_PER_SECOND > 0 else 0.01
        
        logger.info(f"Starting load generation with target {OPERATIONS_PER_SECOND} operations per second")
        
        while True:
            # Decide which operation to perform
            operation = random.choices(
                ['insert', 'select', 'count', 'delete'],
                weights=[0.6, 0.3, 0.05, 0.05],
                k=1
            )[0]
            
            if operation == 'insert':
                event = generate_random_event()
                insert_event(session, event)
            elif operation == 'select':
                limit = random.randint(5, 20)
                results = select_random_events(session, limit)
                # Iterate through results to ensure they're actually fetched
                for _ in results:
                    pass
            elif operation == 'count':
                count = count_events(session)
                logger.debug(f"Current event count: {count}")
            elif operation == 'delete':
                delete_random_events(session, random.randint(1, 5))
            
            operations_counter += 1
            
            # Log progress every 5 seconds
            current_time = time.time()
            if current_time - last_log_time >= 5:
                elapsed = current_time - last_log_time
                rate = operations_counter / elapsed
                logger.info(f"Performed {operations_counter} operations in {elapsed:.2f} seconds ({rate:.2f} ops/sec)")
                last_log_time = current_time
                operations_counter = 0
            
            # Sleep to maintain the target operations per second
            time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        logger.info("Load generator stopped by user")
    except Exception as e:
        logger.error(f"Error in load generator: {e}")
    finally:
        logger.info("Shutting down load generator")
        cluster.shutdown()

if __name__ == "__main__":
    try:
        run_load_generator()
    except Exception as e:
        logger.error(f"Load generator failed: {e}")
        raise
