import mariadb
import random
import time
import datetime
import argparse
import signal
import sys
from mariadb import Error

# Parse command line arguments
parser = argparse.ArgumentParser(description='MariaDB Operations Demo Script')
parser.add_argument('--host', default='localhost', help='MariaDB host')
parser.add_argument('--port', default=3307, type=int, help='MariaDB port')
parser.add_argument('--user', default='mw', help='MariaDB username')
parser.add_argument('--password', required=True, help='MariaDB password')
parser.add_argument('--database', default='mariadb', help='MariaDB database name')
parser.add_argument('--iterations', default=0, type=int, help='Number of operations to perform (0 for infinite)')
parser.add_argument('--delay', default=0.5, type=float, help='Delay between operations in seconds')
args = parser.parse_args()

# Sample product data
products = [
    {"name": "Laptop", "category": "Electronics", "price": 999.99},
    {"name": "Smartphone", "category": "Electronics", "price": 699.99},
    {"name": "Headphones", "category": "Accessories", "price": 129.99},
    {"name": "Monitor", "category": "Electronics", "price": 349.99},
    {"name": "Keyboard", "category": "Accessories", "price": 79.99},
    {"name": "Mouse", "category": "Accessories", "price": 49.99},
    {"name": "Tablet", "category": "Electronics", "price": 499.99},
    {"name": "Printer", "category": "Office", "price": 199.99},
    {"name": "Camera", "category": "Electronics", "price": 599.99},
    {"name": "Speaker", "category": "Audio", "price": 149.99},
    {"name": "Smart Watch", "category": "Wearables", "price": 249.99},
    {"name": "Gaming Console", "category": "Entertainment", "price": 399.99},
    {"name": "External SSD", "category": "Storage", "price": 89.99},
    {"name": "Wireless Earbuds", "category": "Audio", "price": 129.99},
    {"name": "LED TV", "category": "Electronics", "price": 799.99},
    {"name": "Desk Chair", "category": "Furniture", "price": 199.99},
    {"name": "Webcam", "category": "Accessories", "price": 69.99},
    {"name": "Bluetooth Speaker", "category": "Audio", "price": 79.99},
    {"name": "Microphone", "category": "Audio", "price": 99.99},
    {"name": "Graphics Card", "category": "Components", "price": 449.99}
]

# Sample customer data
customers = [
    {"name": "John Doe", "email": "john.doe@example.com", "city": "New York"},
    {"name": "Jane Smith", "email": "jane.smith@example.com", "city": "Los Angeles"},
    {"name": "Bob Johnson", "email": "bob.johnson@example.com", "city": "Chicago"},
    {"name": "Alice Brown", "email": "alice.brown@example.com", "city": "Houston"},
    {"name": "Charlie Wilson", "email": "charlie.wilson@example.com", "city": "Phoenix"},
    {"name": "Emma Davis", "email": "emma.davis@example.com", "city": "Seattle"},
    {"name": "Michael Miller", "email": "michael.miller@example.com", "city": "Boston"},
    {"name": "Olivia Garcia", "email": "olivia.garcia@example.com", "city": "Miami"},
    {"name": "William Jones", "email": "william.jones@example.com", "city": "Denver"},
    {"name": "Sophia Martinez", "email": "sophia.martinez@example.com", "city": "Austin"},
    {"name": "James Taylor", "email": "james.taylor@example.com", "city": "Portland"},
    {"name": "Ava Anderson", "email": "ava.anderson@example.com", "city": "San Francisco"},
    {"name": "Logan Thomas", "email": "logan.thomas@example.com", "city": "Dallas"},
    {"name": "Mia Hernandez", "email": "mia.hernandez@example.com", "city": "Atlanta"},
    {"name": "Benjamin Moore", "email": "benjamin.moore@example.com", "city": "San Diego"}
]

