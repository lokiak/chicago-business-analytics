he f"""
Production Monitoring Example for GX Pipeline

This example shows how to integrate monitoring and alerting into your
production data pipeline workflows.
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.append('step3_transform_model')
sys.path.append('step2_data_ingestion')
sys.path.append('shared')

def run_monitored_pipeline():
    """Example of running the GX pipeline with full monitoring."""

    print("🔍 PRODUCTION GX PIPELINE WITH MONITORING")
    print("=" * 50)

    try:
        # Import required modules
        from config_manager import load_settings
        from sheets_client import open_sheet
        from notebook_utils import load_sheet_data
        from gx_data_cleaning import SmartDataCleaner
        from gx_dashboard import create_dashboard, check_pipeline_health

        # Load settings and data
        print("📊 Loading data...")
        settings = load_settings()
        sh = open_sheet(settings.sheet_id, settings.google_creds_path)

        # Initialize monitoring
        print("🔍 Initializing monitoring...")
        dashboard = create_dashboard()

        # Run pipeline with monitoring for each dataset
        datasets_to_process = [
            ('Business_Licenses_Full', 'business_licenses'),
            ('Building_Permits_Full', 'building_permits'),
            ('CTA_Full', 'cta_boardings')
        ]

        cleaner = SmartDataCleaner(enable_monitoring=True)

        for sheet_name, dataset_name in datasets_to_process:
            print(f"\n🧹 Processing {dataset_name}...")

            # Load data (sample for demo)
            df = load_sheet_data(sh, sheet_name)
            sample_df = df.head(10)  # Use sample for demo

            # Run monitored cleaning
            cleaned_df = cleaner.execute_smart_cleaning(sample_df, dataset_name)

            print(f"✅ {dataset_name} processed: {cleaned_df.shape}")

        # Check health status after processing
        print("\n🔍 CHECKING PIPELINE HEALTH...")
        health_status = check_pipeline_health(1)  # Last 1 hour

        print(f"Health Status: {health_status['alert_status']}")

        if health_status['alerts_triggered']:
            print("\n🚨 ALERTS DETECTED:")
            for alert in health_status['alerts_triggered']:
                print(f"   • {alert['type']}: {alert['message']}")

        if health_status['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for rec in health_status['recommendations'][:3]:
                print(f"   • {rec}")

        # Generate health report
        print("\n📊 GENERATING HEALTH REPORT...")
        report = dashboard.generate_health_report(1)
        print(report)

        # Export metrics for analysis
        print("📈 Exporting metrics...")
        csv_path = dashboard.export_metrics_to_csv(24, 'production_metrics.csv')
        if csv_path:
            print(f"✅ Metrics exported to: {csv_path}")

        print("\n🎉 MONITORED PIPELINE EXECUTION COMPLETE!")

    except Exception as e:
        print(f"❌ Pipeline failed: {e}")

        # Even on failure, try to generate a health report
        try:
            dashboard = create_dashboard()
            report = dashboard.generate_health_report(1)
            print("\n📊 FAILURE ANALYSIS REPORT:")
            print(report)
        except:
            pass

        raise e


def setup_monitoring_alerts():
    """Example of setting up custom alert thresholds."""

    print("⚙️ SETTING UP CUSTOM MONITORING ALERTS")
    print("=" * 50)

    from gx_dashboard import create_dashboard

    # Create dashboard with custom thresholds
    dashboard = create_dashboard()

    # Customize alert thresholds
    dashboard.alert_thresholds = {
        'min_success_rate': 80.0,          # Stricter success rate
        'max_duration_seconds': 30.0,      # Faster response time
        'min_quality_score': 70.0,         # Higher quality standard
        'max_error_rate': 5.0,             # Lower error tolerance
    }

    print("🎯 Custom Alert Thresholds Set:")
    for key, value in dashboard.alert_thresholds.items():
        print(f"   {key}: {value}")

    # Test alerts
    alerts = dashboard.check_alerts(24)
    print(f"\nCurrent Alert Status: {alerts['alert_status']}")

    return dashboard


def monitor_specific_dataset(dataset_name: str, hours: int = 24):
    """Monitor a specific dataset's performance."""

    print(f"🔍 MONITORING DATASET: {dataset_name.upper()}")
    print("=" * 50)

    from gx_dashboard import create_dashboard
    import json

    dashboard = create_dashboard()
    recent_metrics = dashboard.load_recent_metrics(hours)

    # Filter for specific dataset
    dataset_metrics = [m for m in recent_metrics if m.get('dataset_name') == dataset_name]

    if not dataset_metrics:
        print(f"❌ No recent data found for {dataset_name}")
        return

    print(f"📊 Found {len(dataset_metrics)} executions for {dataset_name}")

    # Calculate dataset-specific stats
    success_rate = len([m for m in dataset_metrics if m.get('status') == 'SUCCESS']) / len(dataset_metrics) * 100
    avg_duration = sum(m.get('duration_seconds', 0) for m in dataset_metrics) / len(dataset_metrics)
    avg_transform_rate = sum(m.get('transformation_success_rate', 0) for m in dataset_metrics) / len(dataset_metrics)

    print(f"\n📈 DATASET PERFORMANCE:")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Avg Duration: {avg_duration:.2f}s")
    print(f"   Avg Transform Rate: {avg_transform_rate:.1f}%")

    # Show recent executions
    print(f"\n📋 RECENT EXECUTIONS:")
    for metric in dataset_metrics[-3:]:
        timestamp = metric['timestamp']
        status = metric.get('status', 'UNKNOWN')
        duration = metric.get('duration_seconds', 0)
        transform_rate = metric.get('transformation_success_rate', 0)

        status_icon = '✅' if status == 'SUCCESS' else '❌'
        print(f"   {status_icon} {timestamp}: {duration:.2f}s, {transform_rate:.1f}% transforms")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='GX Pipeline Monitoring Examples')
    parser.add_argument('--action', choices=['pipeline', 'alerts', 'dataset'],
                       default='pipeline', help='Action to perform')
    parser.add_argument('--dataset', type=str, help='Dataset name for dataset monitoring')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back')

    args = parser.parse_args()

    if args.action == 'pipeline':
        run_monitored_pipeline()
    elif args.action == 'alerts':
        setup_monitoring_alerts()
    elif args.action == 'dataset':
        if args.dataset:
            monitor_specific_dataset(args.dataset, args.hours)
        else:
            print("❌ Please specify --dataset for dataset monitoring")
