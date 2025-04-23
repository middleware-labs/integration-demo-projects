#!/usr/bin/env python3
import random
import time
import datetime
import os
import string
import argparse
import threading
from pathlib import Path

def generate_random_hex(length=8):
    """Generate a random hex string of specified length"""
    return ''.join(random.choices('abcdef0123456789', k=length))

def generate_random_ip():
    """Generate a random IP address"""
    return f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def generate_app_log(log_file):
    """Generate application logs similar to loggen.sh"""
    # Constants from the original script
    LOG_LEVELS = ["INFO", "WARN", "ERROR", "DEBUG"]
    SERVICES = ["web-server", "database", "auth-service", "api-gateway", "cache"]
    MESSAGES = [
        "User login successful",
        "Connection established",
        "Request processed",
        "Data retrieved from database",
        "Cache updated",
        "Session expired",
        "Operation completed successfully",
        "Failed to connect to database",
        "Invalid authentication token",
        "Resource not found",
        "Permission denied",
        "Timeout occurred"
    ]
    
    count = 0
    print(f"Generating application logs at a rate of 2 per second. Writing to: {log_file}")
    
    try:
        while True:
            # Generate 2 logs
            for _ in range(2):
                # Get current timestamp with milliseconds
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                # Select random elements
                level = random.choice(LOG_LEVELS)
                service = random.choice(SERVICES)
                message = random.choice(MESSAGES)
                ip = generate_random_ip()
                request_id = generate_random_hex(8)
                
                # Create log entry
                log_entry = f"[{timestamp}] [{level}] [{service}] [{ip}] [REQ-{request_id}] {message}"
                
                # Write to file
                with open(log_file, 'a') as f:
                    f.write(log_entry + "\n")
                
                count += 1
            
            # Display counter every 10 seconds (20 logs)
            if count % 20 == 0:
                print(f"Generated {count} application log entries so far...")
            
            # Sleep for half a second
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print(f"\nApplication log generation stopped. Generated {count} log entries to {log_file}")

def generate_java_error(log_file):
    """Generate Java-style error logs similar to loggenmultiline.sh"""
    # Constants from the original script
    ERRORS = [
        "NullPointerException",
        "ArrayIndexOutOfBoundsException",
        "ClassCastException",
        "IllegalArgumentException",
        "OutOfMemoryError",
        "StackOverflowError",
        "RuntimeException",
        "IOException",
        "FileNotFoundException"
    ]
    
    CLASSES = [
        "com.example.myproject.Book",
        "com.example.myproject.Author",
        "com.example.myproject.User",
        "com.example.myproject.Database",
        "com.example.myproject.Controller",
        "com.example.myproject.Service",
        "com.example.myproject.Repository",
        "com.example.myproject.Utility"
    ]
    
    METHODS = [
        "getTitle",
        "processData",
        "fetchRecords",
        "validateInput",
        "connect",
        "initialize",
        "executeQuery",
        "parseResponse",
        "updateCache",
        "renderView"
    ]
    
    count = 0
    print(f"Generating Java error logs every 2 seconds. Writing to: {log_file}")
    
    try:
        while True:
            # Generate random line numbers
            line1 = random.randint(1, 100)
            line2 = random.randint(1, 100)
            line3 = random.randint(1, 100)
            
            # Select random elements
            error = random.choice(ERRORS)
            class1 = random.choice(CLASSES)
            class2 = random.choice(CLASSES)
            class3 = random.choice(CLASSES)
            method1 = random.choice(METHODS)
            method2 = random.choice(METHODS)
            method3 = random.choice(METHODS)
            
            # Create error message
            error_message = [
                f"Exception in thread \"main\" java.lang.{error}",
                f"at {class1}.{method1}({class1.split('.')[-1]}.java:{line1})",
                f"at {class2}.{method2}({class2.split('.')[-1]}.java:{line2})",
                f"at {class3}.{method3}({class3.split('.')[-1]}.java:{line3})",
                "----------------------------------------"
            ]
            
            # Write to file
            with open(log_file, 'a') as f:
                f.write("\n".join(error_message) + "\n")
            
            count += 1
            
            if count % 5 == 0:
                print(f"Generated {count} Java error logs so far...")
            
            # Wait for 2 seconds
            time.sleep(2)
    
    except KeyboardInterrupt:
        print(f"\nJava error log generation stopped. Generated {count} error entries to {log_file}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate application logs and Java error logs')
    parser.add_argument('--app-log', default='app.log', help='Application log file (default: app.log)')
    parser.add_argument('--error-log', default='java_error.log', help='Java error log file (default: java_error.log)')
    parser.add_argument('--no-app-logs', action='store_true', help='Disable application log generation')
    parser.add_argument('--no-error-logs', action='store_true', help='Disable Java error log generation')
    
    args = parser.parse_args()
    
    # Create directories if needed
    Path(os.path.dirname(args.app_log) or '.').mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(args.error_log) or '.').mkdir(parents=True, exist_ok=True)
    
    # Start threads for each log generator
    threads = []
    
    if not args.no_app_logs:
        app_thread = threading.Thread(target=generate_app_log, args=(args.app_log,))
        app_thread.daemon = True
        threads.append(app_thread)
    
    if not args.no_error_logs:
        error_thread = threading.Thread(target=generate_java_error, args=(args.error_log,))
        error_thread.daemon = True
        threads.append(error_thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    if not threads:
        print("No log generators enabled. Use --help for options.")
        return
    
    print("Log generators started. Press Ctrl+C to stop all generators.")
    
    try:
        # Keep the main thread alive until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nLog generation stopped.")

if __name__ == "__main__":
    main()
