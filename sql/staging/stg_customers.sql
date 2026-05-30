select
    customer_id,
    cast(signup_date as date) as signup_date,
    lower(acquisition_channel) as acquisition_channel,
    upper(country) as country
from raw.customers;
