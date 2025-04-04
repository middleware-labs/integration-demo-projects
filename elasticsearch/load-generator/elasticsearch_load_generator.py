import requests
import json
import random
import time
import concurrent.futures
import argparse
import os
from datetime import datetime
import string
import sys

# Read environment variables
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
ES_USER = os.getenv("ES_USER", "elastic")
ES_PASS = os.getenv("ES_PASS", "changeme")
DURATION = int(os.getenv("DURATION", "300"))  # 0 means run continuously
THREADS = int(os.getenv("THREADS", "4"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
INDEX_COUNT = int(os.getenv("INDEX_COUNT", "3"))
INTERVAL = float(os.getenv("INTERVAL", "2"))  # Seconds between batches

INDEX_NAME = "load_test"
AUTH = (ES_USER, ES_PASS)
HEADERS = {"Content-Type": "application/json"}

# Command line arguments (override environment variables)
parser = argparse.ArgumentParser(description='Generate load on Elasticsearch')
parser.add_argument('--duration', type=int, default=DURATION, help='Duration in seconds to run the test (0 = continuous)')
parser.add_argument('--threads', type=int, default=THREADS, help='Number of concurrent threads')
parser.add_argument('--batch-size', type=int, default=BATCH_SIZE, help='Batch size for bulk operations')
parser.add_argument('--index-count', type=int, default=INDEX_COUNT, help='Number of indices to create')
parser.add_argument('--interval', type=float, default=INTERVAL, help='Seconds between operation batches')
args = parser.parse_args()

# Verify connection to Elasticsearch
def check_connection():
    max_retries = 10
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{ES_HOST}", auth=AUTH)
            if response.status_code == 200:
                print(f"Successfully connected to Elasticsearch at {ES_HOST}")
                return True
            else:
                print(f"Failed to connect to Elasticsearch: {response.status_code}")
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}")
        
        print(f"Retrying in {retry_delay} seconds... ({i+1}/{max_retries})")
        time.sleep(retry_delay)
    
    return False

# Create index with mappings
def create_index(index_name):
    mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "user_id": {"type": "keyword"},
                "message": {"type": "text", "analyzer": "english"},
                "tags": {"type": "keyword"},
                "location": {"type": "geo_point"},
                "status_code": {"type": "integer"},
                "response_time": {"type": "float"},
                "is_error": {"type": "boolean"},
                "nested_data": {
                    "type": "nested",
                    "properties": {
                        "key": {"type": "keyword"},
                        "value": {"type": "text"}
                    }
                }
            }
        },
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 0,
            "refresh_interval": "1s"
        }
    }
    
    try:
        response = requests.put(
            f"{ES_HOST}/{index_name}",
            auth=AUTH,
            headers=HEADERS,
            data=json.dumps(mapping)
        )
        if response.status_code in [200, 201]:
            print(f"Index {index_name} created successfully")
        else:
            print(f"Failed to create index {index_name}: {response.text}")
    except Exception as e:
        print(f"Error creating index: {e}")

