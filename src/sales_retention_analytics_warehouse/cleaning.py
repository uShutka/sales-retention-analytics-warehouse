import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _to_datetime(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    frame = frame.copy()
    for column in columns:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def _to_numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    frame = frame.copy()
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0)
    return frame


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    frame = customers.drop_duplicates(subset=["customer_id"]).copy()
    frame["customer_id"] = frame["customer_id"].astype(str).str.strip()
    frame["acquisition_channel"] = frame["acquisition_channel"].fillna("unknown").str.lower().str.strip()
    frame["country"] = frame["country"].fillna("unknown").str.upper().str.strip()
    frame = _to_datetime(frame, ["signup_date"])
    return frame


def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    frame = products.drop_duplicates(subset=["product_id"]).copy()
    frame["category"] = frame["category"].fillna("uncategorized").str.lower().str.strip()
    frame["brand"] = frame["brand"].fillna("unknown").str.strip()
    frame = _to_numeric(frame, ["unit_cost"])
    return frame


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    frame = orders.drop_duplicates(subset=["order_id"]).copy()
    frame["status"] = frame["status"].fillna("completed").str.lower().str.strip()
    frame = _to_datetime(frame, ["order_date"])
    frame = _to_numeric(frame, ["quantity", "unit_price", "discount_pct"])
    frame = frame[(frame["quantity"] > 0) & (frame["unit_price"] > 0)]
    return frame


def clean_payments(payments: pd.DataFrame) -> pd.DataFrame:
    frame = payments.drop_duplicates(subset=["payment_id"]).copy()
    frame["status"] = frame["status"].fillna("captured").str.lower().str.strip()
    frame["currency"] = frame["currency"].fillna("USD").str.upper().str.strip()
    frame = _to_datetime(frame, ["payment_date"])
    frame = _to_numeric(frame, ["amount"])
    return frame


def clean_refunds(refunds: pd.DataFrame) -> pd.DataFrame:
    frame = refunds.drop_duplicates(subset=["refund_id"]).copy()
    frame = _to_datetime(frame, ["refund_date"])
    frame = _to_numeric(frame, ["amount"])
    return frame


def clean_marketing_spend(marketing_spend: pd.DataFrame) -> pd.DataFrame:
    frame = marketing_spend.copy()
    frame["channel"] = frame["channel"].fillna("unknown").str.lower().str.strip()
    frame = _to_datetime(frame, ["spend_date"])
    frame = _to_numeric(frame, ["spend"])
    return frame


def clean_all(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    logger.info("Cleaning raw sales warehouse tables", extra={"tables": sorted(tables)})
    return {
        "customers": clean_customers(tables["customers"]),
        "products": clean_products(tables["products"]),
        "orders": clean_orders(tables["orders"]),
        "payments": clean_payments(tables["payments"]),
        "refunds": clean_refunds(tables["refunds"]),
        "marketing_spend": clean_marketing_spend(tables["marketing_spend"]),
    }
