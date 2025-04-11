# MariaDB Operations Demo

This repository contains a Python script for demonstrating and testing MariaDB database operations with simulated product and customer data.

## Overview

The demo script creates a sample e-commerce database and simulates various operations such as:
- Creating and managing products and customers
- Processing orders
- Running complex analytical queries
- Performing data modifications and deletions

This is useful for testing MariaDB performance, monitoring tools, and backup/recovery procedures.

## Prerequisites

- Docker and Docker Compose
- Python 3.6+
- Required Python packages: `mariadb`

## Setup

### 1. Install Required Python Package

```bash
pip install mariadb
```

### 2. Start MariaDB using Docker Compose

The included `docker-compose.yml` file sets up a MariaDB container with the necessary configuration:

```bash
docker-compose up -d
```

This will:
- Start a MariaDB container on port 3307
- Create a database named `mariadb`
- Set up a user `mw` with the password defined in the compose file
- Mount a persistent volume for data storage

### 3. Verify MariaDB is Running

```bash
docker ps
```

You should see the MariaDB container running.

## Running the Demo

The script accepts several command-line arguments to customize its behavior:

```bash
python mariadb_demo.py --password your_password [options]
```

### Command-line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | localhost | MariaDB host |
| `--port` | 3307 | MariaDB port |
| `--user` | mw | MariaDB username |
| `--password` | (required) | MariaDB password |
| `--database` | mariadb | MariaDB database name |
| `--iterations` | 0 | Number of operations to perform (0 for infinite) |
| `--delay` | 0.5 | Delay between operations in seconds |

### Examples

Run 100 operations with a 1-second delay between them:

```bash
python mariadb_demo.py --password your_password --iterations 100 --delay 1
```

Run continuously until interrupted (Ctrl+C):

```bash
python mariadb_demo.py --password your_password
```

Use a different database:

```bash
python mariadb_demo.py --password your_password --database test_db
```

## Database Structure

The script creates the following tables:

1. `products` - Product information
   - id, name, category, price, created_at

2. `customers` - Customer information
   - id, name, email, city, created_at

3. `orders` - Order header information
   - id, customer_id, order_date, total_amount

4. `order_items` - Order line items
   - id, order_id, product_id, quantity, price

## Operation Types

The script randomly performs these types of operations:

- **Create Order** (25% chance)
  - Creates a new order with random products for a random customer

- **Delete Order** (20% chance)
  - Deletes a random order and its related items

- **Delete Multiple Orders** (10% chance)
  - Deletes 2-5 orders in a single transaction

- **Run Complex Query** (15% chance)
  - Executes one of several complex analytical queries

- **Add Product** (10% chance)
  - Adds a new random product

- **Add Customer** (5% chance)
  - Adds a new random customer

- **Update Price** (5% chance)
  - Updates the price of a random product

- **Update Multiple Prices** (10% chance)
  - Updates prices for 3-8 products in a single transaction

## Monitoring and Analysis

This script is ideal for demonstrating:
- Query performance patterns
- Transaction processing
- Database growth over time
- Index effectiveness

You can connect tools like Prometheus, Grafana, or other monitoring solutions to observe the database behavior during operation.

## Stopping the Demo

- For finite iterations, the script will stop automatically after completion
- For infinite mode, press `Ctrl+C` to stop the script gracefully
- To stop the MariaDB container:

```bash
docker-compose down
```

Add `-v` to also remove the persistent volume:

```bash
docker-compose down -v
```

## Troubleshooting

- **Connection Issues**: Verify that the MariaDB container is running and accessible on port 3307
- **Authentication Errors**: Check the username and password parameters
- **Permission Denied**: Ensure the user has the necessary permissions in MariaDB