def generate_random_customer():
    """Generate a random customer with unique email"""
    first_names = ["Alex", "Casey", "Dakota", "Drew", "Eli", "Jamie", "Jordan", "Kendall", "Morgan", "Quinn", "Riley", "Taylor", "Sam", "Avery", "Parker"]
    last_names = ["Adams", "Bailey", "Carter", "Douglas", "Evans", "Foster", "Green", "Harris", "Irwin", "Jenkins", "Kelly", "Lewis", "Mills", "Nelson", "Owens"]
    cities = ["Nashville", "Minneapolis", "Pittsburgh", "Kansas City", "Cleveland", "Cincinnati", "Las Vegas", "Raleigh", "Sacramento", "Orlando", "St. Louis", "Tampa", "Charlotte", "Salt Lake City", "Oklahoma City"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f"{first_name} {last_name}"
    # Make email unique with timestamp
    timestamp = int(time.time() * 1000) % 1000000
    email = f"{first_name.lower()}.{last_name.lower()}{timestamp}@example.com"
    city = random.choice(cities)
    
    return {"name": name, "email": email, "city": city}

def generate_random_product():
    """Generate a random product with unique name"""
    categories = ["Electronics", "Accessories", "Office", "Audio", "Wearables", "Entertainment", "Storage", "Furniture", "Components", "Smart Home"]
    adjectives = ["Ultra", "Pro", "Deluxe", "Premium", "Compact", "Wireless", "Smart", "Advanced", "Essential", "Portable"]
    items = ["Charger", "Adapter", "Stand", "Hub", "Controller", "Dock", "Case", "Holder", "Light", "Fan"]
    
    category = random.choice(categories)
    name = f"{random.choice(adjectives)} {random.choice(items)} {int(time.time() * 1000) % 10000}"
    price = round(random.uniform(19.99, 599.99), 2)
    
    return {"name": name, "category": category, "price": price}

def connect_to_mariadb():
    """Connect to MariaDB database"""
    try:
        connection = mariadb.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database
        )
        print(f"Connected to MariaDB database: {args.database}")
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def setup_database(connection):
    """Create necessary tables if they don't exist"""
    cursor = connection.cursor()
    
    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100) NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        city VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    # Create order_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT,
        product_id INT,
        quantity INT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    
    connection.commit()
    print("Database setup complete")

def insert_sample_data(connection):
    """Insert sample data into products and customers tables"""
    cursor = connection.cursor()
    
    # Insert products
    for product in products:
        try:
            cursor.execute(
                "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
                (product["name"], product["category"], product["price"])
            )
        except Error as e:
            if "Duplicate entry" not in str(e):
                print(f"Error inserting product: {e}")
    
    # Insert customers
    for customer in customers:
        try:
            cursor.execute(
                "INSERT INTO customers (name, email, city) VALUES (?, ?, ?)",
                (customer["name"], customer["email"], customer["city"])
            )
        except Error as e:
            if "Duplicate entry" not in str(e):
                print(f"Error inserting customer: {e}")
    
    # Insert additional random products
    for _ in range(10):
        product = generate_random_product()
        try:
            cursor.execute(
                "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
                (product["name"], product["category"], product["price"])
            )
        except Error as e:
            if "Duplicate entry" not in str(e):
                print(f"Error inserting random product: {e}")
    
    # Insert additional random customers
    for _ in range(10):
        customer = generate_random_customer()
        try:
            cursor.execute(
                "INSERT INTO customers (name, email, city) VALUES (?, ?, ?)",
                (customer["name"], customer["email"], customer["city"])
            )
        except Error as e:
            if "Duplicate entry" not in str(e):
                print(f"Error inserting random customer: {e}")
    
    connection.commit()
    print("Sample data inserted")

