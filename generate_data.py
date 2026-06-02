import pandas as pd
import random
import duckdb
import time
from datetime import datetime

random.seed()  # No fixed seed = truly random each run

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

def generate_order(order_num):
    region = random.choice(regions)
    state = random.choice(states[region])
    category, sub_category, product, base_price = random.choice(products)
    segment = random.choice(segments)
    ship_mode = random.choice(ship_modes)
    quantity = random.randint(1, 10)
    discount = random.choice([0, 0.1, 0.2, 0.3])
    sales = round(base_price * quantity * (1 - discount), 2)
    profit = round(sales * random.uniform(0.05, 0.35), 2)

    return {
        "Order_ID": f"ORD-{order_num}",
        "Order_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # real timestamp!
        "Ship_Mode": ship_mode,
        "Segment": segment,
        "Region": region,
        "State": state,
        "Category": category,
        "Sub_Category": sub_category,
        "Product_Name": product,
        "Sales": sales,
        "Quantity": quantity,
        "Discount": discount,
        "Profit": profit
    }

def setup_database():
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
    con.close()
    print("Database ready!")

def stream_orders(interval_seconds=2):
    setup_database()
    order_num = 10000
    print(f"Streaming live orders every {interval_seconds} seconds... Press Ctrl+C to stop")
    print("-" * 60)

    while True:
        order = generate_order(order_num)
        
        # Insert into DuckDB
        con = duckdb.connect("data/sales.db")
        con.execute("""
            INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, list(order.values()))
        
        # Show live count
        count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        con.close()

        print(f"[{order['Order_Date']}] New order: {order['Order_ID']} | "
              f"{order['Product_Name']} | ${order['Sales']} | "
              f"Region: {order['Region']} | Total records: {count}")

        order_num += 1
        time.sleep(interval_seconds)

if __name__ == "__main__":
    stream_orders(interval_seconds=2)  # new order every 2 seconds