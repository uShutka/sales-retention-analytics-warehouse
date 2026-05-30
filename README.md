# Sales & Retention Analytics Warehouse

End-to-end sales analytics warehouse with raw data ingestion, cleaning, SQL-style staging, analytical marts, retention analytics, LTV, RFM segmentation, forecasting, FastAPI endpoints, and a Streamlit dashboard.

## Project Overview

This project demonstrates how raw e-commerce data can be turned into a reliable analytics layer for business decisions. It uses a warehouse-style structure: raw tables, cleaning logic, staging SQL examples, mart builders, KPI services, API endpoints, dashboard views, tests, Docker, and CI.

## Business Problem

Many e-commerce teams look only at revenue charts. That hides the real questions: whether margin is healthy, which channels bring valuable customers, whether repeat purchase happens quickly enough, and which customers/products deserve attention.

## Solution

The project loads raw commerce tables, validates and cleans them, builds reusable marts, calculates business KPIs, exposes the metrics through FastAPI, and visualizes the results in Streamlit.

## Architecture

```text
Raw CSV Tables
-> Cleaning & Normalization
-> Staging SQL Layer
-> Analytical Marts
-> KPI / Forecast / Recommendation Services
-> FastAPI + Streamlit Dashboard
```

## Features

- Raw tables: `orders`, `customers`, `products`, `payments`, `refunds`, `marketing_spend`
- Staging SQL scripts and Python mart builders
- Marts: `mart_daily_revenue`, `mart_customer_ltv`, `mart_cohort_retention`, `mart_product_profitability`, `mart_marketing_roi`, `mart_rfm_segments`
- KPI calculations: revenue, gross profit, gross margin, AOV, repeat purchase rate, refund rate, LTV, CAC, ROAS
- Cohort retention matrix
- RFM customer segmentation
- Simple revenue forecast
- Business recommendation engine
- REST API and dashboard
- Dockerized setup and GitHub Actions CI

## Tech Stack

Python, pandas, SQL, PostgreSQL-ready SQL scripts, FastAPI, Streamlit, Plotly, Docker, pytest, ruff, GitHub Actions.

## Database Schema

Raw layer:

- `orders(order_id, customer_id, product_id, order_date, quantity, unit_price, discount_pct, status)`
- `customers(customer_id, signup_date, acquisition_channel, country)`
- `products(product_id, sku, name, category, brand, unit_cost)`
- `payments(payment_id, order_id, payment_date, amount, currency, payment_method, status)`
- `refunds(refund_id, order_id, refund_date, amount, reason)`
- `marketing_spend(spend_date, channel, campaign, spend)`

Analytical marts:

- `mart_daily_revenue`
- `mart_customer_ltv`
- `mart_cohort_retention`
- `mart_product_profitability`
- `mart_marketing_roi`
- `mart_rfm_segments`

## Data Pipeline

1. Load raw CSV files from `data/raw`.
2. Normalize dates, numeric fields, statuses, countries, and acquisition channels.
3. Build order-level facts with revenue, net revenue, COGS, gross profit, and refunds.
4. Build reusable marts for revenue, retention, LTV, product profitability, marketing ROI, and RFM.
5. Serve analytics through API endpoints and Streamlit dashboard.

## API Endpoints

- `GET /health`
- `GET /analytics/summary`
- `GET /analytics/monthly-growth`
- `GET /analytics/business-findings`
- `GET /analytics/recommendations`
- `GET /analytics/forecast`
- `GET /marts/daily-revenue`
- `GET /marts/customer-ltv`
- `GET /marts/cohort-retention`
- `GET /marts/product-profitability`
- `GET /marts/marketing-roi`
- `GET /marts/rfm-segments`

## Dashboard Screenshots

Screenshots are stored in `docs/screenshots/`:

- Revenue dashboard
- Cohort retention heatmap
- RFM segmentation
- LTV and product profitability view
- SQL data model
- Business conclusions page

## Analytics Results

Example conclusions from the included demo dataset:

- Revenue increased in the latest month while margin risk remains visible in discount-heavy products.
- Paid search creates volume, but high ROAS channels should be protected before scaling spend.
- The second purchase window should be targeted within 14-21 days; after day 30 repeat probability drops.
- Top 20% of customers generate a disproportionate share of total revenue.
- Low-margin products should be reviewed before additional promotions are launched.

## How to Run

```bash
docker compose up --build
```

Open:

- API docs: `http://localhost:8001/docs`
- Dashboard: `http://localhost:8502`

Local development:

```bash
python -m pip install -e .
uvicorn sales_retention_analytics_warehouse.api.main:app --reload
streamlit run dashboard/streamlit_app.py
```

## Tests

```bash
pytest
ruff check .
```

The suite covers cleaning, mart generation, KPI calculations, cohort retention, RFM segmentation, forecasting, recommendations, and API endpoints.

## Engineering Notes

This is structured as a production-style analytics case rather than a notebook. Business logic lives in testable modules, SQL examples document the intended warehouse layers, and the API/dashboard consume the same analytical services.

## Known Limitations

- Demo CSV data is intentionally compact for portfolio review.
- The SQL scripts are warehouse-model examples; the local demo uses pandas for fast reproducibility.
- Forecasting uses a simple moving average, not a full statistical model.
- Attribution is based on acquisition channel, not multi-touch attribution.

## Future Improvements

- Add dbt project scaffolding and warehouse materialization.
- Add Metabase dashboards on top of PostgreSQL.
- Add Airflow or Prefect scheduled runs.
- Add advanced retention prediction and churn scoring.
- Export board-ready PDF/Excel analytics packs.
