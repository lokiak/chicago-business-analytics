#!/usr/bin/env python3
"""
Test Google Authentication and API Access
Comprehensive test to debug Google Sheets access issues
"""

import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import gspread

def test_google_auth():
    # Load environment variables
    load_dotenv()

    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    sheet_id = os.getenv('SHEET_ID')

    print(f"🔑 Testing Google Authentication...")
    print(f"Credentials path: {creds_path}")
    print(f"Sheet ID: {sheet_id}")

    # Check if credentials file exists
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return

    print(f"✅ Credentials file exists")

    try:
        # Test basic authentication
        print("\n🔐 Testing service account authentication...")
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        # Test token refresh
        if creds.expired:
            print("🔄 Refreshing expired credentials...")
            creds.refresh(Request())

        print(f"✅ Authentication successful")
        print(f"   Project ID: {creds.project_id}")
        print(f"   Service account email: {creds.service_account_email}")
        print(f"   Token valid: {not creds.expired}")

        # Test Google Sheets API access
        print("\n📊 Testing Google Sheets API access...")
        gc = gspread.authorize(creds)

        # Try to list accessible spreadsheets
        print("📋 Attempting to list accessible spreadsheets...")
        try:
            spreadsheets = gc.openall()
            print(f"✅ Found {len(spreadsheets)} accessible spreadsheets:")
            for i, sh in enumerate(spreadsheets[:5]):  # Show first 5
                print(f"   {i+1}. {sh.title} (ID: {sh.id})")
            if len(spreadsheets) > 5:
                print(f"   ... and {len(spreadsheets) - 5} more")
        except Exception as e:
            print(f"⚠️  Could not list spreadsheets: {e}")

        # Try to access the specific sheet
        print(f"\n🎯 Attempting to access specific sheet: {sheet_id}")
        try:
            sh = gc.open_by_key(sheet_id)
            print(f"✅ Successfully opened sheet: {sh.title}")

            # List worksheets
            worksheets = sh.worksheets()
            print(f"📋 Found {len(worksheets)} worksheets:")
            for ws in worksheets:
                print(f"   - {ws.title}")

        except gspread.SpreadsheetNotFound:
            print(f"❌ Spreadsheet not found. Possible causes:")
            print(f"   1. Sheet ID is incorrect: {sheet_id}")
            print(f"   2. Service account doesn't have access to this sheet")
            print(f"   3. Sheet has been deleted or moved")
        except Exception as e:
            print(f"❌ Error accessing sheet: {e}")

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_google_auth()
