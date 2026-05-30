select
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score || f_score || m_score as rfm_score,
    segment
from analytics.customer_rfm_scores;
