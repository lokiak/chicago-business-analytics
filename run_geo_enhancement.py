#!/usr/bin/env python3
"""
Run just the geo enhancement stage on existing building permits data.
This will add zip codes, lat/lng coordinates, and enhanced address fields.
"""

import os
import sys
import pandas as pd

# Add project paths
sys.path.append('step3_transform_model')
sys.path.append('shared')

from gx_data_cleaning import SmartDataCleaner
from pipeline_integration import GXPipelineManager
from sheets_client import open_sheet

def main():
    print("🗺️  BUILDING PERMITS GEO ENHANCEMENT")
    print("=" * 50)

    print("🔧 Step 1: Environment setup...")
    # Set up environment
    sheet_id = os.getenv('SHEET_ID')
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    print(f"   📋 Sheet ID: {sheet_id}")
    print(f"   🔑 Creds path: {creds_path}")

    if not sheet_id:
        print("❌ SHEET_ID environment variable not set!")
        return
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable not set!")
        return

    try:
        print("🔧 Step 2: Connecting to Google Sheets...")
        sh = open_sheet(sheet_id, creds_path)
        print("   ✅ Google Sheets connection successful")

        print("🔧 Step 3: Opening Building_Permits_Full worksheet...")
        ws = sh.worksheet('Building_Permits_Full')
        print("   ✅ Worksheet opened successfully")

        print("🔧 Step 4: Loading data (this may take a moment for large datasets)...")
        data = ws.get_all_records()
        print(f"   ✅ Data loaded: {len(data)} records")

        if not data:
            print("❌ No building permits data found!")
            return

        df = pd.DataFrame(data)
        print(f"   ✅ Loaded {len(df)} building permits records")
        print(f"   📋 Columns: {len(df.columns)}")

        # Show sample addresses before processing
        sample_addresses = []
        for idx, row in df.head(3).iterrows():
            addr_parts = []
            if pd.notna(row.get('street_number')) and str(row.get('street_number')).strip():
                addr_parts.append(str(row['street_number']).strip())
            if pd.notna(row.get('street_direction')) and str(row.get('street_direction')).strip():
                addr_parts.append(str(row['street_direction']).strip())
            if pd.notna(row.get('street_name')) and str(row.get('street_name')).strip():
                addr_parts.append(str(row['street_name']).strip())
            if addr_parts:
                sample_addresses.append(' '.join(addr_parts))

        print(f"   📍 Sample addresses to process: {sample_addresses[:3]}")

        print("🔧 Step 6: Starting GX cleaning with smart geo caching...")

        # Run the smart cleaning with geo enhancement
        print("   🧹 Initializing SmartDataCleaner...")
        cleaner = SmartDataCleaner()
        print("   🚀 Executing smart cleaning...")
        cleaned_df = cleaner.execute_smart_cleaning(df, 'building_permits')
        print("   ✅ Smart cleaning completed")

        print(f"\n📊 Enhancement Results:")
        print(f"   Original columns: {len(df.columns)}")
        print(f"   Enhanced columns: {len(cleaned_df.columns)}")

        # Check what geo columns were added
        geo_columns = ['full_address', 'zip_code', 'latitude', 'longitude', 'lat_lng', 'city']
        added_geo_cols = [col for col in geo_columns if col in cleaned_df.columns]
        print(f"   ✅ Added geo columns: {added_geo_cols}")

        # DEBUGGING: Check if geocoded data is in the returned DataFrame
        print(f"\n🔍 DEBUGGING: Checking geocoded data in returned DataFrame...")
        if 'latitude' in cleaned_df.columns and 'longitude' in cleaned_df.columns:
            # Debug data types
            print(f"   🔍 Latitude dtype: {cleaned_df['latitude'].dtype}")
            print(f"   🔍 Longitude dtype: {cleaned_df['longitude'].dtype}")
            print(f"   🔍 First 10 latitude values (raw): {cleaned_df['latitude'].head(10).tolist()}")
            print(f"   🔍 First 10 longitude values (raw): {cleaned_df['longitude'].head(10).tolist()}")

            # Check for non-null, non-empty latitude values with more specific conditions
            geocoded_mask = (
                cleaned_df['latitude'].notna() &
                (cleaned_df['latitude'] != '') &
                (cleaned_df['latitude'] != 'None') &
                (cleaned_df['latitude'] != None) &
                (cleaned_df['latitude'] != 0) &
                (cleaned_df['latitude'].astype(str) != 'None')
            )
            successful_geocodes = geocoded_mask.sum()
            total_addresses = (cleaned_df['street_number'].notna() &
                             cleaned_df['street_name'].notna()).sum()
            print(f"   📊 Geocoded records found: {successful_geocodes}/{total_addresses} addresses")

            if successful_geocodes > 0:
                print(f"   ✅ SUCCESS: Found geocoded data in DataFrame!")
                # Show some sample geocoded results
                geocoded_samples = cleaned_df[geocoded_mask].head(3)
                for idx, row in geocoded_samples.iterrows():
                    addr = row.get('full_address', 'N/A')
                    lat = row.get('latitude', 'N/A')
                    lng = row.get('longitude', 'N/A')
                    lat_lng = row.get('lat_lng', 'N/A')
                    zip_code = row.get('zip_code', 'N/A')
                    print(f"   📍 Row {idx}: {addr} | {lat}, {lng} | {lat_lng} | Zip: {zip_code}")
            else:
                print(f"   ❌ ERROR: No geocoded data found in returned DataFrame!")
                print(f"   🔍 Checking specific first 10 rows for any non-None values...")
                for i in range(min(10, len(cleaned_df))):
                    lat_val = cleaned_df.iloc[i]['latitude']
                    lng_val = cleaned_df.iloc[i]['longitude']
                    if lat_val is not None and lat_val != '' and str(lat_val) != 'None':
                        print(f"   🎯 FOUND: Row {i} has lat={lat_val}, lng={lng_val}")
        else:
            print(f"   ❌ ERROR: Latitude/longitude columns not found!")

        print("\n💾 Saving enhanced data to Google Sheets...")

        # Use the GX pipeline manager to save to sheets
        gx_manager = GXPipelineManager()
        cleaned_datasets = {'building_permits': cleaned_df}

        success = gx_manager.save_cleaned_data_to_sheets(cleaned_datasets, suffix="_GX_Cleaned")

        if success:
            print("   ✅ Successfully saved enhanced building permits to 'Building_Permits_GX_Cleaned'")
            print(f"   📊 Final dataset: {len(cleaned_df)} rows, {len(cleaned_df.columns)} columns")
            print("\n🎉 Geo enhancement completed successfully!")
        else:
            print("   ❌ Failed to save to Google Sheets")

    except Exception as e:
        print(f"❌ Error during geo enhancement: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # CRITICAL: Cleanup to prevent hanging in GitHub Actions
        print("🧹 Final cleanup...")
        import gc
        gc.collect()
        print("✅ Cleanup completed - script should exit cleanly")

if __name__ == "__main__":
    main()
