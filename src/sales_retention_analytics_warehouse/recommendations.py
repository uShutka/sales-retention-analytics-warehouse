import pandas as pd

from sales_retention_analytics_warehouse.metrics import business_findings, kpi_summary


def build_recommendations(marts: dict[str, pd.DataFrame]) -> list[dict[str, str]]:
    summary = kpi_summary(marts)
    product = marts["mart_product_profitability"].sort_values("gross_margin")
    roi = marts["mart_marketing_roi"].groupby("channel", as_index=False).agg(roas=("roas", "mean"), spend=("spend", "sum"))
    best_channel = roi.sort_values("roas", ascending=False).iloc[0]
    weakest_product = product.iloc[0]
    findings = business_findings(marts)
    return [
        {
            "area": "Retention",
            "finding": findings[-1],
            "action": "Launch a second-purchase email or Telegram campaign 14-21 days after the first order.",
        },
        {
            "area": "Marketing ROI",
            "finding": f"{best_channel['channel'].title()} delivers {best_channel['roas']:.2f}x ROAS.",
            "action": "Shift budget from low-ROAS channels into the strongest acquisition channel and monitor CAC weekly.",
        },
        {
            "area": "Gross Margin",
            "finding": f"{weakest_product['name']} has only {weakest_product['gross_margin']:.1%} margin.",
            "action": "Review discount rules and supplier cost for the lowest-margin products before scaling promotions.",
        },
        {
            "area": "Executive KPI",
            "finding": f"Revenue is ${summary['revenue']:,.0f} with {summary['gross_margin']:.1%} gross margin.",
            "action": "Track revenue and margin together; revenue growth without margin control can hide discount risk.",
        },
    ]
