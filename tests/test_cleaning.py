import pandas as pd

from sales_retention_analytics_warehouse.cleaning import clean_all, clean_orders
from sales_retention_analytics_warehouse.loaders import load_raw_tables


def test_load_raw_tables_contains_expected_entities():
    tables = load_raw_tables()
    assert {"orders", "customers", "products", "payments", "refunds", "marketing_spend"} == set(tables)


def test_clean_orders_removes_duplicate_order_ids():
    dirty = pd.DataFrame(
        [
            {"order_id": "O1", "customer_id": "C1", "product_id": "P1", "order_date": "2025-01-01", "quantity": 1, "unit_price": 10, "discount_pct": 0, "status": "Completed"},
            {"order_id": "O1", "customer_id": "C1", "product_id": "P1", "order_date": "2025-01-01", "quantity": 1, "unit_price": 10, "discount_pct": 0, "status": "Completed"},
        ]
    )
    cleaned = clean_orders(dirty)
    assert len(cleaned) == 1


def test_clean_orders_filters_non_positive_prices():
    dirty = pd.DataFrame(
        [
            {"order_id": "O1", "customer_id": "C1", "product_id": "P1", "order_date": "2025-01-01", "quantity": 1, "unit_price": 0, "discount_pct": 0, "status": "completed"}
        ]
    )
    assert clean_orders(dirty).empty


def test_clean_all_parses_dates_and_normalizes_channels():
    cleaned = clean_all(load_raw_tables())
    assert pd.api.types.is_datetime64_any_dtype(cleaned["customers"]["signup_date"])
    assert cleaned["customers"]["acquisition_channel"].str.islower().all()
