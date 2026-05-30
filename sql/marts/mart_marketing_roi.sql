select
    month,
    channel,
    revenue,
    spend,
    revenue / nullif(spend, 0) as roas,
    spend / nullif(new_customers, 0) as cac
from analytics.channel_revenue_and_spend;
