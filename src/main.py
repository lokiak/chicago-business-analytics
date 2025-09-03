
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent / "shared"))
sys.path.append(str(Path(__file__).parent.parent / "step2_data_ingestion"))

from logging_setup import setup_logger
from config_manager import load_settings, load_datasets_yaml
from socrata_client import SocrataClient
from sheets_client import open_sheet, upsert_worksheet, overwrite_with_dataframe, upsert_to_worksheet, get_date_filtered_data
from schema import SchemaManager

logger = setup_logger()

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

    # Get field names from schema instead of hardcoded list
    field_names = SchemaManager.get_field_names("business_licenses")

    params = {
        "$select": ",".join(field_names),
        "$where": f"{ds['application_type_field']}='{ds['issue_value']}' AND {ds['date_field']} >= '{(datetime.utcnow() - pd.Timedelta(days=days_lookback)).strftime('%Y-%m-%d')}'",
        "$order": f"{ds['date_field']}"
    }

    logger.info(f"Business licenses dataset ID: {ds['id']}")
    logger.info(f"Constructed query parameters: {params}")
    logger.info(f"Date lookback: {days_lookback} days")
    start_date = (datetime.utcnow() - pd.Timedelta(days=days_lookback)).strftime('%Y-%m-%d')
    logger.info(f"Start date: {start_date}")
    logger.info(f"Expanded fields: {len(params['$select'].split(','))} fields selected")

    data = client.get(ds["id"], params)
    logger.info(f"Retrieved {len(data)} license records with expanded fields")

    # Check if we got any data and log the actual fields received
    if data:
        actual_fields = list(data[0].keys()) if data[0] else []
        logger.info(f"Actual fields received: {actual_fields}")

    # No longer saving JSON files locally to save space
    df = pd.DataFrame(data)
    if df.empty:
        return df

    return df

def fetch_permits(client, cfg, days_lookback: int):
    ds = cfg["datasets"]["building_permits"]

    # Get field names from schema instead of hardcoded list
    field_names = SchemaManager.get_field_names("building_permits")

    params = {
        "$select": ",".join(field_names),
        "$where": f"{ds['date_field']} >= '{(datetime.utcnow() - pd.Timedelta(days=days_lookback)).strftime('%Y-%m-%d')}'",
        "$order": f"{ds['date_field']}"
    }
    data = client.get(ds["id"], params)
    logger.info(f"Retrieved {len(data)} permit records with expanded fields")

    # Check if we got any data and log the actual fields received
    if data:
        actual_fields = list(data[0].keys()) if data[0] else []
        logger.info(f"Actual fields received: {actual_fields}")

    # No longer saving JSON files locally to save space
    df = pd.DataFrame(data)
    if df.empty:
        return df

    return df

def fetch_cta(client, cfg, days_lookback: int):
    ds = cfg["datasets"]["cta_boardings"]
    # Use 2 years of data for CTA since dataset may not be updated as frequently
    cta_lookback_days = 730  # 2 years
    cta_start_date = (datetime.utcnow() - pd.Timedelta(days=cta_lookback_days)).strftime('%Y-%m-%d')

    logger.info(f"CTA dataset ID: {ds['id']}")
    logger.info(f"CTA lookback period: {cta_lookback_days} days (2 years)")
    logger.info(f"CTA start date: {cta_start_date}")

    # Get field names from schema instead of hardcoded list
    field_names = SchemaManager.get_field_names("cta_boardings")

    params = {
        "$select": ",".join(field_names),
        "$where": f"{ds['date_field']} >= '{cta_start_date}'",
        "$order": f"{ds['date_field']}"
    }

    logger.info(f"CTA query parameters: {params}")
    data = client.get(ds["id"], params)
    # No longer saving JSON files locally to save space
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df[ds['total_field']] = pd.to_numeric(df[ds['total_field']], errors="coerce").fillna(0).astype(int)
    return df

