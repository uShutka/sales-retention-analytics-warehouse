from __future__ import annotations

import pandas as pd


def build_order_lines(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = tables["orders"].query("status != 'cancelled'").copy()
    products = tables["products"]
    refunds = tables["refunds"].groupby("order_id", as_index=False)["amount"].sum().rename(columns={"amount": "refund_amount"})

    lines = orders.merge(products, on="product_id", how="left").merge(refunds, on="order_id", how="left")
    lines["refund_amount"] = lines["refund_amount"].fillna(0)
    lines["gross_revenue"] = lines["quantity"] * lines["unit_price"] * (1 - lines["discount_pct"])
    lines["cogs"] = lines["quantity"] * lines["unit_cost"]
    lines["gross_profit"] = lines["gross_revenue"] - lines["cogs"]
    lines["net_revenue"] = lines["gross_revenue"] - lines["refund_amount"]
    lines["order_month"] = lines["order_date"].dt.to_period("M").astype(str)
    lines["order_week"] = lines["order_date"].dt.to_period("W").astype(str)
    return lines


def mart_daily_revenue(order_lines: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        order_lines.groupby(order_lines["order_date"].dt.date)
        .agg(
            revenue=("net_revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
            units_sold=("quantity", "sum"),
            refunds=("refund_amount", "sum"),
        )
        .reset_index()
        .rename(columns={"order_date": "date"})
    )
    grouped["gross_margin"] = grouped["gross_profit"] / grouped["revenue"].where(grouped["revenue"] != 0)
    grouped["average_order_value"] = grouped["revenue"] / grouped["orders"].where(grouped["orders"] != 0)
    return grouped.sort_values("date")


def mart_customer_ltv(order_lines: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        order_lines.groupby("customer_id")
        .agg(
            revenue=("net_revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            orders=("order_id", "nunique"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
            refunds=("refund_amount", "sum"),
        )
        .reset_index()
    )
    grouped["ltv"] = grouped["revenue"]
    grouped["gross_margin"] = grouped["gross_profit"] / grouped["revenue"].where(grouped["revenue"] != 0)
    return customers.merge(grouped, on="customer_id", how="left").fillna({"revenue": 0, "gross_profit": 0, "orders": 0, "refunds": 0, "ltv": 0})


def mart_cohort_retention(order_lines: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    customer_cohorts = customers[["customer_id", "signup_date"]].copy()
    customer_cohorts["cohort_month"] = customer_cohorts["signup_date"].dt.to_period("M")
    orders = order_lines[["customer_id", "order_date"]].drop_duplicates().copy()
    orders["order_month"] = orders["order_date"].dt.to_period("M")
    cohort_orders = orders.merge(customer_cohorts, on="customer_id", how="left")
    cohort_orders["period_number"] = (
        (cohort_orders["order_month"].dt.year - cohort_orders["cohort_month"].dt.year) * 12
        + (cohort_orders["order_month"].dt.month - cohort_orders["cohort_month"].dt.month)
    )
    cohort_orders = cohort_orders[cohort_orders["period_number"] >= 0]
    cohort_sizes = customer_cohorts.groupby("cohort_month")["customer_id"].nunique().rename("cohort_size")
    retention = (
        cohort_orders.groupby(["cohort_month", "period_number"])["customer_id"].nunique().rename("active_customers").reset_index()
    )
    retention = retention.merge(cohort_sizes, on="cohort_month", how="left")
    retention["retention_rate"] = retention["active_customers"] / retention["cohort_size"].where(retention["cohort_size"] != 0)
    retention["cohort_month"] = retention["cohort_month"].astype(str)
    return retention.sort_values(["cohort_month", "period_number"])


def mart_product_profitability(order_lines: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        order_lines.groupby(["product_id", "name", "category", "brand"], as_index=False)
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("net_revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            refunds=("refund_amount", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("gross_profit", ascending=False)
    )
    grouped["gross_margin"] = grouped["gross_profit"] / grouped["revenue"].where(grouped["revenue"] != 0)
    grouped["refund_rate"] = grouped["refunds"] / grouped["revenue"].where(grouped["revenue"] != 0)
    return grouped


def mart_marketing_roi(order_lines: pd.DataFrame, customers: pd.DataFrame, spend: pd.DataFrame) -> pd.DataFrame:
    customer_channels = customers[["customer_id", "signup_date", "acquisition_channel"]].copy()
    customer_channels["month"] = customer_channels["signup_date"].dt.to_period("M").astype(str)
    revenue = order_lines.merge(customer_channels[["customer_id", "acquisition_channel"]], on="customer_id", how="left")
    revenue_by_channel = (
        revenue.groupby(["order_month", "acquisition_channel"], as_index=False)
        .agg(revenue=("net_revenue", "sum"), gross_profit=("gross_profit", "sum"), customers=("customer_id", "nunique"))
        .rename(columns={"order_month": "month", "acquisition_channel": "channel"})
    )
    spend = spend.copy()
    spend["month"] = spend["spend_date"].dt.to_period("M").astype(str)
    spend_by_channel = spend.groupby(["month", "channel"], as_index=False)["spend"].sum()
    new_customers = customer_channels.groupby(["month", "acquisition_channel"], as_index=False)["customer_id"].nunique()
    new_customers = new_customers.rename(columns={"acquisition_channel": "channel", "customer_id": "new_customers"})

    roi = revenue_by_channel.merge(spend_by_channel, on=["month", "channel"], how="outer").merge(new_customers, on=["month", "channel"], how="outer")
    roi[["revenue", "gross_profit", "customers", "spend", "new_customers"]] = roi[
        ["revenue", "gross_profit", "customers", "spend", "new_customers"]
    ].fillna(0)
    roi["roas"] = roi["revenue"] / roi["spend"].where(roi["spend"] != 0)
    roi["cac"] = roi["spend"] / roi["new_customers"].where(roi["new_customers"] != 0)
    return roi.sort_values(["month", "channel"])


def _score_series(series: pd.Series, high_is_good: bool = True) -> pd.Series:
    ranked = series.rank(method="first", ascending=not high_is_good)
    bins = min(5, ranked.nunique())
    if bins <= 1:
        return pd.Series([3] * len(series), index=series.index)
    return pd.qcut(ranked, q=bins, labels=range(1, bins + 1)).astype(int).reindex(series.index).fillna(1)


def mart_rfm_segments(customer_ltv: pd.DataFrame, reference_date: pd.Timestamp | None = None) -> pd.DataFrame:
    frame = customer_ltv.copy()
    reference = reference_date or pd.to_datetime(frame["last_order_date"].max()) + pd.Timedelta(days=1)
    frame["last_order_date"] = pd.to_datetime(frame["last_order_date"])
    frame["recency_days"] = (reference - frame["last_order_date"]).dt.days.fillna(999)
    frame["frequency"] = frame["orders"].astype(int)
    frame["monetary"] = frame["revenue"].astype(float)
    frame["r_score"] = _score_series(frame["recency_days"], high_is_good=False)
    frame["f_score"] = _score_series(frame["frequency"], high_is_good=True)
    frame["m_score"] = _score_series(frame["monetary"], high_is_good=True)
    frame["rfm_score"] = frame["r_score"].astype(str) + frame["f_score"].astype(str) + frame["m_score"].astype(str)

    def segment(row: pd.Series) -> str:
        if row["r_score"] >= 4 and row["f_score"] >= 4 and row["m_score"] >= 4:
            return "Champions"
        if row["f_score"] >= 4 and row["m_score"] >= 3:
            return "Loyal Customers"
        if row["m_score"] >= 4:
            return "Big Spenders"
        if row["r_score"] <= 2 and row["m_score"] >= 3:
            return "At Risk"
        if row["r_score"] >= 4 and row["frequency"] <= 1:
            return "New Customers"
        return "Regular"

    frame["segment"] = frame.apply(segment, axis=1)
    return frame[
        [
            "customer_id",
            "recency_days",
            "frequency",
            "monetary",
            "r_score",
            "f_score",
            "m_score",
            "rfm_score",
            "segment",
            "acquisition_channel",
        ]
    ]


def build_marts(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    order_lines = build_order_lines(tables)
    customer_ltv = mart_customer_ltv(order_lines, tables["customers"])
    return {
        "fact_order_lines": order_lines,
        "mart_daily_revenue": mart_daily_revenue(order_lines),
        "mart_customer_ltv": customer_ltv,
        "mart_cohort_retention": mart_cohort_retention(order_lines, tables["customers"]),
        "mart_product_profitability": mart_product_profitability(order_lines),
        "mart_marketing_roi": mart_marketing_roi(order_lines, tables["customers"], tables["marketing_spend"]),
        "mart_rfm_segments": mart_rfm_segments(customer_ltv),
    }