def create_order(connection):
    """Create a random order"""
    cursor = connection.cursor()
    
    # Get a random customer
    cursor.execute("SELECT id FROM customers ORDER BY RAND() LIMIT 1")
    customer = cursor.fetchone()
    
    if not customer:
        print("No customers available")
        return
    
    customer_id = customer[0]
    
    # Create order
    order_date = datetime.datetime.now()
    total_amount = 0
    
    cursor.execute(
        "INSERT INTO orders (customer_id, order_date, total_amount) VALUES (?, ?, ?)",
        (customer_id, order_date, total_amount)
    )
    order_id = cursor.lastrowid
    
    # Add 1-5 random products to the order
    num_items = random.randint(1, 5)
    
    for _ in range(num_items):
        cursor.execute("SELECT id, price FROM products ORDER BY RAND() LIMIT 1")
        product = cursor.fetchone()
        
        if not product:
            continue
            
        product_id, price = product
        quantity = random.randint(1, 3)
        item_total = price * quantity
        
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, price)
        )
        
        total_amount += item_total
    
    # Update the order total
    cursor.execute(
        "UPDATE orders SET total_amount = ? WHERE id = ?",
        (total_amount, order_id)
    )
    
    connection.commit()
    print(f"Created order #{order_id} with {num_items} items, total: ${total_amount:.2f}")
    return order_id

def delete_order(connection):
    """Delete a random order"""
    cursor = connection.cursor()
    
    # Get a random order
    cursor.execute("SELECT id FROM orders ORDER BY RAND() LIMIT 1")
    order = cursor.fetchone()
    
    if not order:
        print("No orders available to delete")
        return
    
    order_id = order[0]
    
    # Delete order items first
    cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    
    # Then delete the order
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    
    connection.commit()
    print(f"Deleted order #{order_id}")

def delete_multiple_orders(connection):
    """Delete multiple random orders"""
    cursor = connection.cursor()
    
    # Try to delete between 2-5 orders at once
    num_to_delete = random.randint(2, 5)
    deleted_count = 0
    
    for _ in range(num_to_delete):
        # Get a random order
        cursor.execute("SELECT id FROM orders ORDER BY RAND() LIMIT 1")
        order = cursor.fetchone()
        
        if not order:
            print("No more orders available to delete")
            break
        
        order_id = order[0]
        
        # Delete order items first
        cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        
        # Then delete the order
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        deleted_count += 1
    
    connection.commit()
    print(f"Deleted {deleted_count} orders in bulk operation")
    return deleted_count

