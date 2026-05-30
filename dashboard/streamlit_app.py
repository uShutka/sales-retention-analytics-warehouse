import plotly.express as px
import streamlit as st

from sales_retention_analytics_warehouse.core import run_warehouse
from sales_retention_analytics_warehouse.forecasting import forecast_daily_revenue
from sales_retention_analytics_warehouse.metrics import cohort_matrix, monthly_growth, rfm_segment_summary
from sales_retention_analytics_warehouse.recommendations import build_recommendations

st.set_page_config(page_title="Sales Analytics Warehouse", layout="wide")

warehouse = run_warehouse()
marts = warehouse["marts"]
summary = warehouse["summary"]

st.title("Sales & Retention Analytics Warehouse")

top = st.columns(5)
top[0].metric("Revenue", f"${summary['revenue']:,.0f}")
top[1].metric("Gross margin", f"{summary['gross_margin']:.1%}")
top[2].metric("AOV", f"${summary['average_order_value']:,.0f}")
top[3].metric("Repeat rate", f"{summary['repeat_purchase_rate']:.1%}")
top[4].metric("ROAS", f"{summary['roas']:.2f}x")

left, right = st.columns([1.35, 1])
with left:
    st.subheader("Daily revenue")
    st.plotly_chart(px.line(marts["mart_daily_revenue"], x="date", y="revenue", markers=True), use_container_width=True)
with right:
    st.subheader("RFM revenue concentration")
    st.plotly_chart(px.bar(rfm_segment_summary(marts), x="segment", y="revenue", color="segment"), use_container_width=True)

st.subheader("Cohort retention")
st.dataframe(cohort_matrix(marts).style.format("{:.0%}"), use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Product profitability")
    st.dataframe(
        marts["mart_product_profitability"][["name", "category", "revenue", "gross_profit", "gross_margin", "refund_rate"]],
        use_container_width=True,
    )
with col_b:
    st.subheader("Marketing ROI")
    st.dataframe(marts["mart_marketing_roi"], use_container_width=True)

st.subheader("Revenue forecast")
st.plotly_chart(px.line(forecast_daily_revenue(marts["mart_daily_revenue"]), x="date", y="forecast_revenue"), use_container_width=True)

st.subheader("Business recommendations")
for item in build_recommendations(marts):
    st.markdown(f"**{item['area']}**: {item['finding']} Action: {item['action']}")

st.subheader("Monthly growth")
st.dataframe(monthly_growth(marts), use_container_width=True)
