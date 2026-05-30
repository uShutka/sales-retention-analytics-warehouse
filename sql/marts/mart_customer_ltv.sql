select
    customer_id,
    sum(net_revenue) as ltv,
    count(distinct order_id) as orders,
    min(order_date) as first_order_date,
    max(order_date) as last_order_date
from analytics.fact_order_lines
group by 1;
