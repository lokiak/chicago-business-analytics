"""
GX Pipeline Dashboard and Alerting System

Provides dashboard utilities and alerting mechanisms for monitoring
the Great Expectations data cleaning pipeline health and performance.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

class GXDashboard:
    """
    Dashboard and alerting system for GX pipeline monitoring.

    Features:
    - Performance dashboard generation
    - Alert threshold monitoring
    - Health check reporting
    - Historical trend analysis
    """

    def __init__(self, monitoring_directory: str = "data/monitoring"):
        """
        Initialize the dashboard system.

        Args:
            monitoring_directory: Directory containing monitoring data
        """
        self.monitoring_dir = Path(monitoring_directory)
        self.alert_thresholds = {
            'min_success_rate': 70.0,          # Minimum transformation success rate
            'max_duration_seconds': 60.0,      # Maximum acceptable pipeline duration
            'min_quality_score': 60.0,         # Minimum data quality score
            'max_error_rate': 10.0,            # Maximum acceptable error rate
        }

    def load_recent_metrics(self, hours: int = 24) -> List[Dict]:
        """Load metrics from recent pipeline executions."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = []

        # Read all metrics files
        for metrics_file in self.monitoring_dir.glob("metrics_*.json"):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)

                # Parse timestamp and check if within range
                timestamp = datetime.fromisoformat(data['timestamp'])
                if timestamp >= cutoff_time:
                    recent_metrics.append(data)

            except Exception as e:
                logger.warning(f"⚠️ Could not read metrics file {metrics_file}: {e}")

        # Sort by timestamp
        recent_metrics.sort(key=lambda x: x['timestamp'])
        return recent_metrics

    def check_alerts(self, hours: int = 24) -> Dict[str, Any]:
        """
        Check for alert conditions in recent pipeline executions.

        Args:
            hours: Number of hours to look back for alert checking

        Returns:
            Dictionary containing alert status and triggered alerts
        """
        recent_metrics = self.load_recent_metrics(hours)
        alerts = {
            'timestamp': datetime.now().isoformat(),
            'alert_status': 'GREEN',  # GREEN, YELLOW, RED
            'alerts_triggered': [],
            'metrics_summary': {},
            'recommendations': []
        }

        if not recent_metrics:
            alerts['alert_status'] = 'YELLOW'
            alerts['alerts_triggered'].append({
                'type': 'NO_DATA',
                'severity': 'WARNING',
                'message': f'No pipeline executions found in the last {hours} hours'
            })
            return alerts

        # Calculate aggregate metrics
        total_executions = len(recent_metrics)
        failed_executions = [m for m in recent_metrics if m.get('status') == 'FAILED']
        success_rate = ((total_executions - len(failed_executions)) / total_executions) * 100

        # Average metrics
        avg_duration = sum(m.get('duration_seconds', 0) for m in recent_metrics) / len(recent_metrics)
        avg_transformation_rate = sum(m.get('transformation_success_rate', 0) for m in recent_metrics) / len(recent_metrics)

        # Store summary
        alerts['metrics_summary'] = {
            'total_executions': total_executions,
            'execution_success_rate': success_rate,
            'average_duration': avg_duration,
            'average_transformation_rate': avg_transformation_rate,
            'failed_executions': len(failed_executions)
        }

        # Check alert thresholds
        alert_level = 'GREEN'

        # 1. Check execution success rate
        if success_rate < self.alert_thresholds['min_success_rate']:
            alert_level = 'RED'
            alerts['alerts_triggered'].append({
                'type': 'LOW_SUCCESS_RATE',
                'severity': 'CRITICAL',
                'message': f'Pipeline success rate is {success_rate:.1f}% (threshold: {self.alert_thresholds["min_success_rate"]}%)',
                'value': success_rate,
                'threshold': self.alert_thresholds['min_success_rate']
            })

        # 2. Check average duration
        if avg_duration > self.alert_thresholds['max_duration_seconds']:
            alert_level = max(alert_level, 'YELLOW')
            alerts['alerts_triggered'].append({
                'type': 'SLOW_PERFORMANCE',
                'severity': 'WARNING',
                'message': f'Average pipeline duration is {avg_duration:.1f}s (threshold: {self.alert_thresholds["max_duration_seconds"]}s)',
                'value': avg_duration,
                'threshold': self.alert_thresholds['max_duration_seconds']
            })

        # 3. Check transformation success rate
        if avg_transformation_rate < self.alert_thresholds['min_success_rate']:
            alert_level = max(alert_level, 'YELLOW')
            alerts['alerts_triggered'].append({
                'type': 'LOW_TRANSFORMATION_RATE',
                'severity': 'WARNING',
                'message': f'Average transformation rate is {avg_transformation_rate:.1f}% (threshold: {self.alert_thresholds["min_success_rate"]}%)',
                'value': avg_transformation_rate,
                'threshold': self.alert_thresholds['min_success_rate']
            })

        # 4. Check for recent failures
        recent_failures = [m for m in recent_metrics[-5:] if m.get('status') == 'FAILED']
        if len(recent_failures) >= 2:
            alert_level = 'RED'
            alerts['alerts_triggered'].append({
                'type': 'REPEATED_FAILURES',
                'severity': 'CRITICAL',
                'message': f'Multiple recent failures detected ({len(recent_failures)} in last 5 executions)',
                'value': len(recent_failures)
            })

        alerts['alert_status'] = alert_level

        # Generate recommendations
        if alerts['alerts_triggered']:
            alerts['recommendations'] = self._generate_recommendations(alerts['alerts_triggered'])

        return alerts

    def _generate_recommendations(self, triggered_alerts: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on triggered alerts."""
        recommendations = []

        for alert in triggered_alerts:
            alert_type = alert['type']

            if alert_type == 'LOW_SUCCESS_RATE':
                recommendations.append("🔧 Review failed pipeline executions and check data source quality")
                recommendations.append("📊 Consider adjusting transformation expectations for problematic fields")

            elif alert_type == 'SLOW_PERFORMANCE':
                recommendations.append("⚡ Consider optimizing data processing for large datasets")
                recommendations.append("🧪 Test with smaller data samples to identify bottlenecks")

            elif alert_type == 'LOW_TRANSFORMATION_RATE':
                recommendations.append("🎯 Review desired schema definitions for accuracy")
                recommendations.append("📋 Check if new data patterns require schema updates")

            elif alert_type == 'REPEATED_FAILURES':
                recommendations.append("🚨 URGENT: Investigate root cause of pipeline failures")
                recommendations.append("🛡️ Consider implementing fallback data processing")

            elif alert_type == 'NO_DATA':
                recommendations.append("📈 Verify pipeline scheduling and execution")
                recommendations.append("🔍 Check for system-level issues preventing execution")

        # Remove duplicates while preserving order
        return list(dict.fromkeys(recommendations))

    def generate_health_report(self, hours: int = 24) -> str:
        """
        Generate a comprehensive health report for the GX pipeline.

        Args:
            hours: Number of hours to include in the report

        Returns:
            Formatted health report string
        """
        alerts = self.check_alerts(hours)
        recent_metrics = self.load_recent_metrics(hours)

        # Status emoji mapping
        status_emoji = {
            'GREEN': '✅',
            'YELLOW': '⚠️',
            'RED': '🚨'
        }

        report = f"""
🔍 GX PIPELINE HEALTH REPORT
{'=' * 50}
📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Time Period: Last {hours} hours
{status_emoji.get(alerts['alert_status'], '❓')} Overall Status: {alerts['alert_status']}

📈 PERFORMANCE METRICS:
   Total Executions: {alerts['metrics_summary'].get('total_executions', 0)}
   Success Rate: {alerts['metrics_summary'].get('execution_success_rate', 0):.1f}%
   Avg Duration: {alerts['metrics_summary'].get('average_duration', 0):.2f}s
   Avg Transformation Rate: {alerts['metrics_summary'].get('average_transformation_rate', 0):.1f}%
"""

        # Add alerts section
        if alerts['alerts_triggered']:
            report += f"\n🚨 ACTIVE ALERTS ({len(alerts['alerts_triggered'])}):\n"
            for i, alert in enumerate(alerts['alerts_triggered'], 1):
                severity_emoji = '🚨' if alert['severity'] == 'CRITICAL' else '⚠️'
                report += f"   {i}. {severity_emoji} {alert['type']}: {alert['message']}\n"
        else:
            report += "\n✅ NO ACTIVE ALERTS\n"

        # Add recommendations
        if alerts['recommendations']:
            report += f"\n💡 RECOMMENDATIONS:\n"
            for rec in alerts['recommendations']:
                report += f"   • {rec}\n"

        # Add recent execution summary
        if recent_metrics:
            report += f"\n📋 RECENT EXECUTIONS:\n"
            for metric in recent_metrics[-3:]:  # Last 3 executions
                status_icon = '✅' if metric.get('status') == 'SUCCESS' else '❌'
                timestamp = datetime.fromisoformat(metric['timestamp']).strftime('%H:%M:%S')
                dataset = metric.get('dataset_name', 'unknown')
                duration = metric.get('duration_seconds', 0)
                report += f"   {status_icon} {timestamp} - {dataset} ({duration:.2f}s)\n"

        report += f"\n{'=' * 50}\n"

        return report

    def export_metrics_to_csv(self, hours: int = 168, output_file: str = "gx_metrics_export.csv") -> str:
        """
        Export metrics to CSV for external analysis.

        Args:
            hours: Number of hours of data to export (default: 1 week)
            output_file: Output CSV filename

        Returns:
            Path to the exported CSV file
        """
        recent_metrics = self.load_recent_metrics(hours)

        if not recent_metrics:
            logger.warning("No metrics data available for export")
            return None

        # Flatten metrics for CSV export
        flattened_data = []
        for metric in recent_metrics:
            row = {
                'timestamp': metric.get('timestamp'),
                'dataset_name': metric.get('dataset_name'),
                'execution_id': metric.get('execution_id'),
                'status': metric.get('status'),
                'duration_seconds': metric.get('duration_seconds'),
                'input_rows': metric.get('input_rows'),
                'output_rows': metric.get('output_rows'),
                'input_columns': metric.get('input_columns'),
                'output_columns': metric.get('output_columns'),
                'transformations_attempted': metric.get('transformations_attempted'),
                'transformations_successful': metric.get('transformations_successful'),
                'transformation_success_rate': metric.get('transformation_success_rate'),
                'error_count': len(metric.get('errors', [])),
                'warning_count': len(metric.get('warnings', []))
            }
            flattened_data.append(row)

        # Create DataFrame and export
        df = pd.DataFrame(flattened_data)

        output_path = self.monitoring_dir / output_file
        df.to_csv(output_path, index=False)

        logger.info(f"📊 Metrics exported to {output_path}")
        return str(output_path)


def create_dashboard(monitoring_directory: str = "data/monitoring") -> GXDashboard:
    """
    Create and configure a GX dashboard instance.

    Args:
        monitoring_directory: Directory containing monitoring data

    Returns:
        Configured GXDashboard instance
    """
    return GXDashboard(monitoring_directory)


def check_pipeline_health(hours: int = 24) -> Dict[str, Any]:
    """
    Quick health check function for pipeline monitoring.

    Args:
        hours: Number of hours to look back

    Returns:
        Alert status dictionary
    """
    dashboard = create_dashboard()
    return dashboard.check_alerts(hours)


def print_health_report(hours: int = 24):
    """
    Print a formatted health report to console.

    Args:
        hours: Number of hours to include in report
    """
    dashboard = create_dashboard()
    report = dashboard.generate_health_report(hours)
    print(report)


if __name__ == "__main__":
    # Example usage
    print("🔍 GX Pipeline Health Check")
    print_health_report(24)

    # Export metrics
    dashboard = create_dashboard()
    csv_path = dashboard.export_metrics_to_csv(168)  # 1 week of data
    if csv_path:
        print(f"📊 Metrics exported to: {csv_path}")
