"""
Generate synthetic e-commerce dataset with 1200 transactions.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

# Configuration
NUM_RECORDS = 1200
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

CATEGORIES = {
    "Electronics": {"price_range": (50, 1500), "weight": 0.20},
    "Clothing": {"price_range": (15, 200), "weight": 0.25},
    "Home & Garden": {"price_range": (20, 500), "weight": 0.15},
    "Books": {"price_range": (8, 60), "weight": 0.12},
    "Sports & Outdoors": {"price_range": (25, 400), "weight": 0.10},
    "Beauty & Personal Care": {"price_range": (10, 150), "weight": 0.10},
    "Toys & Games": {"price_range": (12, 120), "weight": 0.08},
}

PRODUCTS = {
    "Electronics": ["Laptop", "Smartphone", "Headphones", "Tablet", "Smartwatch", "Camera", "Speaker"],
    "Clothing": ["T-Shirt", "Jeans", "Dress", "Jacket", "Sneakers", "Hoodie", "Shorts"],
    "Home & Garden": ["Sofa", "Desk Lamp", "Plant Pot", "Curtains", "Cookware Set", "Bedding", "Wall Art"],
    "Books": ["Fiction Novel", "Self-Help Book", "Cookbook", "Science Book", "Biography", "Textbook"],
    "Sports & Outdoors": ["Yoga Mat", "Dumbbells", "Bicycle Helmet", "Running Shoes", "Tent", "Backpack"],
    "Beauty & Personal Care": ["Face Cream", "Shampoo", "Perfume", "Lipstick", "Sunscreen", "Vitamins"],
    "Toys & Games": ["Board Game", "Action Figure", "LEGO Set", "Puzzle", "Remote Car", "Doll"],
}

def generate_dataset():
    categories = list(CATEGORIES.keys())
    weights = [CATEGORIES[c]["weight"] for c in categories]

    records = []
    for i in range(1, NUM_RECORDS + 1):
        order_id = f"ORD-{i:05d}"
        customer_id = f"CUST-{random.randint(1, 400):04d}"
        category = random.choices(categories, weights=weights)[0]
        product_name = random.choice(PRODUCTS[category])
        product_id = f"PROD-{abs(hash(product_name)) % 9000 + 1000}"

        days_range = (END_DATE - START_DATE).days
        # Add seasonal trend (higher sales in Q4)
        month_weights = [0.06, 0.06, 0.07, 0.07, 0.08, 0.08, 0.08, 0.09, 0.09, 0.10, 0.11, 0.11]
        month = random.choices(range(1, 13), weights=month_weights)[0]
        day = random.randint(1, 28)
        year = random.choice([2023, 2024])
        order_date = datetime(year, month, day)

        price_min, price_max = CATEGORIES[category]["price_range"]
        unit_price = round(random.uniform(price_min, price_max), 2)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.5, 0.25, 0.12, 0.08, 0.05])[0]

        # Introduce ~3% missing values for cleaning demo
        if random.random() < 0.03:
            unit_price = None
        if random.random() < 0.02:
            quantity = None

        total_price = round(unit_price * quantity, 2) if unit_price and quantity else None

        records.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "product_id": product_id,
            "product_name": product_name,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "product_category": category,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
        })

    df = pd.DataFrame(records)
    output_path = os.path.join(os.path.dirname(__file__), "ecommerce_data.csv")
    df.to_csv(output_path, index=False)
    print(f"Dataset generated: {len(df)} records saved to {output_path}")
    print(df.head())
    print(df.describe())
    return df

if __name__ == "__main__":
    generate_dataset()
