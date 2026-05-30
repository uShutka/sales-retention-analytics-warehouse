import math
from typing import Any

import pandas as pd
from fastapi import FastAPI

from sales_retention_analytics_warehouse.cleaning import clean_all
from sales_retention_analytics_warehouse.forecasting import forecast_daily_revenue
from sales_retention_analytics_warehouse.loaders import load_raw_tables
from sales_retention_analytics_warehouse.marts import build_marts
from sales_retention_analytics_warehouse.metrics import business_findings, kpi_summary, monthly_growth
from sales_retention_analytics_warehouse.recommendations import build_recommendations

app = FastAPI(title="Sales & Retention Analytics Warehouse", version="0.1.0")


def _warehouse() -> dict[str, pd.DataFrame]:
    return build_marts(clean_all(load_raw_tables()))


def _clean_value(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "isoformat") and value.__class__.__name__ == "date":
        return value.isoformat()
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    safe = frame.copy()
    for column in safe.columns:
        safe[column] = safe[column].map(_clean_value)
    return safe.to_dict(orient="records")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sales-retention-analytics-warehouse"}


@app.get("/analytics/summary")
def analytics_summary() -> dict[str, float]:
    return kpi_summary(_warehouse())


@app.get("/analytics/monthly-growth")
def analytics_monthly_growth() -> list[dict[str, Any]]:
    return _records(monthly_growth(_warehouse()))


@app.get("/analytics/recommendations")
def analytics_recommendations() -> list[dict[str, str]]:
    return build_recommendations(_warehouse())


@app.get("/analytics/business-findings")
def analytics_business_findings() -> list[str]:
    return business_findings(_warehouse())


@app.get("/analytics/forecast")
def analytics_forecast() -> list[dict[str, Any]]:
    marts = _warehouse()
    return _records(forecast_daily_revenue(marts["mart_daily_revenue"]))


@app.get("/marts/daily-revenue")
def daily_revenue() -> list[dict[str, Any]]:
    return _records(_warehouse()["mart_daily_revenue"])


@app.get("/marts/customer-ltv")
def customer_ltv() -> list[dict[str, Any]]:
    return _records(_warehouse()["mart_customer_ltv"])


@app.get("/marts/cohort-retention")
def cohort_retention() -> list[dict[str, Any]]:
    return _records(_warehouse()["mart_cohort_retention"])


@app.get("/marts/product-profitability")
def product_profitability() -> list[dict[str, Any]]:
    return _records(_warehouse()["mart_product_profitability"])


@app.get("/marts/marketing-roi")
def marketing_roi() -> list[dict[str, Any]]:
    return _records(_warehouse()["mart_marketing_roi"])


@app.get("/marts/rfm-segments")
def rfm_segments() -> list[dict[str, Any]]:
    return _records(_warehouse()["mart_rfm_segments"])
