#!/usr/bin/env python3
"""
Simple test script to geocode a few addresses and update Google Sheets
"""
import os
import sys
import pandas as pd
import geocoder
import ssl

# Add project paths
sys.path.append('shared')
from sheets_client import open_sheet

# SSL fix
ssl._create_default_https_context = ssl._create_unverified_context

def main():
    print("🧪 SIMPLE GEOCODING TEST")
    print("=" * 30)

    # Environment setup
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    sheet_id = os.getenv('SHEET_ID')

    if not creds_path or not sheet_id:
        print("❌ Environment variables not set!")
        return

    try:
        # Load current data
        sh = open_sheet(sheet_id, creds_path)
        ws = sh.worksheet('Building_Permits_GX_Cleaned')
        data = ws.get_all_records()

        if not data:
            print("❌ No data found!")
            return

        df = pd.DataFrame(data)
        print(f"📊 Loaded {len(df)} records")

        # Test on first 5 addresses only
        test_df = df.head(5).copy()

        print("🗺️ Geocoding first 5 addresses...")

        for idx, row in test_df.iterrows():
            base_addr = row.get('base_address', '')
            if base_addr and base_addr.strip():
                print(f"  Geocoding: {base_addr}")

                try:
                    full_addr = f"{base_addr}, Chicago, IL"
                    g = geocoder.arcgis(full_addr)

                    if g.ok:
                        lat, lng = g.latlng
                        test_df.at[idx, 'latitude'] = round(lat, 6)
                        test_df.at[idx, 'longitude'] = round(lng, 6)
                        test_df.at[idx, 'lat_lng'] = f"{round(lat, 6)},{round(lng, 6)}"
                        test_df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois"

                        # Extract ZIP code from result
                        if g.postal and g.postal.isdigit():
                            test_df.at[idx, 'zip_code'] = g.postal
                            test_df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois {g.postal}"

                        print(f"    ✅ {lat:.6f}, {lng:.6f}")
                    else:
                        print(f"    ❌ Failed")

                except Exception as e:
                    print(f"    ❌ Error: {e}")

        # Update just these 5 rows in Google Sheets
        print("💾 Updating Google Sheets...")

        # Update the specific rows
        for i, (idx, row) in enumerate(test_df.iterrows()):
            row_num = idx + 2  # +2 because sheets is 1-indexed and has header

            # Find column indices for geo fields
            header = data[0].keys()  # Get header from original data
            header_list = list(header)

            full_addr_col = header_list.index('full_address') + 1 if 'full_address' in header_list else None
            lat_col = header_list.index('latitude') + 1 if 'latitude' in header_list else None
            lng_col = header_list.index('longitude') + 1 if 'longitude' in header_list else None
            latlng_col = header_list.index('lat_lng') + 1 if 'lat_lng' in header_list else None
            zip_col = header_list.index('zip_code') + 1 if 'zip_code' in header_list else None

            # Update each field if column exists
            if full_addr_col and pd.notna(row['full_address']):
                ws.update_cell(row_num, full_addr_col, str(row['full_address']))
            if lat_col and pd.notna(row['latitude']):
                ws.update_cell(row_num, lat_col, str(row['latitude']))
            if lng_col and pd.notna(row['longitude']):
                ws.update_cell(row_num, lng_col, str(row['longitude']))
            if latlng_col and pd.notna(row['lat_lng']):
                ws.update_cell(row_num, latlng_col, str(row['lat_lng']))
            if zip_col and pd.notna(row['zip_code']):
                ws.update_cell(row_num, zip_col, str(row['zip_code']))

            print(f"  ✅ Updated row {row_num}")

        print("🎉 Test geocoding completed!")
        print("Check the first 5 rows in Google Sheets for results")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
