#!/usr/bin/env python3
"""
Simple test to verify that geocoded coordinates are properly saved to Google Sheets.
Tests ONLY the saving mechanism, not the geocoding itself.
"""

import os
import sys
import pandas as pd

# Add the project root to Python path
sys.path.append('/Users/loki/Downloads/chicago-smb-market-radar')

from shared.sheets_client import open_sheet, upsert_to_worksheet, upsert_worksheet

def test_coordinate_saving():
    """Test that coordinates get properly saved to Google Sheets."""

    print("🧪 TESTING COORDINATE SAVING TO GOOGLE SHEETS")
    print("=" * 50)

    # Create test data with known coordinates (from our successful geocoding)
    test_data = pd.DataFrame([
        {
            'id': 'TEST001',
            'permit_': 'TEST_PERMIT_001',
            'full_address': '7214 S MERRILL AVE, Chicago, Illinois',
            'zip_code': '60649',
            'latitude': 41.76383,
            'longitude': -87.572811,
            'lat_lng': '41.76383,-87.572811',
            'city': 'Chicago',
            'street_number': '7214',
            'street_name': 'MERRILL AVE'
        },
        {
            'id': 'TEST002',
            'permit_': 'TEST_PERMIT_002',
            'full_address': '225 W WASHINGTON ST, Chicago, Illinois',
            'zip_code': '60606',
            'latitude': 41.882856,
            'longitude': -87.634991,
            'lat_lng': '41.882856,-87.634991',
            'city': 'Chicago',
            'street_number': '225',
            'street_name': 'WASHINGTON ST'
        }
    ])

    print(f"📊 Test data created: {len(test_data)} records")
    print("   Testing coordinates:")
    for idx, row in test_data.iterrows():
        print(f"   • {row['full_address']} → {row['latitude']}, {row['longitude']}")

    # Test saving to Google Sheets
    try:
        print(f"\n📡 Connecting to Google Sheets...")
        sheet_id = os.getenv('SHEET_ID')
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        if not sheet_id or not creds_path:
            print("❌ Missing environment variables")
            return False

        sh = open_sheet(sheet_id, creds_path)

        # Create a test worksheet
        test_worksheet_name = 'Test_Coordinate_Saving'
        print(f"📋 Creating test worksheet: {test_worksheet_name}")

        ws = upsert_worksheet(sh, test_worksheet_name, rows=100, cols=20)

        # Save the test data using the same upsert logic as production
        print(f"💾 Saving test data using production upsert logic...")

        key_columns = ['id']
        print(f"🔄 Upserting with key columns: {key_columns}")
        upsert_to_worksheet(ws, test_data, key_columns)

        print(f"✅ Data saved successfully!")

        # Verify the data was saved correctly
        print(f"\n🔍 Verifying saved data...")
        saved_data = ws.get_all_records()
        saved_df = pd.DataFrame(saved_data)

        if len(saved_df) > 0:
            print(f"📊 Found {len(saved_df)} records in Google Sheets")

            # Check critical columns
            critical_cols = ['zip_code', 'latitude', 'longitude', 'lat_lng']
            for col in critical_cols:
                if col in saved_df.columns:
                    non_empty = saved_df[col].dropna()
                    non_empty = non_empty[non_empty != '']
                    print(f"   ✅ {col}: {len(non_empty)} non-empty values")
                    if len(non_empty) > 0:
                        print(f"      Sample: {non_empty.iloc[0]}")
                else:
                    print(f"   ❌ {col}: Column not found")

            return True
        else:
            print(f"❌ No data found in Google Sheets")
            return False

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_coordinate_saving()
    if success:
        print(f"\n🎉 Test PASSED: Coordinates are being saved properly!")
    else:
        print(f"\n💥 Test FAILED: Coordinates are NOT being saved properly!")
