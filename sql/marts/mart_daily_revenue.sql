select
    order_date as date,
    sum(quantity * unit_price * (1 - discount_pct)) as revenue,
    count(distinct order_id) as orders,
    count(distinct customer_id) as customers
from staging.stg_orders
where status <> 'cancelled'
group by 1
order by 1;
