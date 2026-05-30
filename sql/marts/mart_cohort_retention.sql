select
    cohort_month,
    period_number,
    count(distinct customer_id) as active_customers,
    count(distinct customer_id)::numeric / max(cohort_size) as retention_rate
from analytics.fact_customer_cohorts
group by 1, 2
order by 1, 2;
