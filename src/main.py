
from pathlib import Path
from datetime import datetime
import pandas as pd

from .logging_setup import setup_logger
from .config import load_settings, load_datasets_yaml
from .socrata import SocrataClient


from .sheets import open_sheet, upsert_worksheet, overwrite_with_dataframe
from .brief import render_markdown_brief

logger = setup_logger()
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

def debug_socrata_api(client, cfg):
    """Debug function to test Socrata API directly"""
    ds = cfg["datasets"]["business_licenses"]
    logger.info("=== Socrata API Debug ===")
    logger.info(f"Domain: {cfg['domain']}")
    logger.info(f"Dataset ID: {ds['id']}")

    # Test basic endpoint
    test_url = f"https://{cfg['domain']}/resource/{ds['id']}.json"
    logger.info(f"Testing basic endpoint: {test_url}")

    try:
        import requests
        # First try to get just one record to see the schema
        r = requests.get(test_url, params={"$limit": 1}, timeout=30)
        logger.info(f"Basic endpoint test - Status: {r.status_code}")
        logger.info(f"Response headers: {dict(r.headers)}")
        if r.status_code == 200:
            try:
                data = r.json()
                logger.info(f"Basic endpoint test - Success, got {len(data)} records")
                if data:
                    logger.info(f"Sample record keys: {list(data[0].keys())}")
                    logger.info(f"Sample record: {data[0]}")

                    # Test if the configured fields exist
                    configured_fields = [
                        ds['date_field'],
                        ds['area_field'],
                        ds['area_name_field'],
                        ds['description_field'],
                        ds['application_type_field']
                    ]
                    logger.info(f"Configured fields: {configured_fields}")

                    missing_fields = [field for field in configured_fields if field not in data[0].keys()]
                    if missing_fields:
                        logger.error(f"Missing fields in dataset: {missing_fields}")
                    else:
                        logger.info("All configured fields found in dataset")

            except ValueError as e:
                logger.error(f"Basic endpoint test - JSON parse error: {e}")
                logger.error(f"Response content: {r.text[:500]}")
        else:
            logger.error(f"Basic endpoint test - HTTP error: {r.text}")

        # Try to find date-related columns
        logger.info("=== Searching for date columns ===")
        if r.status_code == 200:
            try:
                data = r.json()
                if data:
                    date_columns = [key for key in data[0].keys() if 'date' in key.lower() or 'time' in key.lower()]
                    logger.info(f"Potential date columns: {date_columns}")

                    # Test a simple query with one of the date columns
                    if date_columns:
                        test_date_col = date_columns[0]
                        logger.info(f"Testing query with date column: {test_date_col}")
                        test_params = {
                            "$select": f"community_area, {test_date_col}",
                            "$limit": 5
                        }
                        test_r = requests.get(test_url, params=test_params, timeout=30)
                        logger.info(f"Test query status: {test_r.status_code}")
                        if test_r.status_code == 200:
                            logger.info("Test query successful!")
                        else:
                            logger.error(f"Test query failed: {test_r.text}")
            except Exception as e:
                logger.error(f"Error testing date columns: {e}")

    except Exception as e:
        logger.error(f"Basic endpoint test - Exception: {e}")

    logger.info("=== End Debug ===")

