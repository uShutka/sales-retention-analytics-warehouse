import pandas as pd


def forecast_daily_revenue(daily_revenue: pd.DataFrame, periods: int = 14) -> pd.DataFrame:
    history = daily_revenue.copy()
    history["date"] = pd.to_datetime(history["date"])
    history = history.sort_values("date")
    rolling_average = history["revenue"].tail(14).mean()
    last_date = history["date"].max()
    forecast = pd.DataFrame(
        {
            "date": pd.date_range(last_date + pd.Timedelta(days=1), periods=periods, freq="D"),
            "forecast_revenue": rolling_average,
            "method": "14-day moving average",
        }
    )
    return forecast
