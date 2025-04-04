# MySQL Operations Demo

This tool generates a variety of MySQL database operations to create activity metrics for OpenTelemetry (OTEL) dashboards and monitoring systems.

## Features

- Creates a sample database with products, customers, orders, and order items
- Performs a variety of database operations:
  - Creates new orders (25%)
  - Deletes individual orders (20%)
  - Bulk deletes multiple orders (10%)
  - Runs complex analytical queries (15%)
  - Adds new products (10%)
  - Adds new customers (5%)
  - Updates individual product prices (5%) 
  - Bulk updates multiple product prices (10%)
- Runs either for a specified number of iterations or indefinitely
- Includes randomized timing between operations

## Requirements

- Python 3.6+
- MySQL database
- `mysql-connector-python` package

0. Start the docker image in this directory by:
   ```bash
   docker-compose up -d
   ```

1. Install the required Python package:
   ```bash
   pip install mysql-connector-python
   ```

2. Set up your MySQL database:
   - Make sure you have a MySQL server running
   - Create a MySQL user with appropriate permissions:
     ```sql
     CREATE USER 'mw'@'%' IDENTIFIED BY 'your_password';
     GRANT ALL PRIVILEGES ON *.* TO 'mw'@'%';
     GRANT REPLICATION CLIENT ON *.* TO 'mw'@'%';
     GRANT PROCESS ON *.* TO 'mw'@'%';
     GRANT SELECT ON performance_schema.* TO 'mw'@'%';
     ALTER USER 'mw'@'%' WITH MAX_USER_CONNECTIONS 5;
     FLUSH PRIVILEGES;
     ```

## Usage

Run the script with your MySQL credentials:

```bash
python demo.py --password=your_password
```

### Command Line Options

- `--host`: MySQL host (default: localhost)
- `--port`: MySQL port (default: 3306)
- `--user`: MySQL username (default: mw)
- `--password`: MySQL password (required)
- `--database`: Database name (default: mysqldb)
- `--iterations`: Number of operations to perform (default: 0 for infinite)
- `--delay`: Delay between operations in seconds (default: 0.5)

### Examples

Run 100 operations with a 0.2 second delay:
```bash
python demo.py --password=your_password --iterations=100 --delay=0.2
```

Run indefinitely with default delay:
```bash
python demo.py --password=your_password
```

Connect to a remote MySQL server:
```bash
python demo.py --host=mysql.example.com --port=3306 --user=mw --password=your_password
```

## Stopping the Demo

Press `Ctrl+C` to stop the script when running in infinite mode.

## Database Schema

The script creates the following tables:

- `products`: Product catalog with name, category, and price
- `customers`: Customer information with name, email, and city
- `orders`: Order records with customer reference and total amount
- `order_items`: Individual line items in each order

## Monitoring

This tool is designed to be used with monitoring systems like Prometheus, Grafana, and OpenTelemetry. The varied database operations will generate metrics that can be visualized in dashboards to:

- Monitor query performance
- Track database load
- Analyze operation patterns
- Test alerting systems

