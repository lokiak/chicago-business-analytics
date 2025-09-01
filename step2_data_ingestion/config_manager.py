
from dataclasses import dataclass
from pathlib import Path
import os, yaml
from dotenv import load_dotenv

load_dotenv()
CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"

@dataclass
class Settings:
    google_creds_path: str
    sheet_id: str
    tab_licenses: str = os.getenv("TAB_LICENSES", "licenses_weekly")
    tab_permits: str = os.getenv("TAB_PERMITS", "permits_weekly")
    tab_cta: str = os.getenv("TAB_CTA", "cta_weekly")
    tab_summary: str = os.getenv("TAB_SUMMARY", "summary_latest")
    days_lookback: int = int(os.getenv("DAYS_LOOKBACK", "90"))
    baseline_weeks: int = int(os.getenv("WEEKLY_BASELINE_WEEKS", "13"))
    enable_permits: bool = os.getenv("ENABLE_PERMITS", "true").lower() == "true"
    enable_cta: bool = os.getenv("ENABLE_CTA", "true").lower() == "true"

def load_settings() -> Settings:
    google_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    sheet_id = os.getenv("SHEET_ID", "").strip()
    if not google_creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS missing in environment.")
    if not sheet_id:
        raise ValueError("SHEET_ID missing in environment.")
    return Settings(google_creds_path=google_creds_path, sheet_id=sheet_id)

def load_datasets_yaml():
    with open(CONFIGS_DIR / "datasets.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_category_map():
    import pandas as pd
    import csv
    p = CONFIGS_DIR / "category_map.csv"
    df = pd.read_csv(p, quoting=csv.QUOTE_MINIMAL)
    df["license_description"] = df["license_description"].astype(str).str.strip().str.upper()
    df["bucket"] = df["bucket"].astype(str).str.strip()
    return df
