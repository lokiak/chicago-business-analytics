#!/usr/bin/env python3
"""
Simple local test to verify everything works before GitHub Actions
"""

import os
import sys
import tempfile
import base64
import json
from pathlib import Path

# Clean base64 credentials (from the file we just generated)
CLEAN_BASE64 = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAicmF2ZW5zd29vZC1jb25zdWx0aW5nIiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiYzNhMmU2MGQ2N2E5OGNhMTRhZGM1Yjg0NGIxM2YwNzA2MzE4NDFmYSIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZRSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2N3Z2dTakFnRUFBb0lCQVFET2NiYStQTlluTHN1dVxuUFNYOWFJWGxyRXcwSHZsTVFRMU9DdERJWGM4VklobGZraHFJbGp6ZEVCMFRubnI3WExRL0xIcDlZakJ0cTVZVFxuaXhSZjRKZG52Y1NEeCtmSEVOdjlLd3ZiUG9WN3JXNUNlbG1XRTR4aDZzeXpTM1AwTnRWcFEraVNmMExMbFRYS1xuZkFWbnN2VWdUT2szcGpBcTFzbmFQYXBVeXY4M0xtV05nZUpwZHJoelRqS1BBWFBZaVg1Z1pTMmxCZzIyM1R0N1xuSEpCNy80ZVdDTWpOK0ZrN3VvdUlQZXRjQzFOUUE4MXBON1JpNTNnaWEyak1zTTd6aXZ1VzM0aDkxMVZYZW5qdlxueXhvd0hhdCtTOWxWQ01qRWVEVEFuREFvWkp1NWtyUFgrZVg5ZEo5dXdrbER1VGVsOXZaZTZGYkh1SnNITWxqN1xuY1BXQ1ExUmpBZ01CQUFFQ2dnRUFOZVI0bk1QNzhlR2srVmpzTkhHWFZzUTZabmJaaEw4TXJwMWpNSk5Rcm9jbVxuMFl5dUVZOEsxM2pQNW1HK1lDVXN4cnNoUk44Zm5sbW5SWFhPdlZLL282em1BckxxZmt5WDZValdBUWVheUJVWFxuemhIcmxpS0hTTDZIYnB6WmFkendyRmkyZTV2dVA0QTF1U1RVTW1TRTJraEpyNlhhT0N5M0tCcGwvMW00ODFuWVxuemV3MnpTMmNXMkhiZTZJUktDU09TQmlrbnBpemR4U0Y0a3FvWExVdlVBbHVsZUxsU0xGSDRUMytyZjJPcFduV1xualQvb1Rvb1RiRG92VmcvOEhXcTRsekZOU3lHcldjVmRER055Sk5QcHQzTlhkV2NjVXVNRXh6aWxuRDNMR09BbFxuMm9XRnJSRm5hS0ZZVnYra2ZvYWF5U2FTeFVqQ082RlRiOEREaHhXam9RS0JnUURwQWpueDhBMS9kSVNtNkM5elxuVnNpSWxOMVZBUUFJVFkyVjhTR1d4MDA1NFlVRHowdDlkTWM4Ym1uWlN3am4zNkpXMVlBeTNlR1hla1dLMi9rVVxuL0Z2WDNSbFltajFTVHcyK2pCNktkb3J1cE8yd2Q2bVQwdlM5MHJGY1ZXR2F0UVZsaE1vSDk0a1BoZHRTNy9TOFxuZXdCSUVCTDYvVnkyQnR4NzJFMXU1VTBjZ3dLQmdRRGkwSGljbDJ2WklnSDdVTW0zSjB3YTdvWUVlc3QyRkxzcVxuaHozUWREZ0Y0THd6ckh0aklHWnpYeVB3UCtMUXFwTEVrbkFsSHpUd0VtNUg3OUNvLzZYNlo5L0FpbDVPOXhZbFxuUU8zbjRKRVhUOWkxNmErSXRVZnlDMEx4QlBYemJiWGw1TFVIeU04SzJ2dUZzMXhuWWtCb2NxWjI5V0RKaTVjM1xuRXJpVUtpa2lvUUtCZ0RBM3o3bnJUVC9FNHZhUE1kS1NjT2tpdFRLMEJFZXpsTXNrblNqUWtZQ2ExS1hYTGU0R1xuVG55STlNcU1wb2tsVkRqWDhiR1ZET3dGMTRKR3h5SzZubDdyV0NWbnRhemt3eGxkY2F5Qm4zcUhFdERqMG1uT1xueStyRVFRTzBmNEErV2FHS2V5eHU0eVFkTlNmU2xEaTAwM2dXSzNkWkd1aG9QeFE1ekx4WUl6NzFBb0dCQUpmK1xuZURVSHpBQVFLQi9RUGJ6OUdxVVpucm0xeUU3ekNaSXdXeDRzSTdiY3FZSS9YZGhKeUI0Y2JhcjhSUFRzdWJuOVxuSUNYZ1NjdHZybk9Lbzl2OHBhK3VtR1VnMUo0Nk9wN3dhZjF2b2d0ck9LQi9YMkJQaTAwS2V1dWxGV1R4Nm1tS1xuNEQyOU5mSGlXWmQ1WUx6dlBKWkI3b2ZkVytUMEpIdUZraWZJTVJUQkFvR0FHcEdvajlSOVF3TTd4N045c011TVxuK2wzeVFSZit4UUlpMGx6bTU3ek5jRi9JaGxQNC9icjY2SlpkVkQ5Y25FTzZpUFd6eXRhU3o0SDVNTUxSOVZOcVxuV3ZHRnhlLzBqc0ovV1BKL1U2MHFiQjNtWlJpMmZTR2Funcng3YnUyVHd2Qm1USzhZdmNGTUdXNkNsYnFwSzQzQlxuL0wzeGtmeVBydzR3K2d0SVcvSzBEdzg9XG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4iLAogICJjbGllbnRfZW1haWwiOiAiZ2VuZXJhbC1hZG1pbi1yYXZlbnN3b29kQHJhdmVuc3dvb2QtY29uc3VsdGluZy5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgImNsaWVudF9pZCI6ICIxMDY1ODU1MzY1OTc1MjUwNjUzMTYiLAogICJhdXRoX3VyaSI6ICJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20vby9vYXV0aDIvYXV0aCIsCiAgInRva2VuX3VyaSI6ICJodHRwczovL29hdXRoMi5nb29nbGVhcGlzLmNvbS90b2tlbiIsCiAgImF1dGhfcHJvdmlkZXJfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9vYXV0aDIvdjEvY2VydHMiLAogICJjbGllbnRfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9yb2JvdC92MS9tZXRhZGF0YS94NTA5L2dlbmVyYWwtYWRtaW4tcmF2ZW5zd29vZCU0MHJhdmVuc3dvb2QtY29uc3VsdGluZy5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo="