def run_complex_query(connection):
    """Run a complex query that would generate interesting metrics"""
    cursor = connection.cursor()
    
    query_type = random.randint(1, 10)
    
    if query_type == 1:
        # Sales by category
        print("Running query: Sales by category")
        cursor.execute("""
        SELECT p.category, SUM(oi.quantity * oi.price) as total_sales
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        JOIN orders o ON oi.order_id = o.id
        GROUP BY p.category
        ORDER BY total_sales DESC
        """)
    elif query_type == 2:
        # Top customers
        print("Running query: Top customers")
        cursor.execute("""
        SELECT c.name, c.city, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id
        ORDER BY total_spent DESC
        LIMIT 10
        """)
    elif query_type == 3:
        # Product performance
        print("Running query: Product performance")
        cursor.execute("""
        SELECT p.name, SUM(oi.quantity) as units_sold, SUM(oi.quantity * oi.price) as revenue
        FROM products p
        LEFT JOIN order_items oi ON p.id = oi.product_id
        GROUP BY p.id
        ORDER BY revenue DESC
        """)
    elif query_type == 4:
        # Orders in date range (last 30 days)
        print("Running query: Recent orders")
        cursor.execute("""
        SELECT DATE(o.order_date) as order_day, COUNT(o.id) as order_count, SUM(o.total_amount) as daily_sales
        FROM orders o
        WHERE o.order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY order_day
        ORDER BY order_day
        """)
    elif query_type == 5:
        # Inventory turnover
        print("Running query: Inventory analysis")
        cursor.execute("""
        SELECT p.category, 
               AVG(oi.quantity) as avg_quantity_per_order,
               COUNT(DISTINCT o.id) as order_count
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        JOIN orders o ON oi.order_id = o.id
        GROUP BY p.category
        """)
    elif query_type == 6:
        # City-based sales analysis
        print("Running query: Sales by city")
        cursor.execute("""
        SELECT c.city, COUNT(o.id) as order_count, SUM(o.total_amount) as total_sales
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        GROUP BY c.city
        ORDER BY total_sales DESC
        """)
    elif query_type == 7:
        # Price range distribution
        print("Running query: Price range distribution")
        cursor.execute("""
        SELECT 
            CASE 
                WHEN price < 50 THEN 'Under $50'
                WHEN price >= 50 AND price < 100 THEN '$50-$99'
                WHEN price >= 100 AND price < 200 THEN '$100-$199'
                WHEN price >= 200 AND price < 500 THEN '$200-$499'
                ELSE '$500+'
            END as price_range,
            COUNT(*) as product_count,
            AVG(price) as avg_price
        FROM products
        GROUP BY price_range
        ORDER BY MIN(price)
        """)
    elif query_type == 8:
        # Customer purchase frequency
        print("Running query: Customer purchase frequency")
        cursor.execute("""
        SELECT 
            c.id, c.name,
            COUNT(o.id) as order_count,
            MIN(o.order_date) as first_purchase,
            MAX(o.order_date) as last_purchase,
            DATEDIFF(MAX(o.order_date), MIN(o.order_date)) as days_between_purchases
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id
        HAVING COUNT(o.id) > 1
        ORDER BY order_count DESC
        """)
    elif query_type == 9:
      # Complex subquery for product popularity
      print("Running query: Product popularity")
      cursor.execute("""
      SELECT p.name, p.category, 
          SUM(oi.quantity) as total_qty,
          (SELECT AVG(sub_oi.quantity)
           FROM order_items sub_oi
           JOIN products sub_p ON sub_oi.product_id = sub_p.id
           WHERE sub_p.category = p.category) as category_avg_qty
      FROM products p
      JOIN order_items oi ON p.id = oi.product_id
      GROUP BY p.id
      HAVING SUM(oi.quantity) > (
          SELECT AVG(sub_oi.quantity)
          FROM order_items sub_oi
          JOIN products sub_p ON sub_oi.product_id = sub_p.id
          WHERE sub_p.category = p.category
      )
      ORDER BY (SUM(oi.quantity) / (
          SELECT AVG(sub_oi.quantity)
          FROM order_items sub_oi
          JOIN products sub_p ON sub_oi.product_id = sub_p.id
          WHERE sub_p.category = p.category
      )) DESC
      """) 
    else:
        # Heavy join with window function
        print("Running query: Monthly sales trends")
        cursor.execute("""
        WITH monthly_sales AS (
            SELECT 
                DATE_FORMAT(o.order_date, '%Y-%m') as month,
                p.category,
                SUM(oi.quantity * oi.price) as monthly_revenue
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            GROUP BY month, p.category
        )
        SELECT 
            ms.month,
            ms.category,
            ms.monthly_revenue,
            LAG(ms.monthly_revenue) OVER (PARTITION BY ms.category ORDER BY ms.month) as prev_month_revenue,
            CASE 
                WHEN LAG(ms.monthly_revenue) OVER (PARTITION BY ms.category ORDER BY ms.month) IS NULL THEN 0
                ELSE (ms.monthly_revenue - LAG(ms.monthly_revenue) OVER (PARTITION BY ms.category ORDER BY ms.month)) / 
                     LAG(ms.monthly_revenue) OVER (PARTITION BY ms.category ORDER BY ms.month) * 100
            END as growth_percent
        FROM monthly_sales ms
        ORDER BY ms.month, ms.monthly_revenue DESC
        """)
    
    # Fetch results (not used, but simulates real application behavior)
    results = cursor.fetchall()
    print(f"Query returned {len(results)} rows")

def add_random_product(connection):
    """Add a random product to the database"""
    cursor = connection.cursor()
    product = generate_random_product()
    
    try:
        cursor.execute(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            (product["name"], product["category"], product["price"])
        )
        connection.commit()
        print(f"Added new product: {product['name']} ({product['category']}) - ${product['price']}")
    except Error as e:
        print(f"Error adding product: {e}")