# Generate random document
def generate_document():
    user_id = f"user_{random.randint(1, 1000)}"
    message = ''.join(random.choices(string.ascii_letters + ' ', k=random.randint(20, 200)))
    tags = random.sample(["error", "warning", "info", "debug", "critical", "notice", "alert", "emergency"], 
                         random.randint(1, 3))
    
    # Generate random geo coordinates
    lat = random.uniform(-90, 90)
    lon = random.uniform(-180, 180)
    
    # Generate nested data
    nested_items = []
    for _ in range(random.randint(1, 5)):
        nested_items.append({
            "key": f"key_{random.randint(1, 100)}",
            "value": ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "message": message,
        "tags": tags,
        "location": {"lat": lat, "lon": lon},
        "status_code": random.choice([200, 201, 204, 400, 401, 403, 404, 500, 503]),
        "response_time": round(random.uniform(0.001, 2.0), 3),
        "is_error": random.choice([True, False]),
        "nested_data": nested_items
    }

# Insert documents in bulk
def bulk_insert(index_name, batch_size):
    bulk_data = []
    
    for _ in range(batch_size):
        # Add the action and metadata
        bulk_data.append(json.dumps({"index": {"_index": index_name}}))
        # Add the document source
        bulk_data.append(json.dumps(generate_document()))
    
    # Add newlines between each action
    bulk_request_body = "\n".join(bulk_data) + "\n"
    
    try:
        response = requests.post(
            f"{ES_HOST}/_bulk",
            auth=AUTH,
            headers={"Content-Type": "application/x-ndjson"},
            data=bulk_request_body
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get('errors', True):
                print(f"Bulk insert completed with some errors: {result.get('items', [])[0]}")
            else:
                print(f"Successfully inserted {batch_size} documents into {index_name}")
        else:
            print(f"Failed bulk insert: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"Error during bulk insert: {e}")

# Perform searches with different complexities
def perform_search(index_name):
    search_types = [
        "simple_term",
        "multi_term",
        "range",
        "aggregation",
        "complex"
    ]
    
    search_type = random.choice(search_types)
    query = None
    
    if search_type == "simple_term":
        user_id = f"user_{random.randint(1, 1000)}"
        query = {
            "query": {
                "term": {
                    "user_id": user_id
                }
            }
        }
    elif search_type == "multi_term":
        tags = random.sample(["error", "warning", "info", "debug", "critical"], 
                            random.randint(1, 3))
        query = {
            "query": {
                "terms": {
                    "tags": tags
                }
            }
        }
    elif search_type == "range":
        query = {
            "query": {
                "range": {
                    "response_time": {
                        "gte": random.uniform(0.0, 0.5),
                        "lte": random.uniform(0.5, 2.0)
                    }
                }
            }
        }
    elif search_type == "aggregation":
        query = {
            "size": 0,
            "aggs": {
                "status_codes": {
                    "terms": {
                        "field": "status_code"
                    }
                },
                "avg_response_time": {
                    "avg": {
                        "field": "response_time"
                    }
                },
                "error_histogram": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "hour"
                    }
                }
            }
        }
    elif search_type == "complex":
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"message": random.choice(["error", "warning", "success", "data", "user", "system"])}},
                        {"range": {"response_time": {"gte": 0.1}}}
                    ],
                    "should": [
                        {"term": {"tags": random.choice(["error", "warning", "info", "debug", "critical"])}}
                    ],
                    "must_not": [
                        {"term": {"status_code": 200}}
                    ],
                    "filter": [
                        {
                            "geo_distance": {
                                "distance": f"{random.randint(10, 1000)}km",
                                "location": {
                                    "lat": random.uniform(-90, 90),
                                    "lon": random.uniform(-180, 180)
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {"timestamp": {"order": "desc"}}
            ]
        }
    
    if query:
        try:
            response = requests.post(
                f"{ES_HOST}/{index_name}/_search",
                auth=AUTH,
                headers=HEADERS,
                data=json.dumps(query)
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Search completed: {search_type} - found {result.get('hits', {}).get('total', {}).get('value', 0)} hits")
            else:
                print(f"Search failed: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"Error during search: {e}")

# Perform field stats aggregation
def field_stats(index_name):
    try:
        agg_query = {
            "size": 0,
            "aggs": {
                "avg_response_time": {
                    "avg": {
                        "field": "response_time"
                    }
                },
                "max_response_time": {
                    "max": {
                        "field": "response_time"
                    }
                },
                "status_distribution": {
                    "terms": {
                        "field": "status_code",
                        "size": 10
                    }
                },
                "errors_over_time": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "hour"
                    },
                    "aggs": {
                        "error_count": {
                            "filter": {
                                "term": {
                                    "is_error": True
                                }
                            }
                        }
                    }
                }
            }
        }
        
        response = requests.post(
            f"{ES_HOST}/{index_name}/_search",
            auth=AUTH,
            headers=HEADERS,
            data=json.dumps(agg_query)
        )
        
        if response.status_code == 200:
            print(f"Field stats aggregation completed for {index_name}")
        else:
            print(f"Field stats failed: {response.status_code}")
    except Exception as e:
        print(f"Error during field stats: {e}")

# Create and update index template
def manage_templates():
    try:
        # Create component template
        component_template = {
            "template": {
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "dynamic_templates": [
                        {
                            "strings_as_keywords": {
                                "match_mapping_type": "string",
                                "mapping": {
                                    "type": "keyword"
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        response = requests.put(
            f"{ES_HOST}/_component_template/load_test_component",
            auth=AUTH,
            headers=HEADERS,
            data=json.dumps(component_template)
        )
        
        if response.status_code in [200, 201]:
            print("Component template created/updated")
        
        # Create index template
        index_template = {
            "index_patterns": ["load_test*"],
            "template": {
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 0
                }
            },
            "composed_of": ["load_test_component"],
            "priority": 500
        }
        
        response = requests.put(
            f"{ES_HOST}/_index_template/load_test_template",
            auth=AUTH,
            headers=HEADERS,
            data=json.dumps(index_template)
        )
        
        if response.status_code in [200, 201]:
            print("Index template created/updated")
        
    except Exception as e:
        print(f"Error managing templates: {e}")

# Get cluster stats
def get_cluster_stats():
    try:
        response = requests.get(
            f"{ES_HOST}/_cluster/stats",
            auth=AUTH
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"Cluster name: {stats.get('cluster_name')}")
            print(f"Nodes: {stats.get('nodes', {}).get('count', {}).get('total')}")
            print(f"Indices: {stats.get('indices', {}).get('count')}")
            print(f"Shards: {stats.get('indices', {}).get('shards', {}).get('total')}")
            print(f"Documents: {stats.get('indices', {}).get('docs', {}).get('count')}")
        else:
            print(f"Failed to get cluster stats: {response.status_code}")
    except Exception as e:
        print(f"Error getting cluster stats: {e}")

# Worker function to perform various operations
def worker(index_names, batch_size, stop_time, interval):
    operations = [
        {"name": "insert", "weight": 70, "func": lambda: bulk_insert(random.choice(index_names), batch_size)},
        {"name": "search", "weight": 20, "func": lambda: perform_search(random.choice(index_names))},
        {"name": "stats", "weight": 5, "func": lambda: field_stats(random.choice(index_names))},
        {"name": "template", "weight": 1, "func": manage_templates},
        {"name": "cluster_stats", "weight": 4, "func": get_cluster_stats}
    ]
    
    # Extract just the weights for random.choices
    weights = [op["weight"] for op in operations]
    
    while stop_time == 0 or time.time() < stop_time:
        # Choose operation based on weights
        operation = random.choices(operations, weights=weights, k=1)[0]
        
        print(f"Performing operation: {operation['name']}")
        try:
            operation["func"]()
        except Exception as e:
            print(f"Error in operation {operation['name']}: {e}")
        
        # Sleep between operations
        time.sleep(interval)

def main():
    print(f"Starting Elasticsearch load generator with settings:")
    print(f"ES_HOST: {ES_HOST}")
    print(f"DURATION: {args.duration} seconds (0 = continuous)")
    print(f"THREADS: {args.threads}")
    print(f"BATCH_SIZE: {args.batch_size}")
    print(f"INDEX_COUNT: {args.index_count}")
    print(f"INTERVAL: {args.interval} seconds")
    
    if not check_connection():
        print("Exiting due to connection failure")
        sys.exit(1)
    
    # Create multiple indices
    index_names = [f"{INDEX_NAME}_{i}" for i in range(1, args.index_count + 1)]
    
    for index_name in index_names:
        create_index(index_name)
    
    # Create initial templates
    manage_templates()
    
    print(f"Starting load test with {args.threads} threads")
    
    # Set stop time (0 means run continuously)
    stop_time = 0 if args.duration == 0 else time.time() + args.duration
    
    # Create and start worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for _ in range(args.threads):
            futures.append(
                executor.submit(worker, index_names, args.batch_size, stop_time, args.interval)
            )
        
        # Wait for all workers to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Worker error: {e}")
    
    print("Load test completed")

if __name__ == "__main__":
    main()
