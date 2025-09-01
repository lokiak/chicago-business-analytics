
import pandas as pd
from datetime import datetime, timedelta

def start_date_days_ago(days: int) -> str:
    d = datetime.utcnow().date() - timedelta(days=days)
    return d.isoformat()

def week_start(d: pd.Timestamp) -> pd.Timestamp:
    return d - pd.to_timedelta(d.weekday(), unit="D")
