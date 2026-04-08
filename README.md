# EcomInsight — E-Commerce Analytics Dashboard

A full-stack analytics dashboard for e-commerce sales data.

## Project Structure
```
ecommerce_dashboard/
├── data/
│   ├── generate_data.py        # Synthetic dataset generator
│   └── ecommerce_data.csv      # Generated dataset (1200 rows)
├── backend/
│   ├── app.py                  # Flask server + all API endpoints
│   └── analysis.py             # Data cleaning, KPI logic, chart generation
├── frontend/
│   ├── templates/index.html    # Main dashboard HTML
│   └── static/
│       ├── css/style.css       # Dashboard styles
│       ├── js/dashboard.js     # Chart.js visualizations & API calls
│       └── charts/             # Static chart PNGs (for reports)
├── notebooks/
│   └── EDA_Analysis.ipynb      # Jupyter EDA notebook
├── requirements.txt
└── README.md
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate the dataset (if not already present)
```bash
python data/generate_data.py
```

### 3. Start the Flask server
```bash
python backend/app.py
```

### 4. Open the dashboard
Visit: http://localhost:5000

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/kpis` | GET | Total revenue, orders, AOV, customers, units |
| `/api/sales_by_month` | GET | Monthly revenue series |
| `/api/sales_by_category` | GET | Revenue breakdown by product category |
| `/api/top_products` | GET | Top N products by revenue (param: `n`) |
| `/api/orders_by_quarter` | GET | Quarterly revenue & order count |
| `/api/customer_stats` | GET | Customer spend & repeat rate stats |
| `/api/generate_report` | GET | Download CSV or TXT report |

All endpoints accept optional `start_date` and `end_date` query parameters (YYYY-MM-DD).

## Technologies
- **Backend:** Python, Flask, Pandas
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Analysis:** Pandas, NumPy, Matplotlib, Seaborn
- **Notebook:** Jupyter
- **Version Control:** Git
