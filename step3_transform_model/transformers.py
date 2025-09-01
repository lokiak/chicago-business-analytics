
import pandas as pd
import numpy as np
from typing import List
from .utils import week_start

def normalize_license_descriptions(df: pd.DataFrame, desc_col: str = "license_description"):
    df[desc_col] = df[desc_col].astype(str).str.upper().str.strip()
    return df

def apply_category_map(df: pd.DataFrame, mapping_df: pd.DataFrame, desc_col: str, out_col: str = "bucket"):
    m = dict(zip(mapping_df["license_description"], mapping_df["bucket"]))
    df[out_col] = df[desc_col].map(m)
    fallback = {
        "RESTAURANT": "Food & Bev",
        "FOOD": "Food & Bev",
        "BARBER": "Personal Services",
        "SALON": "Personal Services",
        "NAIL": "Personal Services",
        "MASSAGE": "Personal Services",
        "CONSULT": "Professional",
        "ACCOUNT": "Professional",
        "REAL ESTATE": "Professional",
        "INSURANCE": "Professional",
        "IT": "Professional",
        "CONTRACTOR": "Home Services",
        "PLUMB": "Home Services",
        "ELECTR": "Home Services",
        "ROOF": "Home Services",
        "HVAC": "Home Services",
    }
    mask = df[out_col].isna()
    df.loc[mask, out_col] = df.loc[mask, desc_col].apply(
        lambda s: next((b for k,b in fallback.items() if k in s), np.nan)
    )
    return df

def daily_to_weekly(df: pd.DataFrame, date_col: str, group_cols: List[str], value_col: str = "n"):
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d["week_start"] = d[date_col].apply(week_start)
    grp = d.groupby(["week_start"] + group_cols, dropna=False, as_index=False)[value_col].sum()
    return grp

def add_baselines(df: pd.DataFrame, group_cols: List[str], value_col: str, baseline_weeks: int = 13):
    d = df.copy().sort_values("week_start")
    d["avg_13w"] = (
        d.groupby(group_cols)[value_col]
         .rolling(window=baseline_weeks, min_periods=1).mean()
         .reset_index(level=group_cols, drop=True)
    )
    d["std_13w"] = (
        d.groupby(group_cols)[value_col]
         .rolling(window=baseline_weeks, min_periods=1).std()
         .reset_index(level=group_cols, drop=True)
         .fillna(0.0)
    )
    d["wow"] = d.groupby(group_cols)[value_col].pct_change().replace([np.inf, -np.inf], np.nan)
    d["momentum_index"] = (d[value_col] - d["avg_13w"]) / d["std_13w"].replace(0, 1.0)
    return d

def build_summary_latest(weekly_df: pd.DataFrame, area_col: str = "community_area_name", value_col: str = "new_licenses"):
    d = weekly_df.copy()
    if d.empty:
        return pd.Timestamp("1970-01-05"), pd.DataFrame(), pd.DataFrame()
    if area_col not in d.columns:
        area_col = "community_area"
    latest_week = d["week_start"].max()
    latest = d[d["week_start"] == latest_week]
    top_level = (latest.groupby(area_col, as_index=False)[value_col]
                 .sum().sort_values(value_col, ascending=False).head(10))
    cols = [c for c in ["bucket","momentum_index",value_col,"avg_13w",area_col] if c in latest.columns]
    if "momentum_index" in latest.columns:
        top_momentum = latest.sort_values("momentum_index", ascending=False).head(10)[cols]
    else:
        top_momentum = pd.DataFrame(columns=cols)
    return latest_week, top_level, top_momentum
