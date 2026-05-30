import pandas as pd


def kpi_summary(marts: dict[str, pd.DataFrame]) -> dict[str, float]:
    daily = marts["mart_daily_revenue"]
    customer_ltv = marts["mart_customer_ltv"]
    roi = marts["mart_marketing_roi"]
    revenue = float(daily["revenue"].sum())
    gross_profit = float(daily["gross_profit"].sum())
    order_count = int(daily["orders"].sum())
    customer_count = int((customer_ltv["orders"] > 0).sum())
    repeat_customers = int((customer_ltv["orders"] > 1).sum())
    refund_amount = float(daily["refunds"].sum())
    spend = float(roi["spend"].sum())
    return {
        "revenue": revenue,
        "gross_profit": gross_profit,
        "gross_margin": gross_profit / revenue if revenue else 0,
        "average_order_value": revenue / order_count if order_count else 0,
        "repeat_purchase_rate": repeat_customers / customer_count if customer_count else 0,
        "refund_rate": refund_amount / revenue if revenue else 0,
        "customers": customer_count,
        "orders": order_count,
        "average_ltv": float(customer_ltv["ltv"].mean()),
        "cac": spend / customer_count if customer_count else 0,
        "roas": revenue / spend if spend else 0,
    }


def monthly_growth(marts: dict[str, pd.DataFrame]) -> pd.DataFrame:
    daily = marts["mart_daily_revenue"].copy()
    daily["month"] = pd.to_datetime(daily["date"]).dt.to_period("M").astype(str)
    monthly = daily.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), gross_profit=("gross_profit", "sum"))
    monthly["revenue_mom_change"] = monthly["revenue"].pct_change()
    monthly["gross_margin"] = monthly["gross_profit"] / monthly["revenue"].where(monthly["revenue"] != 0)
    monthly["margin_delta"] = monthly["gross_margin"].diff()
    return monthly


def cohort_matrix(marts: dict[str, pd.DataFrame]) -> pd.DataFrame:
    retention = marts["mart_cohort_retention"]
    return retention.pivot(index="cohort_month", columns="period_number", values="retention_rate").fillna(0)


def rfm_segment_summary(marts: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return (
        marts["mart_rfm_segments"].groupby("segment", as_index=False)
        .agg(customers=("customer_id", "nunique"), revenue=("monetary", "sum"))
        .sort_values("revenue", ascending=False)
    )


def business_findings(marts: dict[str, pd.DataFrame]) -> list[str]:
    summary = kpi_summary(marts)
    growth = monthly_growth(marts)
    roi = marts["mart_marketing_roi"]
    rfm = marts["mart_rfm_segments"]
    product = marts["mart_product_profitability"]

    findings: list[str] = []
    if len(growth) >= 2:
        last = growth.iloc[-1]
        mom = last["revenue_mom_change"]
        findings.append(
            f"Revenue changed by {mom:.1%} MoM in {last['month']}; gross margin ended at {last['gross_margin']:.1%}."
        )
    best_channel = roi.groupby("channel")["roas"].mean().replace([float("inf")], 0).sort_values(ascending=False)
    if not best_channel.empty:
        findings.append(f"{best_channel.index[0].title()} has the strongest average ROAS at {best_channel.iloc[0]:.2f}x.")
    paying = rfm.sort_values("monetary", ascending=False)
    top_20 = max(1, int(len(paying) * 0.2))
    concentration = paying.head(top_20)["monetary"].sum() / paying["monetary"].sum()
    findings.append(f"Top 20% of customers generate {concentration:.1%} of total revenue.")
    weak_margin = product.sort_values("gross_margin").iloc[0]
    findings.append(
        f"{weak_margin['category'].title()} contains the lowest-margin product ({weak_margin['name']}) at {weak_margin['gross_margin']:.1%} margin."
    )
    findings.append(f"Repeat purchase rate is {summary['repeat_purchase_rate']:.1%}; retention actions should focus before day 30.")
    return findings
