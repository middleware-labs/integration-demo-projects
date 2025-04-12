import requests
import time
import random
from typing import Dict, Any
from datetime import datetime
from tqdm import tqdm
from random import randrange

def generate_random_item() -> Dict[str, Any]:
    categories = ['Electronics', 'Books', 'Clothing', 'Food', 'Tools']
    adjectives = ['Awesome', 'Fantastic', 'Basic', 'Premium', 'Budget']
    
    price = round(random.uniform(5.99, 299.99), 2)
    category = random.choice(categories)
    adjective = random.choice(adjectives)
    item_id = random.randint(1000, 9999)
    
    return {
        "name": f"{adjective} {category} Item {item_id}",
        "price": price,
        "desc": f"A {adjective.lower()} quality {category.lower()} item. SKU: {item_id}"
    }

def generate_invalid_item() -> Dict[str, Any]:
    invalid_types = [
        {"name": 123, "price": "not a number", "desc": True},
        {"name": "", "price": -50, "desc": ""},
        {"random_field": "unexpected"},
        {"name": "x" * 1000, "price": 10**6, "desc": "too large"},
    ]
    return random.choice(invalid_types)

def run_create_reqs() -> None:
    success_count = 0
    failure_count = 0
    start_time = time.time()
    headers = {'Content-Type': 'application/json'}
    
    # We'll track different types of HTTP status codes and errors
    error_types = {
        'client_errors': 0,    # 400-level errors (like validation failures)
        'server_errors': 0,    # 500-level errors
        'timeout_errors': 0,   # Connection timeouts
        'connection_errors': 0  # Network/connection issues
    }

    for i in tqdm(range(1000)):
        try:
            # Add random delay between requests
            # time.sleep(random.uniform(0.1, 0.3))
            
            random_num = random.random()
            
            if random_num < 0.15:  # 15% chance of invalid data
                item_data = generate_invalid_item()
                endpoint = "item"
            elif random_num < 0.25:  # 10% chance of wrong endpoint
                item_data = generate_random_item()
                endpoint = f"item-error"
            else:  # 75% chance of valid request
                item_data = generate_random_item()
                endpoint = "item"

            timeout = 5 if random.random() > 0.05 else 0.001

            # Make the request and capture the response
            response = requests.post(
                f"http://localhost:8000/{endpoint}",
                json=item_data,
                headers=headers,
                timeout=timeout
            )
            
            # Check response status and categorize errors
            if response.status_code >= 500:
                error_types['server_errors'] += 1
                failure_count += 1
                print(f"Server error ({response.status_code}) on request {i}")
            elif response.status_code >= 400:
                error_types['client_errors'] += 1
                failure_count += 1
                print(f"Client error ({response.status_code}) on request {i}: {response.text}")
            else:
                success_count += 1
                if random.random() < 0.1:  # 10% chance to log success
                    print(f"Success - Created item: {item_data['name']}")

        except requests.exceptions.Timeout:
            error_types['timeout_errors'] += 1
            failure_count += 1
            print(f"Timeout error on request {i}")
        
        except requests.exceptions.ConnectionError:
            error_types['connection_errors'] += 1
            failure_count += 1
            print(f"Connection error on request {i}")
        
        except requests.exceptions.RequestException as e:
            # Catch any other request-related errors
            failure_count += 1
            print(f"Unexpected error on request {i}: {str(e)}")
            print(f"Failed request data: {item_data}")

        # Show progress with percentage
        if i % 100 == 0:
            progress = (i + 1) / 1000 * 100
            print(f"Progress: {progress:.1f}% ({i + 1}/1000 requests)")

    # Calculate and display detailed statistics
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n=== Test Results ===")
    print(f"Total requests: 1000")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print("\nError Breakdown:")
    for error_type, count in error_types.items():
        print(f"  {error_type}: {count}")
    print(f"\nPerformance Metrics:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per request: {(total_time/1000):.3f} seconds")
    print(f"Success rate: {(success_count/1000*100):.1f}%")

if __name__ == "__main__":
   for i in range(1000000):
      time.sleep(randrange(10))
      run_create_reqs()