def add_random_customer(connection):
    """Add a random customer to the database"""
    cursor = connection.cursor()
    customer = generate_random_customer()
    
    try:
        cursor.execute(
            "INSERT INTO customers (name, email, city) VALUES (?, ?, ?)",
            (customer["name"], customer["email"], customer["city"])
        )
        connection.commit()
        print(f"Added new customer: {customer['name']} from {customer['city']}")
    except Error as e:
        print(f"Error adding customer: {e}")

def update_random_price(connection):
    """Update a random product's price"""
    cursor = connection.cursor()
    
    cursor.execute("SELECT id, name, price FROM products ORDER BY RAND() LIMIT 1")
    product = cursor.fetchone()
    
    if not product:
        print("No products available to update")
        return
    
    product_id, product_name, old_price = product
    
    # Random price adjustment between -20% and +20%
    adjustment = random.uniform(0.8, 1.2)
    # Convert Decimal to float before multiplication
    new_price = round(float(old_price) * adjustment, 2)
    
    cursor.execute(
        "UPDATE products SET price = ? WHERE id = ?",
        (new_price, product_id)
    )
    connection.commit()
    
    print(f"Updated price for {product_name}: ${old_price} -> ${new_price}")

def update_multiple_prices(connection):
    """Update prices for multiple products"""
    cursor = connection.cursor()
    
    # Try to update between 3-8 products at once
    num_to_update = random.randint(3, 8)
    updated_count = 0
    
    cursor.execute("SELECT id, name, price FROM products ORDER BY RAND() LIMIT ?", (num_to_update,))
    products = cursor.fetchall()
    
    if not products:
        print("No products available to update")
        return 0
    
    for product in products:
        product_id, product_name, old_price = product
        
        # Random price adjustment between -25% and +25%
        adjustment = random.uniform(0.75, 1.25)
        # Convert Decimal to float before multiplication
        new_price = round(float(old_price) * adjustment, 2)
        
        cursor.execute(
            "UPDATE products SET price = ? WHERE id = ?",
            (new_price, product_id)
        )
        updated_count += 1
        print(f"Updated price for {product_name}: ${old_price} -> ${new_price}")
    
    connection.commit()
    print(f"Updated prices for {updated_count} products in bulk operation")
    return updated_count

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the demo"""
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    connection = connect_to_mariadb()
    if not connection:
        return
    
    try:
        # Setup database and initial data
        setup_database(connection)
        insert_sample_data(connection)
        
        operation_count = 0
        infinite_mode = args.iterations == 0
        
        if infinite_mode:
            print(f"Starting infinite operations with {args.delay}s delay between them...")
            print("Press Ctrl+C to stop the script")
        else:
            print(f"Starting {args.iterations} operations with {args.delay}s delay between them...")
        
        # Run mixed operations
        while infinite_mode or operation_count < args.iterations:
            operation_count += 1
            
            # More varied random distribution with higher update/delete frequency
            operation = random.randint(1, 100)
            
            if infinite_mode:
                print(f"\nOperation #{operation_count}")
            else:
                print(f"\nOperation {operation_count}/{args.iterations}")
            
            if operation <= 25:  # 25% chance
                create_order(connection)
            elif operation <= 45:  # 20% chance
                delete_order(connection)
            elif operation <= 55:  # 10% chance
                delete_multiple_orders(connection)
            elif operation <= 70:  # 15% chance
                run_complex_query(connection)
            elif operation <= 80:  # 10% chance
                add_random_product(connection)
            elif operation <= 85:  # 5% chance
                add_random_customer(connection)
            elif operation <= 90:  # 5% chance
                update_random_price(connection)
            else:  # 10% chance
                update_multiple_prices(connection)
            
            # Randomize delay slightly to make metrics more interesting
            actual_delay = args.delay * random.uniform(0.8, 1.2)
            time.sleep(actual_delay)
        
        print("\nDemo operations completed")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if not infinite_mode and connection.is_connected():
            connection.close()
            print("MariaDB connection closed")

if __name__ == "__main__":
    main()
