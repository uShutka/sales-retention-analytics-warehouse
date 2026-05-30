from pathlib import Path

import pandas as pd

from sales_retention_analytics_warehouse.config import project_root

RAW_TABLE_FILES = {
    "orders": "orders.csv",
    "customers": "customers.csv",
    "products": "products.csv",
    "payments": "payments.csv",
    "refunds": "refunds.csv",
    "marketing_spend": "marketing_spend.csv",
}


def default_raw_dir() -> Path:
    return project_root() / "data" / "raw"


def load_raw_tables(raw_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    data_dir = raw_dir or default_raw_dir()
    tables: dict[str, pd.DataFrame] = {}
    for table_name, file_name in RAW_TABLE_FILES.items():
        path = data_dir / file_name
        if not path.exists():
            raise FileNotFoundError(f"Missing raw table {table_name}: {path}")
        tables[table_name] = pd.read_csv(path)
    return tables
