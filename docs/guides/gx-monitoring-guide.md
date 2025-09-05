# GX Pipeline Monitoring & Alerting Guide

Complete guide to understanding and using the Great Expectations pipeline monitoring system for production data quality assurance.

## 📊 Overview

The GX monitoring system provides comprehensive tracking, alerting, and reporting for your data cleaning pipeline. It automatically captures metrics, detects issues, and provides actionable insights for maintaining data quality.

## 🗂️ Monitoring Data Storage Architecture

### Storage Types & Persistence

The monitoring system uses a **three-tier storage strategy** to balance detail, performance, and accessibility:

#### 1. 📁 **Individual Execution Metrics (JSON)**
```
data/monitoring/metrics_{dataset}_{timestamp}.json
```

**Purpose**: Detailed metrics for each pipeline execution
**Persistence**: ✅ **PERMANENT** - Stored indefinitely
**Content**: Complete execution details including:
- Execution timing and duration
- Data volume metrics (rows/columns)
- Transformation success rates
- Data quality scores (4 dimensions)
- Error and warning details
- Validation results

**Example**:
```json
{
  "timestamp": "2025-09-05T09:09:01.535413",
  "dataset_name": "business_licenses",
  "execution_id": "business_licenses_20250905_090901_535390",
  "duration_seconds": 0.03277,
  "input_rows": 5,
  "output_rows": 5,
  "transformations_attempted": 39,
  "transformations_successful": 39,
  "transformation_success_rate": 100.0,
  "status": "SUCCESS"
}
```

#### 2. 📝 **Daily Log Files**
```
data/monitoring/gx_monitoring_{date}.log
```

**Purpose**: Human-readable operational logs
**Persistence**: ✅ **PERMANENT** - One file per day
**Content**: Timestamped entries for:
- Pipeline execution events
- Data quality calculations
- Error and warning messages
- Performance benchmarks

**Example**:
```
2025-09-05 09:09:01,567 - gx_monitoring - INFO - 🔧 Transformations - 39/39 successful (100.0%)
2025-09-05 09:09:01,568 - gx_monitoring - INFO - 📊 Data Quality Score: 67.4/100
```

#### 3. 📈 **CSV Exports (On-Demand)**
```
data/monitoring/{custom_name}.csv
```

**Purpose**: Data analysis and external reporting
**Persistence**: ⚠️ **MANUAL EXPORT** - Generated on-demand
**Content**: Flattened metrics for:
- Excel analysis
- BI tool integration
- Historical trend analysis
- Executive reporting

## 🔍 Monitoring Components

### Core Monitoring Classes

#### `GXPipelineMonitor`
**Location**: `step3_transform_model/gx_monitoring.py`

Primary monitoring engine that:
- Tracks pipeline execution metrics
- Calculates data quality scores
- Stores metrics to JSON and logs
- Provides historical metric retrieval

**Key Methods**:
```python
# Start monitoring a pipeline execution
execution_id = monitor.start_pipeline_monitoring("dataset_name")

# Log transformation results
monitor.log_transformation_results(execution_id, attempted=39, successful=39)

# Calculate data quality score
quality_score = monitor.calculate_data_quality_score(execution_id, dataframe)

# Finish monitoring and save results
final_metrics = monitor.finish_pipeline_monitoring(execution_id)
```

#### `GXDashboard`
**Location**: `step3_transform_model/gx_dashboard.py`

Dashboard and alerting system that:
- Generates health reports
- Checks alert thresholds
- Exports metrics to CSV
- Provides trend analysis

**Key Methods**:
```python
# Check for alert conditions
alerts = dashboard.check_alerts(hours=24)

# Generate comprehensive health report
report = dashboard.generate_health_report(hours=24)

# Export metrics for analysis
csv_path = dashboard.export_metrics_to_csv(hours=168, output_file="metrics.csv")
```

## 🚨 Alert System

### Alert Thresholds

The system monitors four key thresholds:

| Metric | Default Threshold | Severity | Description |
|--------|------------------|----------|-------------|
| **Success Rate** | 70% minimum | CRITICAL | Pipeline execution success rate |
| **Duration** | 60s maximum | WARNING | Pipeline execution time |
| **Quality Score** | 60/100 minimum | WARNING | Overall data quality |
| **Error Rate** | 10% maximum | WARNING | Transformation error rate |

### Alert Levels

- 🟢 **GREEN**: All systems normal
- 🟡 **YELLOW**: Warning conditions detected
- 🔴 **RED**: Critical issues requiring attention

### Customizing Alert Thresholds

```python
from step3_transform_model.gx_dashboard import create_dashboard

dashboard = create_dashboard()
dashboard.alert_thresholds = {
    'min_success_rate': 80.0,          # Stricter success rate
    'max_duration_seconds': 30.0,      # Faster response time
    'min_quality_score': 70.0,         # Higher quality standard
    'max_error_rate': 5.0,             # Lower error tolerance
}
```

## 📊 Data Quality Scoring

### Quality Dimensions

The system calculates a comprehensive quality score across four dimensions:

#### 1. **Completeness** (30% weight)
- Percentage of non-null values
- Measures data availability
- Formula: `(total_cells - null_cells) / total_cells * 100`

#### 2. **Validity** (30% weight)
- Percentage of values passing GX expectations
- Measures data correctness
- Based on transformation success rates

#### 3. **Consistency** (30% weight)
- Percentage of successful type conversions
- Measures data standardization
- Reflects transformation pipeline effectiveness

