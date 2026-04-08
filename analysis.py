
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/ecommerce_data.csv")
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "../frontend/static/charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Color palette ──────────────────────────────────────────────────
PALETTE = ["#1e3a5f", "#2d6a9f", "#4a90d9", "#7ab8f5", "#a8d1f7",
           "#d4e8fb", "#f0c040", "#e87040"]
sns.set_theme(style="darkgrid", palette=PALETTE)

def load_and_clean():
    DATA_PATH = "C:/Users/HomePC/Downloads/ecommercedashboards/data.csv"
    df = pd.read_csv(DATA_PATH)
    print(f"Raw shape: {df.shape}")
    print(f"Missing values:\n{df.isnull().sum()}\n")

    # 1. Convert order_date to datetime
    df["order_date"] = pd.to_datetime(df["order_date"])

    # 2. Fill missing quantity with median
    df["quantity"] = df["quantity"].fillna(df["quantity"].median())

    # 3. Fill missing unit_price with category median
    df["unit_price"] = df.groupby("product_category")["unit_price"] \
                         .transform(lambda x: x.fillna(x.median()))

    # 4. Recalculate total_price where missing
    df["total_price"] = df["total_price"].fillna(
        df["unit_price"] * df["quantity"]
    )

    # 5. Standardize category names (strip whitespace)
    df["product_category"] = df["product_category"].str.strip().str.title()

    # 6. Extract time features
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["month_name"] = df["order_date"].dt.strftime("%b")
    df["quarter"] = df["order_date"].dt.quarter
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)

    print(f"Clean shape: {df.shape}")
    print(f"Missing after cleaning:\n{df.isnull().sum()}\n")
    return df


def compute_kpis(df):
    kpis = {
        "total_revenue": round(df["total_price"].sum(), 2),
        "total_orders": int(df["order_id"].nunique()),
        "avg_order_value": round(df["total_price"].mean(), 2),
        "unique_customers": int(df["customer_id"].nunique()),
        "total_units_sold": int(df["quantity"].sum()),
    }
    print("KPIs:", kpis)
    return kpis


def sales_by_month(df):
    monthly = (
        df.groupby("year_month")["total_price"]
        .sum()
        .reset_index()
        .rename(columns={"year_month": "month", "total_price": "revenue"})
        .sort_values("month")
    )
    monthly["revenue"] = monthly["revenue"].round(2)
    return monthly.to_dict(orient="records")


def sales_by_category(df):
    cat = (
        df.groupby("product_category")["total_price"]
        .sum()
        .reset_index()
        .rename(columns={"product_category": "category", "total_price": "revenue"})
        .sort_values("revenue", ascending=False)
    )
    cat["revenue"] = cat["revenue"].round(2)
    return cat.to_dict(orient="records")


def top_products(df, n=10):
    top = (
        df.groupby(["product_name", "product_category"])
        .agg(total_revenue=("total_price", "sum"), total_orders=("order_id", "count"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(n)
    )
    top["total_revenue"] = top["total_revenue"].round(2)
    return top.to_dict(orient="records")


def orders_by_quarter(df):
    q = (
        df.groupby(["year", "quarter"])
        .agg(orders=("order_id", "count"), revenue=("total_price", "sum"))
        .reset_index()
    )
    q["label"] = "Q" + q["quarter"].astype(str) + " " + q["year"].astype(str)
    q["revenue"] = q["revenue"].round(2)
    return q[["label", "orders", "revenue"]].to_dict(orient="records")


def customer_stats(df):
    cust = df.groupby("customer_id").agg(
        total_spent=("total_price", "sum"),
        order_count=("order_id", "count")
    ).reset_index()
    return {
        "avg_spend_per_customer": round(cust["total_spent"].mean(), 2),
        "max_spend": round(cust["total_spent"].max(), 2),
        "repeat_customers": int((cust["order_count"] > 1).sum()),
        "one_time_customers": int((cust["order_count"] == 1).sum()),
    }


# ── Static chart generation for the report ────────────────────────
def generate_charts(df):
    # 1. Monthly Revenue Trend
    monthly = df.groupby("year_month")["total_price"].sum().sort_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    monthly.plot(ax=ax, color="#4a90d9", linewidth=2, marker="o", markersize=4)
    ax.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue ($)")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    fig.savefig(f"{CHARTS_DIR}/monthly_revenue.png", dpi=100)
    plt.close(fig)

    # 2. Sales by Category
    cat = df.groupby("product_category")["total_price"].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    cat.plot(kind="barh", ax=ax, color=PALETTE[:len(cat)])
    ax.set_title("Revenue by Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Revenue ($)")
    plt.tight_layout()
    fig.savefig(f"{CHARTS_DIR}/category_revenue.png", dpi=100)
    plt.close(fig)

    # 3. Top 10 Products
    top = df.groupby("product_name")["total_price"].sum().nlargest(10).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    top.plot(kind="barh", ax=ax, color="#2d6a9f")
    ax.set_title("Top 10 Products by Revenue", fontsize=14, fontweight="bold")
    ax.set_xlabel("Revenue ($)")
    plt.tight_layout()
    fig.savefig(f"{CHARTS_DIR}/top_products.png", dpi=100)
    plt.close(fig)

    print("Charts saved.")


if __name__ == "__main__":
    df = load_and_clean()
    print("\nKPIs:", compute_kpis(df))
    generate_charts(df)
    print("\nTop Products:", top_products(df, 5))
