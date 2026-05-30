from sales_retention_analytics_warehouse.core import load_orders, monthly_revenue, rfm_segments, summary
def test_sales_metrics():
    df = load_orders()
    assert summary(df)["orders"] == 8
    assert monthly_revenue(df)["revenue"].sum() == df["revenue"].sum()
    assert "vip" in set(rfm_segments(df)["segment"])
