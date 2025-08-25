#!/usr/bin/env python3
"""
Test Google Sheets Connection
Simple script to debug the 404 error when trying to access Google Sheets
"""

import os
from dotenv import load_dotenv
from src.sheets import open_sheet

def test_connection():
    # Load environment variables
    load_dotenv()

    sheet_id = os.getenv('SHEET_ID')
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    print(f"Sheet ID: {sheet_id}")
    print(f"Credentials path: {creds_path}")

    # Check if credentials file exists
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return

    print(f"✅ Credentials file exists")

    try:
        print("🔑 Attempting to open Google Sheet...")
        sh = open_sheet(sheet_id, creds_path)
        print(f"✅ Successfully opened sheet: {sh.title}")

        # List all worksheets
        worksheets = sh.worksheets()
        print(f"📋 Found {len(worksheets)} worksheets:")
        for ws in worksheets:
            print(f"  - {ws.title}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_connection()
