import streamlit as st
from sales_retention_analytics_warehouse.core import load_orders, monthly_revenue, ltv_by_channel, rfm_segments, summary
df = load_orders()
st.title("Sales & Retention Analytics Warehouse")
st.write(summary(df))
st.dataframe(monthly_revenue(df))
st.dataframe(ltv_by_channel(df))
st.dataframe(rfm_segments(df))
