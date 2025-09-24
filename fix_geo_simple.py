#!/usr/bin/env python3
"""
Simple script to fix geo columns by directly updating Google Sheets
Based on the working test_simple_geocoding.py approach
"""
import os
import sys
import pandas as pd
import geocoder
import ssl
import time
import signal

# Add project paths
sys.path.append('shared')
from sheets_client import open_sheet

# SSL fix
ssl._create_default_https_context = ssl._create_unverified_context

# Timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def main():
    print("🔧 SIMPLE GEO COLUMN FIX")
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

        # Find rows that need geocoding (empty geo data)
        needs_fix = []
        for i, row in df.iterrows():
            if (not row.get('full_address') or row.get('full_address') == '') and \
               (not row.get('latitude') or row.get('latitude') == '') and \
               row.get('base_address') and row.get('base_address').strip():
                needs_fix.append(i)

        print(f"🗺️ Found {len(needs_fix)} addresses that need geocoding")

        if not needs_fix:
            print("✅ All addresses already have geo data!")
            return

        # Process only first 10 for quick testing
        batch_size = min(10, len(needs_fix))
        batch_indices = needs_fix[:batch_size]

        print(f"📍 Processing first {batch_size} addresses...")

        # Get column indices for updates
        header_list = list(data[0].keys())
        full_addr_col = header_list.index('full_address') + 1
        lat_col = header_list.index('latitude') + 1
        lng_col = header_list.index('longitude') + 1
        latlng_col = header_list.index('lat_lng') + 1
        zip_col = header_list.index('zip_code') + 1

        geocoded_count = 0

        # Set timeout for entire operation (2 minutes)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(120)  # 2 minute timeout

        try:
            for i, row_idx in enumerate(batch_indices):
                row = df.iloc[row_idx]
                base_addr = row.get('base_address', '')

                print(f"  [{i+1}/{batch_size}] Geocoding: {base_addr}")

                try:
                    full_addr = f"{base_addr}, Chicago, IL"
                    g = geocoder.arcgis(full_addr)

                    if g.ok and g.latlng:
                        lat, lng = g.latlng
                        lat_rounded = round(lat, 6)
                        lng_rounded = round(lng, 6)

                        # Create formatted data
                        full_address = f"{base_addr}, Chicago, Illinois"
                        lat_lng = f"{lat_rounded},{lng_rounded}"
                        zip_code = ""

                        if hasattr(g, 'postal') and g.postal and g.postal.isdigit():
                            zip_code = g.postal
                            full_address = f"{base_addr}, Chicago, Illinois {zip_code}"

                        # Update Google Sheets directly
                        sheets_row = row_idx + 2  # +2 for 1-indexing and header

                        ws.update_cell(sheets_row, full_addr_col, full_address)
                        ws.update_cell(sheets_row, lat_col, str(lat_rounded))
                        ws.update_cell(sheets_row, lng_col, str(lng_rounded))
                        ws.update_cell(sheets_row, latlng_col, lat_lng)
                        if zip_code:
                            ws.update_cell(sheets_row, zip_col, zip_code)

                        geocoded_count += 1
                        print(f"    ✅ {lat_rounded}, {lng_rounded} → Updated row {sheets_row}")

                    else:
                        print(f"    ❌ Geocoding failed")

                    # Rate limiting
                    time.sleep(0.2)

                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    continue

        except TimeoutError:
            print(f"⏰ Timeout reached after processing {geocoded_count} addresses")
        finally:
            signal.alarm(0)  # Cancel timeout

        print(f"\n🎉 Completed!")
        print(f"   📊 Successfully geocoded: {geocoded_count}/{batch_size}")
        print(f"   📍 Check rows 2-{2+batch_size} in Google Sheets for results")
        print(f"   🔄 Run again to process the next batch")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