# Google Sheet ID from user
SHEET_ID = "1R0LEXCxdEVCtslpaRz8A0ZjSkFKYestD01Z1y-5CgBE"

def setup_credentials():
    """Setup Google credentials like GitHub Actions does"""
    print("🔐 Setting up Google credentials...")

    # Create temporary file for credentials (like GitHub Actions does)
    temp_dir = tempfile.gettempdir()
    creds_file = os.path.join(temp_dir, "sa.json")

    try:
        # Decode base64 credentials
        decoded_creds = base64.b64decode(CLEAN_BASE64)

        # Write to file
        with open(creds_file, 'wb') as f:
            f.write(decoded_creds)

        # Set restrictive permissions
        os.chmod(creds_file, 0o600)

        # Validate JSON
        with open(creds_file, 'r') as f:
            json.load(f)

        print(f"✅ Credentials file created: {creds_file}")
        return creds_file

    except Exception as e:
        print(f"❌ Failed to setup credentials: {e}")
        return None

def setup_environment(creds_file):
    """Set up environment variables like GitHub Actions"""
    print("🌍 Setting up environment variables...")

    env_vars = {
        'GOOGLE_APPLICATION_CREDENTIALS': creds_file,
        'SHEET_ID': SHEET_ID,
        'DAYS_LOOKBACK': '90',
        'WEEKLY_BASELINE_WEEKS': '13',
        'ENABLE_PERMITS': 'true',
        'ENABLE_CTA': 'true'
    }

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ {key}: {value}")

    return True

def test_google_auth():
    """Test Google authentication"""
    print("\n🔑 Testing Google authentication...")

    try:
        from google.auth import default
        credentials, project = default()
        print(f"✅ Authentication successful")
        print(f"✅ Project: {project}")

        # Test service account details
        creds_file = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        with open(creds_file, 'r') as f:
            sa_info = json.load(f)
        print(f"✅ Service account: {sa_info['client_email']}")

        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_google_sheets():
    """Test Google Sheets access"""
    print("\n📊 Testing Google Sheets access...")

    try:
        import gspread
        from google.auth import default

        credentials, _ = default()
        gc = gspread.authorize(credentials)

        # Try to open the sheet
        sheet = gc.open_by_key(SHEET_ID)
        print(f"✅ Successfully opened sheet: {sheet.title}")

        # List worksheets
        worksheets = sheet.worksheets()
        print(f"✅ Found {len(worksheets)} worksheets:")
        for ws in worksheets:
            print(f"   - {ws.title}")

        return True
    except Exception as e:
        print(f"❌ Sheets access failed: {e}")
        return False

def test_pipeline_imports():
    """Test that pipeline can import properly"""
    print("\n📦 Testing pipeline imports...")

    try:
        # Test main pipeline imports
        import src.main
        print("✅ src.main imported successfully")

        # Test other key modules
        import step2_data_ingestion.socrata_client
        print("✅ socrata_client imported successfully")

        import step3_transform_model.gx_data_cleaning
        print("✅ gx_data_cleaning imported successfully")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def run_quick_pipeline_test():
    """Run a quick test of pipeline components"""
    print("\n🚀 Running quick pipeline test...")

    try:
        # Import and test a simple component
        from step2_data_ingestion.socrata_client import SocrataClient

        client = SocrataClient()
        print("✅ SocrataClient created successfully")

        # Test configuration loading
        from step2_data_ingestion.config_manager import ConfigManager
        config = ConfigManager()
        print("✅ ConfigManager loaded successfully")

        return True
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

def main():
    """Run comprehensive local testing"""
    print("🧪 GitHub Actions Local Testing Suite")
    print("=" * 60)

    # Setup credentials
    creds_file = setup_credentials()
    if not creds_file:
        return 1

    # Setup environment
    if not setup_environment(creds_file):
        return 1

    # Run tests
    tests = [
        test_google_auth,
        test_google_sheets,
        test_pipeline_imports,
        run_quick_pipeline_test
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All tests passed ({passed}/{total})!")
        print("✅ Ready for GitHub Actions deployment!")

        # Ask if user wants to run full pipeline
        print("\n" + "=" * 40)
        response = input("Run full pipeline? (y/N): ").strip().lower()
        if response == 'y':
            print("🚀 Running full pipeline...")
            try:
                import src.main
                # Note: This would run the actual pipeline
                print("⚠️  Full pipeline would run here")
                print("   (Skipped for safety - remove this line to actually run)")
            except Exception as e:
                print(f"❌ Full pipeline failed: {e}")
                return 1

        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
        print("Fix issues before deploying to GitHub Actions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
