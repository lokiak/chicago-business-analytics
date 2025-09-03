#!/usr/bin/env python3
"""
Refresh Pickle Cache Script

This script safely refreshes the pickle cache files that have numpy compatibility issues.
It backs up the old files and creates new ones with the current environment.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "shared"))
sys.path.append(str(project_root / "step2_data_ingestion"))

def backup_old_cache():
    """Create backups of existing pickle files."""
    cache_dir = project_root / "step3_transform_model" / "data" / "processed"
    backup_dir = cache_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    cache_files = [
        'licenses_df.pkl',
        'permits_df.pkl',
        'cta_df.pkl'
    ]

    backed_up_files = []

    if any((cache_dir / f).exists() for f in cache_files):
        backup_dir.mkdir(exist_ok=True)
        print(f"📦 Creating backup directory: {backup_dir}")

        for file_name in cache_files:
            file_path = cache_dir / file_name
            if file_path.exists():
                backup_path = backup_dir / file_name
                shutil.copy2(file_path, backup_path)
                backed_up_files.append(file_name)
                print(f"   ✅ Backed up {file_name}")

    return backed_up_files, backup_dir if backed_up_files else None

def refresh_cache_from_sheets():
    """Refresh cache by loading fresh data from Google Sheets."""
    try:
        from notebook_utils import load_sheet_data, save_analysis_results
        from sheets_client import open_sheet
        from config_manager import load_settings

        print("🔄 Loading fresh data from Google Sheets...")

        # Load settings and connect to sheets
        settings = load_settings()
        sh = open_sheet(settings.sheet_id, settings.google_creds_path)

        # Define datasets to refresh
        datasets_config = {
            'business_licenses': {
                'worksheet': 'Business_Licenses_Full',
                'pickle_name': 'licenses_df'
            },
            'building_permits': {
                'worksheet': 'Building_Permits_Full',
                'pickle_name': 'permits_df'
            },
            'cta_boardings': {
                'worksheet': 'CTA_Full',
                'pickle_name': 'cta_df'
            }
        }

        refreshed_count = 0
        cache_dir = "step3_transform_model/data/processed"

        for dataset_name, config in datasets_config.items():
            try:
                print(f"\n📊 Refreshing {dataset_name}...")

                # Load from sheets
                df = load_sheet_data(sh, config['worksheet'])
                print(f"   📥 Loaded {len(df):,} rows from '{config['worksheet']}'")

                # Save with current environment
                save_analysis_results(df, config['pickle_name'], cache_dir)
                print(f"   💾 Cached as {config['pickle_name']}.pkl")

                # Test loading to verify compatibility
                from notebook_utils import load_analysis_results
                test_df = load_analysis_results(config['pickle_name'], cache_dir)
                print(f"   ✅ Verified: {len(test_df):,} rows loaded successfully")

                refreshed_count += 1

            except Exception as e:
                print(f"   ❌ Failed to refresh {dataset_name}: {e}")

        return refreshed_count

    except Exception as e:
        print(f"❌ Cache refresh failed: {e}")
        return 0

def main():
    """Main execution function."""
    print("🚀 PICKLE CACHE REFRESH")
    print("=" * 50)
    print("This script will refresh pickle cache files with current numpy/pandas compatibility")

    # Step 1: Backup existing files
    print("\n📦 STEP 1: Backing up existing cache files...")
    backed_up_files, backup_dir = backup_old_cache()

    if backed_up_files:
        print(f"✅ Backed up {len(backed_up_files)} files to {backup_dir}")

        # Step 2: Remove old cache files
        print("\n🗑️  STEP 2: Removing old cache files...")
        cache_dir = project_root / "step3_transform_model" / "data" / "processed"
        for file_name in backed_up_files:
            file_path = cache_dir / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"   🗑️  Removed {file_name}")
    else:
        print("ℹ️  No existing cache files found to backup")

    # Step 3: Refresh from sheets
    print("\n🔄 STEP 3: Refreshing cache from Google Sheets...")
    refreshed_count = refresh_cache_from_sheets()

    # Summary
    print(f"\n🎯 REFRESH COMPLETE")
    print(f"   Files backed up: {len(backed_up_files) if backed_up_files else 0}")
    print(f"   Files refreshed: {refreshed_count}")

    if backup_dir:
        print(f"   Backup location: {backup_dir}")
        print(f"   (You can delete the backup after confirming everything works)")

    print(f"\n✅ Cache refresh successful! All pickle files now use current numpy/pandas versions.")
    return refreshed_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
