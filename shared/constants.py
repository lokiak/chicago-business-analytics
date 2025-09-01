"""
Chicago SMB Market Radar - Project Constants

This module contains project-wide constants and configuration.
"""

# BI Framework Steps
BI_STEPS = {
    1: "Scope & Strategy",
    2: "Data Ingestion",
    3: "Transform & Model",
    4: "Load & Validate",
    5: "Visualize & Report",
    6: "Automate & Scale"
}

# Data Sources
DATA_SOURCES = {
    "business_licenses": "r5kz-chrr",
    "building_permits": "ydr8-5enu",
    "cta_boardings": "6iiy-9s97"
}

# Default Configuration
DEFAULT_DAYS_LOOKBACK = 90
DEFAULT_BASELINE_WEEKS = 13
DEFAULT_SHEET_ROWS = 1000
DEFAULT_SHEET_COLS = 26