def debug_cta_api(client, cfg):
    """Debug function to test CTA API directly"""
    ds = cfg["datasets"]["cta_boardings"]
    logger.info("=== CTA API Debug ===")
    logger.info(f"Dataset ID: {ds['id']}")

    # Test basic endpoint
    test_url = f"https://{cfg['domain']}/resource/{ds['id']}.json"
    logger.info(f"Testing CTA endpoint: {test_url}")

    try:
        import requests
        # First try to get just one record to see the schema
        r = requests.get(test_url, params={"$limit": 1}, timeout=30)
        logger.info(f"CTA endpoint test - Status: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                logger.info(f"CTA endpoint test - Success, got {len(data)} records")
                if data:
                    logger.info(f"CTA sample record keys: {list(data[0].keys())}")
                    logger.info(f"CTA sample record: {data[0]}")

                    # Test if the configured fields exist
                    configured_fields = [ds['date_field'], ds['total_field']]
                    logger.info(f"CTA configured fields: {configured_fields}")

                    missing_fields = [field for field in configured_fields if field not in data[0].keys()]
                    if missing_fields:
                        logger.error(f"CTA missing fields: {missing_fields}")

                        # Try to find date and total columns
                        date_columns = [key for key in data[0].keys() if 'date' in key.lower() or 'time' in key.lower()]
                        total_columns = [key for key in data[0].keys() if 'total' in key.lower() or 'count' in key.lower() or 'board' in key.lower()]
                        logger.info(f"CTA potential date columns: {date_columns}")
                        logger.info(f"CTA potential total columns: {total_columns}")
                    else:
                        logger.info("All CTA configured fields found in dataset")

            except ValueError as e:
                logger.error(f"CTA endpoint test - JSON parse error: {e}")
                logger.error(f"Response content: {r.text[:500]}")
        else:
            logger.error(f"CTA endpoint test - HTTP error: {r.text}")

    except Exception as e:
        logger.error(f"CTA endpoint test - Exception: {e}")

    logger.info("=== End CTA Debug ===")

def fetch_licenses(client, cfg, days_lookback: int):
    ds = cfg["datasets"]["business_licenses"]
    params = {
        "$select": ",".join([
            "id", "license_id", "account_number", "site_number", "legal_name", "doing_business_as_name",
            "address", "city", "state", "zip_code", "ward", "precinct", "ward_precinct", "police_district",
            f"{ds['area_field']}", f"{ds['area_name_field']}", "neighborhood", "license_code",
            f"{ds['description_field']}", "business_activity_id", "business_activity", "license_number",
            f"{ds['application_type_field']}", "application_created_date", "application_requirements_complete",
            "payment_date", "conditional_approval", f"{ds['date_field']}", "expiration_date",
            "license_approved_for_issuance", "date_issued", "license_status", "license_status_change_date",
            "ssa", "latitude", "longitude", "location"
        ]),
        "$where": f"{ds['application_type_field']}='{ds['issue_value']}' AND {ds['date_field']} >= '{(datetime.utcnow() - pd.Timedelta(days=days_lookback)).strftime('%Y-%m-%d')}'",
        "$order": f"{ds['date_field']}"
    }

    logger.info(f"Business licenses dataset ID: {ds['id']}")
    logger.info(f"Constructed query parameters: {params}")
    logger.info(f"Date lookback: {days_lookback} days")
    logger.info(f"Start date: {start_date_days_ago(days_lookback)}")
    logger.info(f"Expanded fields: {len(params['$select'].split(','))} fields selected")

    data = client.get(ds["id"], params)
    logger.info(f"Retrieved {len(data)} license records with expanded fields")

    # Check if we got any data and log the actual fields received
    if data:
        actual_fields = list(data[0].keys()) if data[0] else []
        logger.info(f"Actual fields received: {actual_fields}")

    pd.DataFrame(data).to_json(RAW_DIR / f"licenses_{datetime.utcnow().date().isoformat()}.json", orient="records", indent=2)
    df = pd.DataFrame(data)
    if df.empty:
        return df

    return df

def fetch_permits(client, cfg, days_lookback: int):
    ds = cfg["datasets"]["building_permits"]
    params = {
        "$select": ",".join([
            "id", "permit_", "permit_status", "permit_milestone", "permit_type", "review_type",
            "application_start_date", f"{ds['date_field']}", "processing_time", "street_number",
            "street_direction", "street_name", "work_type", "work_description", "building_fee_paid",
            "zoning_fee_paid", "other_fee_paid", "subtotal_paid", "building_fee_unpaid",
            "zoning_fee_unpaid", "other_fee_unpaid", "subtotal_unpaid", "building_fee_waived",
            "building_fee_subtotal", "zoning_fee_subtotal", "other_fee_subtotal", "zoning_fee_waived",
            "other_fee_waived", "subtotal_waived", "total_fee",
            f"{ds['area_field']}"
        ]),
        "$where": f"{ds['date_field']} >= '{(datetime.utcnow() - pd.Timedelta(days=days_lookback)).strftime('%Y-%m-%d')}'",
        "$order": f"{ds['date_field']}"
    }
    data = client.get(ds["id"], params)
    logger.info(f"Retrieved {len(data)} permit records with expanded fields")

    # Check if we got any data and log the actual fields received
    if data:
        actual_fields = list(data[0].keys()) if data[0] else []
        logger.info(f"Actual fields received: {actual_fields}")

    pd.DataFrame(data).to_json(RAW_DIR / f"permits_{datetime.utcnow().date().isoformat()}.json", orient="records", indent=2)
    df = pd.DataFrame(data)
    if df.empty:
        return df

    return df

def fetch_cta(client, cfg, days_lookback: int):
    ds = cfg["datasets"]["cta_boardings"]
    # Use 2 years of data for CTA since dataset may not be updated as frequently
    cta_lookback_days = 730  # 2 years
    cta_start_date = start_date_days_ago(cta_lookback_days)

    logger.info(f"CTA dataset ID: {ds['id']}")
    logger.info(f"CTA lookback period: {cta_lookback_days} days (2 years)")
    logger.info(f"CTA start date: {cta_start_date}")

    params = {
        "$select": f"{ds['date_field']}, {ds['total_field']}",
        "$where": f"{ds['date_field']} >= '{cta_start_date}'",
        "$order": f"{ds['date_field']}"
    }

    logger.info(f"CTA query parameters: {params}")
    data = client.get(ds["id"], params)
    pd.DataFrame(data).to_json(RAW_DIR / f"cta_{datetime.utcnow().date().isoformat()}.json", orient="records", indent=2)
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df[ds['total_field']] = pd.to_numeric(df[ds['total_field']], errors="coerce").fillna(0).astype(int)
    return df

def main():
    settings = load_settings()
    cfg = load_datasets_yaml()
    client = SocrataClient(cfg["domain"])

    # Debug the APIs first
    debug_socrata_api(client, cfg)
    debug_cta_api(client, cfg)

    logger.info("Fetching Business Licenses...")
    try:
        lic_df = fetch_licenses(client, cfg, settings.days_lookback)
        logger.info(f"Successfully fetched {len(lic_df)} license records")
    except Exception as e:
        logger.error(f"Failed to fetch business licenses: {e}")
        logger.error(f"Dataset config: {cfg['datasets']['business_licenses']}")
        raise

    # Create empty weekly dataframe since we're not doing weekly aggregation
    lic_weekly = pd.DataFrame(columns=["week_start","community_area","community_area_name","bucket","new_licenses","avg_13w","std_13w","wow","momentum_index"])

    permits_weekly = pd.DataFrame()
    p_df = pd.DataFrame()
    if settings.enable_permits:
        logger.info("Fetching Building Permits...")
        try:
            p_df = fetch_permits(client, cfg, settings.days_lookback)
            logger.info(f"Successfully fetched {len(p_df)} permit records")
        except Exception as e:
            logger.error(f"Failed to fetch building permits: {e}")
            p_df = pd.DataFrame()

        # Create empty weekly dataframe since we're not doing weekly aggregation
        permits_weekly = pd.DataFrame(columns=["week_start","community_area","permits"])

    cta_weekly = pd.DataFrame()
    if settings.enable_cta:
        logger.info("Fetching CTA boardings...")
        try:
            cta_df = fetch_cta(client, cfg, settings.days_lookback)
            logger.info(f"Successfully fetched {len(cta_df)} CTA records")
        except Exception as e:
            logger.error(f"Failed to fetch CTA boardings: {e}")
            cta_df = pd.DataFrame()

        # Create empty weekly dataframe since we're not doing weekly aggregation
        cta_weekly = pd.DataFrame(columns=["week_start", "total_rides"])

    # Create empty summary since we're not doing weekly aggregation
    summary_df = pd.DataFrame(columns=["metric","week_start","community_area_name","value"])
    latest_week = "N/A"

    # Sheets
    logger.info("Writing to Google Sheets...")
    sh = open_sheet(settings.sheet_id, settings.google_creds_path)

    # Write weekly aggregated data
    ws = upsert_worksheet(sh, settings.tab_licenses, rows=max(len(lic_weekly)+10, 100), cols=10)
    overwrite_with_dataframe(ws, lic_weekly)

    if settings.enable_permits:
        ws2 = upsert_worksheet(sh, settings.tab_permits, rows=max(len(permits_weekly)+10, 100), cols=5)
        overwrite_with_dataframe(ws2, permits_weekly)

    if settings.enable_cta:
        ws3 = upsert_worksheet(sh, settings.tab_cta, rows=max(len(cta_weekly)+10, 100), cols=3)
        overwrite_with_dataframe(ws3, cta_weekly)

    ws4 = upsert_worksheet(sh, settings.tab_summary, rows=max(len(summary_df)+10, 100), cols=8)
    overwrite_with_dataframe(ws4, summary_df)

    # Write full expanded datasets
    if not lic_df.empty:
        logger.info(f"Writing full business licenses dataset with {len(lic_df)} records and {len(lic_df.columns)} columns...")
        lic_full_ws = upsert_worksheet(sh, "Business_Licenses_Full", rows=max(len(lic_df)+10, 100), cols=50)
        overwrite_with_dataframe(lic_full_ws, lic_df)

    if settings.enable_permits and not p_df.empty:
        logger.info(f"Writing full building permits dataset with {len(p_df)} records and {len(p_df.columns)} columns...")
        permits_full_ws = upsert_worksheet(sh, "Building_Permits_Full", rows=max(len(p_df)+10, 100), cols=50)
        overwrite_with_dataframe(permits_full_ws, p_df)

    if settings.enable_cta and not cta_df.empty:
        logger.info(f"Writing full CTA dataset with {len(cta_df)} records and {len(cta_df.columns)} columns...")
        cta_full_ws = upsert_worksheet(sh, "CTA_Full", rows=max(len(cta_df)+10, 100), cols=20)
        overwrite_with_dataframe(cta_full_ws, cta_df)

    # Brief
    logger.info("Rendering brief...")
    # Create empty dataframes for brief since we're not doing weekly aggregation
    top_level = pd.DataFrame(columns=["community_area_name", "new_licenses"])
    top_momentum = pd.DataFrame(columns=["community_area_name", "new_licenses"])
    md_path = render_markdown_brief(REPORTS_DIR, latest_week, top_level, top_momentum)
    logger.info(f"Brief saved to {md_path}")
    logger.info("Done.")

if __name__ == "__main__":
    main()