def flatten_location_data(df):
    """
    Flatten nested location data to make it compatible with Google Sheets
    """
    df_flat = df.copy()

    # Check if 'location' column exists and has nested data
    if 'location' in df_flat.columns:
        try:
            # Extract latitude and longitude from location field
            if df_flat['location'].notna().any():
                # Handle the nested location structure
                location_data = df_flat['location'].dropna()

                # Extract coordinates if they exist
                if not location_data.empty:
                    # Create new flattened columns
                    df_flat['location_latitude'] = None
                    df_flat['location_longitude'] = None
                    df_flat['location_human_address'] = None

                    # Process each location entry
                    for idx, loc in location_data.items():
                        if isinstance(loc, dict):
                            if 'latitude' in loc:
                                df_flat.at[idx, 'location_latitude'] = loc['latitude']
                            if 'longitude' in loc:
                                df_flat.at[idx, 'location_longitude'] = loc['longitude']
                            if 'human_address' in loc:
                                df_flat.at[idx, 'location_human_address'] = str(loc['human_address'])

                    # Drop the original nested location column
                    df_flat = df_flat.drop(columns=['location'])

                    logger.info("Successfully flattened location data")
        except Exception as e:
            logger.warning(f"Could not flatten location data: {e}")
            # If flattening fails, just drop the location column
            if 'location' in df_flat.columns:
                df_flat = df_flat.drop(columns=['location'])

    return df_flat

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
    # Set latest_week to current date for brief generation
    from datetime import datetime
    latest_week = datetime.utcnow()

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

    # Write full expanded datasets using dynamic updates (upsert)
    raw_datasets = {}

    if not lic_df.empty:
        logger.info(f"Upserting business licenses dataset with {len(lic_df)} records and {len(lic_df.columns)} columns...")
        # Flatten location data before writing
        lic_df_flat = flatten_location_data(lic_df)
        lic_full_ws = upsert_worksheet(sh, "Business_Licenses_Full", rows=max(len(lic_df_flat)+10, 1000), cols=50)

        # Upsert using unique identifier (id field)
        upsert_to_worksheet(lic_full_ws, lic_df_flat, key_columns=['id'])
        raw_datasets['business_licenses'] = lic_df_flat

    if settings.enable_permits and not p_df.empty:
        logger.info(f"Upserting building permits dataset with {len(p_df)} records and {len(p_df.columns)} columns...")
        # Flatten location data before writing
        p_df_flat = flatten_location_data(p_df)
        permits_full_ws = upsert_worksheet(sh, "Building_Permits_Full", rows=max(len(p_df_flat)+10, 1000), cols=50)

        # Upsert using unique identifier (id field)
        upsert_to_worksheet(permits_full_ws, p_df_flat, key_columns=['id'])
        raw_datasets['building_permits'] = p_df_flat

    if settings.enable_cta and not cta_df.empty:
        logger.info(f"Upserting CTA dataset with {len(cta_df)} records and {len(cta_df.columns)} columns...")
        cta_full_ws = upsert_worksheet(sh, "CTA_Full", rows=max(len(cta_df)+10, 1000), cols=20)

        # Upsert using service date as unique identifier
        upsert_to_worksheet(cta_full_ws, cta_df, key_columns=['service_date'])
        raw_datasets['cta_boardings'] = cta_df

    # NEW: Great Expectations Data Cleaning Integration
    if raw_datasets:
        logger.info("🚀 Running Great Expectations data cleaning pipeline...")
        try:
            # Import GX integration
            sys.path.append(str(Path(__file__).parent.parent / "step3_transform_model"))
            from pipeline_integration import enhanced_clean_and_save

            # Run GX cleaning and save to sheets
            cleaned_datasets, cleaning_report = enhanced_clean_and_save(
                raw_datasets,
                use_gx=True,
                save_to_sheets=True
            )

            logger.info(f"✅ GX cleaning completed successfully!")
            logger.info(f"   Strategy: {cleaning_report.get('strategy_used', 'Unknown')}")
            logger.info(f"   Datasets processed: {len(cleaning_report.get('datasets_processed', []))}")
            logger.info(f"   Sheets saved: {cleaning_report.get('save_success', False)}")

            # Log cleaning results
            for dataset_result in cleaning_report.get('datasets_processed', []):
                name = dataset_result['name']
                success = "✅" if dataset_result['success'] else "❌"
                original_shape = dataset_result['original_shape']
                cleaned_shape = dataset_result['cleaned_shape']
                logger.info(f"   {success} {name}: {original_shape} → {cleaned_shape}")

        except ImportError:
            logger.warning("⚠️  Great Expectations modules not available - skipping data cleaning")
        except Exception as e:
            logger.error(f"❌ GX data cleaning failed: {e}")
            logger.error("   Raw data has been saved, but cleaning step failed")

    # Brief generation temporarily disabled (functionality moved to step5)
    logger.info("Brief generation skipped - will be implemented in step5_visualize_report")
    logger.info("Done.")

if __name__ == "__main__":
    main()
