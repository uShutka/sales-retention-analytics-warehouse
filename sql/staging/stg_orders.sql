select
    order_id,
    customer_id,
    product_id,
    cast(order_date as date) as order_date,
    quantity,
    unit_price,
    discount_pct,
    lower(status) as status
from raw.orders
where quantity > 0
  and unit_price > 0;
