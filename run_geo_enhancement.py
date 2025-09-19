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

    # Set up environment
    sheet_id = os.getenv('SHEET_ID')
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    if not sheet_id:
        print("❌ SHEET_ID environment variable not set!")
        return
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable not set!")
        return

    try:
        print("📊 Loading existing building permits data from Google Sheets...")
        sh = open_sheet(sheet_id, creds_path)

        # Load raw building permits data
        ws = sh.worksheet('Building_Permits_Full')
        data = ws.get_all_records()

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

        print("\n🚀 Running GX cleaning with smart geo caching...")

        # Run the smart cleaning with geo enhancement
        cleaner = SmartDataCleaner()
        cleaned_df = cleaner.execute_smart_cleaning(df, 'building_permits')

        print(f"\n📊 Enhancement Results:")
        print(f"   Original columns: {len(df.columns)}")
        print(f"   Enhanced columns: {len(cleaned_df.columns)}")

        # Check what geo columns were added
        geo_columns = ['full_address', 'zip_code', 'latitude', 'longitude', 'lat_lng', 'city']
        added_geo_cols = [col for col in geo_columns if col in cleaned_df.columns]
        print(f"   ✅ Added geo columns: {added_geo_cols}")

        # Check geocoding success rate
        if 'latitude' in cleaned_df.columns and 'longitude' in cleaned_df.columns:
            successful_geocodes = cleaned_df[['latitude', 'longitude']].notna().all(axis=1).sum()
            total_addresses = (cleaned_df['street_number'].notna() &
                             cleaned_df['street_name'].notna()).sum()
            print(f"   🎯 Geocoding success: {successful_geocodes}/{total_addresses} addresses")

            # Show some sample results
            geocoded_samples = cleaned_df[cleaned_df['latitude'].notna()].head(3)
            for idx, row in geocoded_samples.iterrows():
                addr = row.get('full_address', 'N/A')
                lat_lng = row.get('lat_lng', 'N/A')
                zip_code = row.get('zip_code', 'N/A')
                print(f"   📍 {addr} | {lat_lng} | Zip: {zip_code}")

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

if __name__ == "__main__":
    main()
