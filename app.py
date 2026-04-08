"""
Flask Backend - E-Commerce Analytics Dashboard
Endpoints: /api/kpis, /api/sales_by_month, /api/sales_by_category,
           /api/top_products, /api/orders_by_quarter,
           /api/customer_stats, /api/generate_report
"""
import os, io, csv
from datetime import datetime
from flask import Flask, jsonify, request, send_file, render_template

# ── path setup ────────────────────────────────────────────────────


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.csv")

import sys
sys.path.insert(0, BASE_DIR)
from analysis import (
    load_and_clean, compute_kpis, sales_by_month,
    sales_by_category, top_products, orders_by_quarter, customer_stats,
    generate_charts
)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# ── Load & cache data once on startup ─────────────────────────────
print("Loading dataset...")
try:
    _df_full = load_and_clean()
    generate_charts(_df_full)
    print("Dataset loaded successfully")
except Exception as e:
    print("ERROR LOADING DATASET:", e)
    _df_full = None
generate_charts(_df_full)
print("Ready.")

def _filtered_df(start_date=None, end_date=None):
    if _df_full is None:
        return pd.DataFrame()
def _filtered_df(start_date=None, end_date=None):
    df = _df_full.copy()
    if start_date:
        df = df[df["order_date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["order_date"] <= pd.to_datetime(end_date)]
    return df


import pandas as pd  # needed for _filtered_df


# ── CORS helper ───────────────────────────────────────────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# ── Serve frontend ────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── API Endpoints ─────────────────────────────────────────────────
@app.route("/api/kpis")
def api_kpis():
    start = request.args.get("start_date")
    end   = request.args.get("end_date")
    df = _filtered_df(start, end)
    return jsonify(compute_kpis(df))


@app.route("/api/sales_by_month")
def api_sales_by_month():
    start = request.args.get("start_date")
    end   = request.args.get("end_date")
    df = _filtered_df(start, end)
    return jsonify(sales_by_month(df))


@app.route("/api/sales_by_category")
def api_sales_by_category():
    start = request.args.get("start_date")
    end   = request.args.get("end_date")
    df = _filtered_df(start, end)
    return jsonify(sales_by_category(df))


@app.route("/api/top_products")
def api_top_products():
    n = int(request.args.get("n", 10))
    start = request.args.get("start_date")
    end   = request.args.get("end_date")
    df = _filtered_df(start, end)
    return jsonify(top_products(df, n))


@app.route("/api/orders_by_quarter")
def api_orders_by_quarter():
    df = _filtered_df()
    return jsonify(orders_by_quarter(df))


@app.route("/api/customer_stats")
def api_customer_stats():
    df = _filtered_df()
    return jsonify(customer_stats(df))


@app.route("/api/generate_report")
def api_generate_report():
    start = request.args.get("start_date")
    end   = request.args.get("end_date")
    fmt   = request.args.get("format", "csv").lower()

    df = _filtered_df(start, end)

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["E-Commerce Sales Report"])
        writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        if start or end:
            writer.writerow([f"Period: {start or 'All'} to {end or 'All'}"])
        writer.writerow([])

        # KPIs section
        kpis = compute_kpis(df)
        writer.writerow(["--- KEY PERFORMANCE INDICATORS ---"])
        for k, v in kpis.items():
            writer.writerow([k.replace("_", " ").title(), v])
        writer.writerow([])

        # Monthly sales
        writer.writerow(["--- MONTHLY REVENUE ---"])
        writer.writerow(["Month", "Revenue ($)"])
        for row in sales_by_month(df):
            writer.writerow([row["month"], row["revenue"]])
        writer.writerow([])

        # Category breakdown
        writer.writerow(["--- REVENUE BY CATEGORY ---"])
        writer.writerow(["Category", "Revenue ($)"])
        for row in sales_by_category(df):
            writer.writerow([row["category"], row["revenue"]])
        writer.writerow([])

        # Top products
        writer.writerow(["--- TOP PRODUCTS ---"])
        writer.writerow(["Product", "Category", "Revenue ($)", "Orders"])
        for row in top_products(df, 10):
            writer.writerow([row["product_name"], row["product_category"],
                             row["total_revenue"], row["total_orders"]])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"ecommerce_report_{datetime.now().strftime('%Y%m%d')}.csv",
        )

    # ── Simple HTML/text report as fallback ───────────────────────
    kpis = compute_kpis(df)
    lines = [
        "E-COMMERCE ANALYTICS REPORT",
        "=" * 40,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "KEY METRICS",
        f"  Total Revenue     : ${kpis['total_revenue']:,.2f}",
        f"  Total Orders      : {kpis['total_orders']:,}",
        f"  Avg Order Value   : ${kpis['avg_order_value']:,.2f}",
        f"  Unique Customers  : {kpis['unique_customers']:,}",
        f"  Units Sold        : {kpis['total_units_sold']:,}",
    ]
    return send_file(
        io.BytesIO("\n".join(lines).encode()),
        mimetype="text/plain",
        as_attachment=True,
        download_name="report.txt",
    )


import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
