import os
import duckdb
import random
from datetime import datetime, timedelta

def init_database():
    """Create and seed the database if it doesn't exist"""
    os.makedirs("data", exist_ok=True)
    
    if os.path.exists("data/sales.db"):
        print("Database already exists, skipping seed")
        return
    
    print("Creating and seeding database...")
    
    products = [
        ("Furniture", "Chairs", "Office Chair Pro", 299.99),
        ("Furniture", "Tables", "Executive Desk", 499.99),
        ("Furniture", "Bookcases", "Wood Bookcase", 199.99),
        ("Technology", "Phones", "iPhone Case", 29.99),
        ("Technology", "Laptops", "Laptop Stand", 79.99),
        ("Technology", "Accessories", "USB Hub", 39.99),
        ("Technology", "Accessories", "Wireless Mouse", 49.99),
        ("Office Supplies", "Paper", "Copy Paper Box", 19.99),
        ("Office Supplies", "Binders", "3-Ring Binder", 9.99),
        ("Office Supplies", "Pens", "Pen Set 12pk", 7.99),
        ("Office Supplies", "Labels", "Label Maker", 24.99),
        ("Office Supplies", "Storage", "File Cabinet", 149.99),
    ]

    regions = ["East", "West", "Central", "South"]
    states = {
        "East": ["New York", "Pennsylvania", "New Jersey", "Massachusetts"],
        "West": ["California", "Washington", "Oregon", "Nevada"],
        "Central": ["Texas", "Illinois", "Ohio", "Michigan"],
        "South": ["Florida", "Georgia", "North Carolina", "Virginia"]
    }
    segments = ["Consumer", "Corporate", "Home Office"]
    ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

    con = duckdb.connect("data/sales.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            Order_ID VARCHAR,
            Order_Date TIMESTAMP,
            Ship_Mode VARCHAR,
            Segment VARCHAR,
            Region VARCHAR,
            State VARCHAR,
            Category VARCHAR,
            Sub_Category VARCHAR,
            Product_Name VARCHAR,
            Sales DOUBLE,
            Quantity INTEGER,
            Discount DOUBLE,
            Profit DOUBLE
        )
    """)

    random.seed(42)
    start_date = datetime(2024, 1, 1)
    
    for i in range(5000):
        region = random.choice(regions)
        state = random.choice(states[region])
        category, sub_category, product, base_price = random.choice(products)
        segment = random.choice(segments)
        ship_mode = random.choice(ship_modes)
        quantity = random.randint(1, 10)
        discount = random.choice([0, 0.1, 0.2, 0.3])
        sales = round(base_price * quantity * (1 - discount), 2)
        profit = round(sales * random.uniform(0.05, 0.35), 2)
        order_date = start_date + timedelta(days=random.randint(0, 365))

        con.execute("""
            INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            f"ORD-{10000+i}", order_date, ship_mode, segment,
            region, state, category, sub_category, product,
            sales, quantity, discount, profit
        ])

    con.close()
    print(f"Database seeded with 5000 rows!")

if __name__ == "__main__":
    init_database()