from sales_retention_analytics_warehouse.cleaning import clean_all
from sales_retention_analytics_warehouse.core import run_warehouse
from sales_retention_analytics_warehouse.forecasting import forecast_daily_revenue
from sales_retention_analytics_warehouse.loaders import load_raw_tables
from sales_retention_analytics_warehouse.marts import build_marts, build_order_lines
from sales_retention_analytics_warehouse.metrics import (
    business_findings,
    cohort_matrix,
    kpi_summary,
    monthly_growth,
    rfm_segment_summary,
)
from sales_retention_analytics_warehouse.recommendations import build_recommendations


def _marts():
    return build_marts(clean_all(load_raw_tables()))


def test_order_lines_include_profit_fields():
    lines = build_order_lines(clean_all(load_raw_tables()))
    assert {"gross_revenue", "gross_profit", "net_revenue", "refund_amount"}.issubset(lines.columns)
    assert lines["net_revenue"].sum() > 0


def test_daily_revenue_has_positive_revenue():
    marts = _marts()
    assert marts["mart_daily_revenue"]["revenue"].sum() > 0


def test_customer_ltv_contains_repeat_customers():
    marts = _marts()
    assert (marts["mart_customer_ltv"]["orders"] > 1).any()


def test_cohort_retention_has_period_zero():
    marts = _marts()
    assert 0 in set(marts["mart_cohort_retention"]["period_number"])


def test_product_profitability_is_sorted_by_profit():
    marts = _marts()
    profits = marts["mart_product_profitability"]["gross_profit"].tolist()
    assert profits == sorted(profits, reverse=True)


def test_marketing_roi_calculates_roas():
    marts = _marts()
    assert "roas" in marts["mart_marketing_roi"].columns
    assert marts["mart_marketing_roi"]["spend"].sum() > 0


def test_rfm_segments_assign_named_segments():
    marts = _marts()
    assert marts["mart_rfm_segments"]["segment"].notna().all()


def test_kpi_summary_contains_business_metrics():
    summary = kpi_summary(_marts())
    assert summary["revenue"] > 0
    assert 0 < summary["gross_margin"] < 1
    assert summary["average_order_value"] > 0


def test_monthly_growth_has_change_column():
    growth = monthly_growth(_marts())
    assert "revenue_mom_change" in growth.columns
    assert len(growth) >= 4


def test_cohort_matrix_is_pivoted():
    matrix = cohort_matrix(_marts())
    assert 0 in matrix.columns


def test_rfm_segment_summary_groups_revenue():
    summary = rfm_segment_summary(_marts())
    assert {"segment", "customers", "revenue"}.issubset(summary.columns)


def test_forecast_returns_requested_periods():
    forecast = forecast_daily_revenue(_marts()["mart_daily_revenue"], periods=7)
    assert len(forecast) == 7
    assert forecast["forecast_revenue"].gt(0).all()


def test_business_findings_are_actionable_text():
    findings = business_findings(_marts())
    assert len(findings) >= 4
    assert any("Top 20%" in finding for finding in findings)


def test_recommendations_include_actions():
    recommendations = build_recommendations(_marts())
    assert all("action" in item for item in recommendations)


def test_run_warehouse_returns_summary_and_marts():
    result = run_warehouse()
    assert "summary" in result
    assert "mart_daily_revenue" in result["marts"]
