from sales_retention_analytics_warehouse.cleaning import clean_all
from sales_retention_analytics_warehouse.loaders import load_raw_tables
from sales_retention_analytics_warehouse.marts import build_marts
from sales_retention_analytics_warehouse.metrics import business_findings, kpi_summary


def run_warehouse() -> dict[str, object]:
    tables = clean_all(load_raw_tables())
    marts = build_marts(tables)
    return {
        "tables": tables,
        "marts": marts,
        "summary": kpi_summary(marts),
        "business_findings": business_findings(marts),
    }


def run_demo() -> dict[str, object]:
    return run_warehouse()
