#!/usr/bin/env python3
"""
🚨 EMERGENCY PIPELINE SCRIPT 🚨

Quick-access emergency script for Chicago SMB Market Radar data pipeline issues.

Run this script when:
- GX pipeline fails
- Data corruption is detected
- Performance is severely degraded
- You need immediate fallback to manual cleaning

Usage:
    python emergency_pipeline.py --action health_check
    python emergency_pipeline.py --action manual_fallback
    python emergency_pipeline.py --action full_recovery

Author: Chicago SMB Market Radar Team
Version: 1.0
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

def print_banner():
    """Print emergency banner."""
    print("=" * 70)
    print("🚨 CHICAGO SMB MARKET RADAR - EMERGENCY PIPELINE 🚨")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Emergency procedures activated!")
    print()

def health_check():
    """Perform comprehensive system health check."""
    print("🔍 EMERGENCY HEALTH CHECK")
    print("-" * 30)

    try:
        # Add paths
        sys.path.append('step3_transform_model')
        sys.path.append('shared')
        sys.path.append('step2_data_ingestion')

        # Test GX pipeline
        print("1. Testing GX Pipeline...")
        try:
            from step3_transform_model.gx_data_cleaning import SmartDataCleaner
            import pandas as pd

            cleaner = SmartDataCleaner(enable_monitoring=False)
            # Use realistic test data that matches expected schemas
            test_df = pd.DataFrame({
                'id': ['TEST001', 'TEST002', 'TEST003'],
                'license_code': [123, 456, 789],
                'date_issued': ['2025-01-01', '2025-01-02', '2025-01-03']
            })
            start_time = time.time()
            cleaned = cleaner.execute_smart_cleaning(test_df, 'business_licenses')
            duration = time.time() - start_time

            throughput = len(test_df) / duration if duration > 0 else 0

            if throughput > 1000:
                print("   ✅ GX Pipeline: HEALTHY")
                print(f"   📊 Performance: {throughput:.0f} rows/second")
            else:
                print("   ⚠️  GX Pipeline: DEGRADED PERFORMANCE")
                print(f"   📊 Performance: {throughput:.0f} rows/second (expected >1000)")

        except Exception as e:
            print("   ❌ GX Pipeline: FAILED")
            print(f"   💥 Error: {str(e)}")

        # Test emergency fallback
        print("\n2. Testing Emergency Fallback...")
        try:
            from step3_transform_model.emergency_fallback import EmergencyDataProcessor
            import pandas as pd

            processor = EmergencyDataProcessor(enable_logging=False)
            health_status = processor.emergency_health_check()

            # Test the fallback with realistic data
            test_data = {
                'business_licenses': pd.DataFrame({
                    'id': ['TEST001', 'TEST002', 'TEST003'],
                    'license_code': [123, 456, 789],
                    'date_issued': ['2025-01-01', '2025-01-02', '2025-01-03']
                })
            }
            cleaned = processor.emergency_manual_cleaning(test_data)

            if health_status['fallback_ready']:
                print("   ✅ Emergency Fallback: READY")
                print(f"   📊 Expected Performance: {health_status['estimated_performance']}")
            else:
                print("   ❌ Emergency Fallback: NOT READY")

        except Exception as e:
            print("   ❌ Emergency Fallback: FAILED")
            print(f"   💥 Error: {str(e)}")

        # Test monitoring system
        print("\n3. Testing Monitoring System...")
        try:
            from step3_transform_model.gx_dashboard import GXDashboard

            dashboard = GXDashboard('data/monitoring')

            # Get alerts (this returns a dict with health info)
            alerts = dashboard.check_alerts(24)
            alert_status = alerts.get('alert_status', 'RED')

            # Convert alert status to health score
            health_score = {'GREEN': 1.0, 'YELLOW': 0.6, 'RED': 0.2}.get(alert_status, 0.0)

            if health_score > 0.8:
                print("   ✅ Monitoring System: HEALTHY")
                print(f"   📊 Alert Status: {alert_status}")
                print(f"   📊 Health Score: {health_score:.2f}")
            else:
                print("   ⚠️  Monitoring System: DEGRADED")
                print(f"   📊 Alert Status: {alert_status}")
                print(f"   📊 Health Score: {health_score:.2f} (expected >0.8)")

        except Exception as e:
            print("   ❌ Monitoring System: FAILED")
            print(f"   💥 Error: {str(e)}")

        # Test data access
        print("\n4. Testing Data Access...")
        try:
            from config_manager import load_settings
            from sheets_client import open_sheet

            settings = load_settings()
            sh = open_sheet(settings.sheet_id, settings.google_creds_path)

            print("   ✅ Google Sheets: ACCESSIBLE")
            print(f"   📊 Sheet ID: {settings.sheet_id[:20]}...")

        except Exception as e:
            print("   ❌ Google Sheets: FAILED")
            print(f"   💥 Error: {str(e)}")

        print("\n🎯 HEALTH CHECK COMPLETE")

    except Exception as e:
        print(f"\n❌ HEALTH CHECK FAILED: {str(e)}")
        return False

    return True

def manual_fallback():
    """Execute manual fallback cleaning procedure."""
    print("🔄 MANUAL FALLBACK PROCEDURE")
    print("-" * 30)

    try:
        sys.path.append('step3_transform_model')
        sys.path.append('shared')
        sys.path.append('step2_data_ingestion')

        from step3_transform_model.emergency_fallback import EmergencyDataProcessor
        from config_manager import load_settings
        from sheets_client import open_sheet
        from notebook_utils import load_sheet_data

        # Initialize emergency processor
        processor = EmergencyDataProcessor()

        # Load datasets
        print("1. Loading datasets from Google Sheets...")
        settings = load_settings()
        sh = open_sheet(settings.sheet_id, settings.google_creds_path)

        datasets_config = {
            'business_licenses': 'Business_Licenses_Full',
            'building_permits': 'Building_Permits_Full',
            'cta_boardings': 'CTA_Full'
        }

        datasets = {}
        for dataset_name, sheet_name in datasets_config.items():
            df = load_sheet_data(sh, sheet_name)
            datasets[dataset_name] = df
            print(f"   ✅ Loaded {dataset_name}: {len(df):,} rows")

        # Execute emergency cleaning
        print("\n2. Executing emergency manual cleaning...")
        cleaned_datasets = processor.emergency_manual_cleaning(datasets)

        # Save cleaned data
        print("\n3. Saving cleaned data to Google Sheets...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        sheet_mapping = {
            'business_licenses': f'Business_Licenses_Emergency_{timestamp}',
            'building_permits': f'Building_Permits_Emergency_{timestamp}',
            'cta_boardings': f'CTA_Emergency_{timestamp}'
        }

        from sheets_client import upsert_worksheet, overwrite_with_dataframe

        for dataset_name, df in cleaned_datasets.items():
            sheet_name = sheet_mapping[dataset_name]
            ws = upsert_worksheet(sh, sheet_name, rows=len(df)+100, cols=len(df.columns)+5)
            overwrite_with_dataframe(ws, df)
            print(f"   ✅ Saved {sheet_name}")

        # Performance report
        report = processor.get_performance_report()
        metrics = report['performance_metrics']

        print(f"\n🎯 MANUAL FALLBACK COMPLETE")
        print(f"   📊 Total rows processed: {metrics.get('total_rows', 0):,}")
        print(f"   ⏱️  Duration: {metrics.get('duration_seconds', 0):.2f}s")
        print(f"   📈 Throughput: {metrics.get('throughput_rows_per_second', 0):.0f} rows/second")
        print(f"   ✅ Success rate: {metrics.get('success_rate', 0):.1f}%")

        return True

    except Exception as e:
        print(f"\n❌ MANUAL FALLBACK FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def full_recovery():
    """Execute complete emergency data recovery."""
    print("🚨 FULL EMERGENCY RECOVERY")
    print("-" * 30)

    try:
        sys.path.append('step3_transform_model')
        from step3_transform_model.emergency_fallback import EmergencyDataProcessor

        processor = EmergencyDataProcessor()

        print("Initiating complete data recovery...")
        print("This will:")
        print("  - Fetch fresh data from Google Sheets")
        print("  - Apply emergency manual cleaning")
        print("  - Save to timestamped recovery sheets")
        print("  - Generate recovery report")

        confirm = input("\nContinue with full recovery? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Recovery cancelled.")
            return False

        # Execute recovery
        recovered_datasets = processor.emergency_data_recovery()

        # Generate report
        report = processor.get_performance_report()

        print(f"\n🎯 FULL RECOVERY COMPLETE")
        print(f"   📊 Datasets recovered: {len(recovered_datasets)}")

        for dataset_name, df in recovered_datasets.items():
            print(f"   📋 {dataset_name}: {len(df):,} rows")

        return True

    except Exception as e:
        print(f"\n❌ FULL RECOVERY FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main emergency script entry point."""
    parser = argparse.ArgumentParser(
        description="Emergency pipeline procedures for Chicago SMB Market Radar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python emergency_pipeline.py --action health_check
    python emergency_pipeline.py --action manual_fallback
    python emergency_pipeline.py --action full_recovery

Actions:
    health_check    - Check system health (GX, fallback, monitoring)
    manual_fallback - Switch to manual cleaning pipeline
    full_recovery   - Complete emergency data recovery
        """
    )

    parser.add_argument(
        '--action',
        choices=['health_check', 'manual_fallback', 'full_recovery'],
        required=True,
        help='Emergency action to perform'
    )

    args = parser.parse_args()

    print_banner()

    success = False

    if args.action == 'health_check':
        success = health_check()
    elif args.action == 'manual_fallback':
        success = manual_fallback()
    elif args.action == 'full_recovery':
        success = full_recovery()

    print()
    if success:
        print("✅ Emergency procedure completed successfully!")
    else:
        print("❌ Emergency procedure failed!")
        print("📞 Escalate to technical team or check logs for details")

    print("=" * 70)

if __name__ == "__main__":
    main()