#### 4. **Timeliness** (10% weight)
- Data freshness assessment
- Currently defaults to 100% (real-time processing)
- Can be enhanced with actual freshness checks

### Overall Quality Score
```
Overall Score = (Completeness × 0.3) + (Validity × 0.3) + (Consistency × 0.3) + (Timeliness × 0.1)
```

## 🔧 Integration Guide

### Automatic Monitoring

Monitoring is **automatically enabled** when using `SmartDataCleaner`:

```python
from step3_transform_model.gx_data_cleaning import SmartDataCleaner

# Monitoring enabled by default
cleaner = SmartDataCleaner(enable_monitoring=True)
cleaned_df = cleaner.execute_smart_cleaning(df, "dataset_name")
```

### Manual Monitoring Setup

For custom pipelines, use the context manager:

```python
from step3_transform_model.gx_monitoring import monitor_pipeline

with monitor_pipeline("dataset_name") as (monitor, execution_id):
    # Your pipeline code here
    result = some_data_processing()

    # Log custom metrics
    monitor.log_transformation_results(execution_id, attempted=10, successful=8)
    monitor.log_data_metrics(execution_id, input_df, output_df)
```

### Production Integration

For production environments:

```python
from step3_transform_model.gx_dashboard import check_pipeline_health, print_health_report

# Check system health
health = check_pipeline_health(hours=24)
if health['alert_status'] == 'RED':
    # Send alerts, trigger recovery procedures
    print("🚨 CRITICAL ALERTS DETECTED")

# Generate daily health reports
print_health_report(hours=24)
```

## 📈 Reporting & Analysis

### Health Reports

Generate comprehensive health reports:

```python
from step3_transform_model.gx_dashboard import create_dashboard

dashboard = create_dashboard()
report = dashboard.generate_health_report(hours=24)
print(report)
```

**Sample Output**:
```
🔍 GX PIPELINE HEALTH REPORT
==================================================
📅 Report Time: 2025-09-05 09:12:32
📊 Time Period: Last 24 hours
✅ Overall Status: GREEN

📈 PERFORMANCE METRICS:
   Total Executions: 15
   Success Rate: 96.7%
   Avg Duration: 2.34s
   Avg Transformation Rate: 87.3%

✅ NO ACTIVE ALERTS

📋 RECENT EXECUTIONS:
   ✅ 09:10:15 - business_licenses (1.23s)
   ✅ 09:08:42 - building_permits (3.45s)
   ✅ 09:05:18 - cta_boardings (0.89s)
```

### CSV Export for Analysis

Export metrics for external analysis:

```python
# Export last week of data
csv_path = dashboard.export_metrics_to_csv(
    hours=168,  # 1 week
    output_file="weekly_metrics.csv"
)

# Use in Excel, Tableau, or other BI tools
import pandas as pd
metrics_df = pd.read_csv(csv_path)
```

### Historical Trend Analysis

Query specific time periods:

```python
# Get metrics from last 48 hours
recent_metrics = dashboard.load_recent_metrics(hours=48)

# Filter by dataset
business_metrics = [m for m in recent_metrics
                   if m.get('dataset_name') == 'business_licenses']

# Calculate trends
success_rates = [m['transformation_success_rate'] for m in business_metrics]
avg_success = sum(success_rates) / len(success_rates)
```

## 🛠️ Maintenance & Operations

### File Management

Monitor storage usage and clean old files as needed:

```bash
# Check monitoring directory size
du -sh data/monitoring/

# Archive old files (example: older than 30 days)
find data/monitoring/ -name "*.json" -mtime +30 -exec mv {} archive/ \;
```

### Log Rotation

Daily log files automatically rotate. Consider implementing log archival:

```bash
# Compress old log files
gzip data/monitoring/gx_monitoring_*.log

# Archive logs older than 1 month
find data/monitoring/ -name "*.log.gz" -mtime +30 -exec mv {} archive/ \;
```

### Performance Considerations

- **JSON files**: ~1KB per execution (minimal impact)
- **Log files**: ~2KB per execution (human-readable)
- **CSV exports**: Variable size (on-demand only)

Typical usage: **~50KB per day** for moderate pipeline activity.

## 🔍 Troubleshooting

### Common Issues

#### No Monitoring Data
```python
# Check if monitoring is enabled
cleaner = SmartDataCleaner()
print(f"Monitoring enabled: {cleaner.enable_monitoring}")

# Verify monitoring directory exists
import os
print(f"Monitoring dir exists: {os.path.exists('data/monitoring')}")
```

#### Missing Metrics Files
- Ensure write permissions on `data/monitoring/`
- Check for disk space issues
- Verify no exceptions during pipeline execution

#### Alert Threshold Issues
```python
# Check current thresholds
dashboard = create_dashboard()
print("Current thresholds:", dashboard.alert_thresholds)

# Test with custom thresholds
dashboard.alert_thresholds['min_success_rate'] = 50.0  # More lenient
alerts = dashboard.check_alerts(24)
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('gx_monitoring').setLevel(logging.DEBUG)
```

## 📚 Related Documentation

- **[GX Integration Guide](gx-integration-guide.md)** - Main GX setup and configuration
- **[Great Expectations Guide](great-expectations.md)** - Core GX concepts
- **[Technical Reference](../technical/README.md)** - API documentation

## 🎯 Next Steps

1. **Set up monitoring** in your production pipeline
2. **Customize alert thresholds** for your requirements
3. **Schedule regular health reports** for stakeholders
4. **Integrate with external monitoring** systems (if needed)

For implementation examples, see: `step3_transform_model/monitoring_example.py`
