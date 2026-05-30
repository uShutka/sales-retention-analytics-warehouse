from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/orders.csv")

def load_orders(path: str | Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df

def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "count"))

def ltv_by_channel(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("channel", as_index=False).agg(ltv=("revenue", "mean"), revenue=("revenue", "sum")).sort_values("ltv", ascending=False)

def rfm_segments(df: pd.DataFrame) -> pd.DataFrame:
    snapshot = df["order_date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_id").agg(recency=("order_date", lambda s: (snapshot - s.max()).days), frequency=("order_id", "count"), monetary=("revenue", "sum"))
    rfm["segment"] = "regular"
    rfm.loc[(rfm.frequency >= 3) & (rfm.monetary >= 400), "segment"] = "vip"
    rfm.loc[(rfm.recency > 60), "segment"] = "at_risk"
    return rfm.reset_index()

def cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    first = df.groupby("customer_id")["order_date"].min().dt.to_period("M")
    orders = df.copy()
    orders["cohort"] = orders["customer_id"].map(first).astype(str)
    orders["period"] = orders["order_date"].dt.to_period("M").astype(str)
    return orders.groupby(["cohort", "period"], as_index=False).agg(customers=("customer_id", "nunique"))

def summary(df: pd.DataFrame) -> dict:
    return {"revenue": float(df.revenue.sum()), "orders": int(df.order_id.nunique()), "customers": int(df.customer_id.nunique())}

if __name__ == "__main__":
    print(summary(load_orders()))
