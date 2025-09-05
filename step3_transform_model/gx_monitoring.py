"""
GX Pipeline Monitoring and Error Handling Module

Provides comprehensive monitoring, logging, and error handling for the
Great Expectations data cleaning pipeline.
"""

import logging
import time
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
from dataclasses import dataclass, asdict

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class PipelineMetrics:
    """Data class for tracking pipeline execution metrics."""

    # Execution info
    timestamp: str
    dataset_name: str
    execution_id: str

    # Performance metrics
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: Optional[float] = None

    # Data metrics
    input_rows: int = 0
    output_rows: int = 0
    input_columns: int = 0
    output_columns: int = 0

    # Quality metrics
    transformations_attempted: int = 0
    transformations_successful: int = 0
    transformation_success_rate: float = 0.0

    # Validation metrics
    expectations_evaluated: int = 0
    expectations_passed: int = 0
    expectations_failed: int = 0
    validation_success_rate: float = 0.0

    # Error tracking
    errors: List[str] = None
    warnings: List[str] = None
    status: str = "RUNNING"  # RUNNING, SUCCESS, FAILED, WARNING

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

@dataclass
class DataQualityScore:
    """Data class for tracking data quality scores."""

    dataset_name: str
    timestamp: str

    # Quality dimensions
    completeness_score: float = 0.0  # % of non-null values
    validity_score: float = 0.0      # % of valid values (passed expectations)
    consistency_score: float = 0.0   # % of consistent data types
    timeliness_score: float = 0.0    # Based on data freshness

    # Overall score
    overall_quality_score: float = 0.0

    # Supporting metrics
    total_records: int = 0
    null_records: int = 0
    invalid_records: int = 0
    type_conversion_errors: int = 0


class GXPipelineMonitor:
    """
    Comprehensive monitoring system for GX data cleaning pipeline.

    Features:
    - Real-time performance tracking
    - Data quality scoring
    - Error logging and alerting
    - Historical metrics storage
    - Dashboard-ready metrics export
    """

    def __init__(self, log_directory: str = "data/monitoring"):
        """
        Initialize the monitoring system.

        Args:
            log_directory: Directory to store monitoring logs and metrics
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Setup monitoring logs
        self.setup_logging()

        # Current session metrics
        self.current_metrics: Dict[str, PipelineMetrics] = {}
        self.quality_scores: List[DataQualityScore] = []

        logger.info("🔍 GX Pipeline Monitor initialized")

    def setup_logging(self):
        """Setup dedicated logging for monitoring."""

        # Create monitoring log file
        log_file = self.log_directory / f"gx_monitoring_{datetime.now().strftime('%Y%m%d')}.log"

        # Configure logging
        monitoring_handler = logging.FileHandler(log_file)
        monitoring_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        monitoring_handler.setFormatter(formatter)

        # Add handler to logger
        monitor_logger = logging.getLogger('gx_monitoring')
        monitor_logger.addHandler(monitoring_handler)
        monitor_logger.setLevel(logging.INFO)

    def start_pipeline_monitoring(self, dataset_name: str) -> str:
        """
        Start monitoring a pipeline execution.

        Args:
            dataset_name: Name of the dataset being processed

        Returns:
            execution_id: Unique ID for this execution
        """
        execution_id = f"{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        metrics = PipelineMetrics(
            timestamp=datetime.now().isoformat(),
            dataset_name=dataset_name,
            execution_id=execution_id,
            start_time=time.time(),
            status="RUNNING"
        )

        self.current_metrics[execution_id] = metrics

        logger.info(f"📊 Started monitoring pipeline execution: {execution_id}")
        return execution_id

    def log_data_metrics(self, execution_id: str, input_df: pd.DataFrame, output_df: pd.DataFrame = None):
        """
        Log data size and structure metrics.

        Args:
            execution_id: Pipeline execution ID
            input_df: Input DataFrame
            output_df: Output DataFrame (optional)
        """
        if execution_id not in self.current_metrics:
            logger.warning(f"⚠️ Unknown execution ID: {execution_id}")
            return

        metrics = self.current_metrics[execution_id]

        # Input metrics
        metrics.input_rows = len(input_df)
        metrics.input_columns = len(input_df.columns)

        # Output metrics
        if output_df is not None:
            metrics.output_rows = len(output_df)
            metrics.output_columns = len(output_df.columns)

        logger.info(f"📊 Data metrics - Input: {metrics.input_rows}x{metrics.input_columns}, "
                   f"Output: {metrics.output_rows}x{metrics.output_columns}")

    def log_transformation_results(self, execution_id: str, attempted: int, successful: int):
        """
        Log transformation success metrics.

        Args:
            execution_id: Pipeline execution ID
            attempted: Number of transformations attempted
            successful: Number of transformations successful
        """
        if execution_id not in self.current_metrics:
            logger.warning(f"⚠️ Unknown execution ID: {execution_id}")
            return

        metrics = self.current_metrics[execution_id]
        metrics.transformations_attempted = attempted
        metrics.transformations_successful = successful

        if attempted > 0:
            metrics.transformation_success_rate = (successful / attempted) * 100

        logger.info(f"🔧 Transformations - {successful}/{attempted} successful "
                   f"({metrics.transformation_success_rate:.1f}%)")

    def log_validation_results(self, execution_id: str, evaluated: int, passed: int, failed: int):
        """
        Log GX validation results.

        Args:
            execution_id: Pipeline execution ID
            evaluated: Number of expectations evaluated
            passed: Number of expectations passed
            failed: Number of expectations failed
        """
        if execution_id not in self.current_metrics:
            logger.warning(f"⚠️ Unknown execution ID: {execution_id}")
            return

        metrics = self.current_metrics[execution_id]
        metrics.expectations_evaluated = evaluated
        metrics.expectations_passed = passed
        metrics.expectations_failed = failed

        if evaluated > 0:
            metrics.validation_success_rate = (passed / evaluated) * 100

        logger.info(f"✅ Validations - {passed}/{evaluated} passed "
                   f"({metrics.validation_success_rate:.1f}%)")

    def log_error(self, execution_id: str, error: str, error_type: str = "ERROR"):
        """
        Log an error or warning.

        Args:
            execution_id: Pipeline execution ID
            error: Error message
            error_type: Type of error (ERROR, WARNING)
        """
        if execution_id not in self.current_metrics:
            logger.warning(f"⚠️ Unknown execution ID: {execution_id}")
            return

        metrics = self.current_metrics[execution_id]

        if error_type == "ERROR":
            metrics.errors.append(error)
            metrics.status = "FAILED"
            logger.error(f"❌ Pipeline error: {error}")
        else:
            metrics.warnings.append(error)
            if metrics.status == "RUNNING":
                metrics.status = "WARNING"
            logger.warning(f"⚠️ Pipeline warning: {error}")

    def calculate_data_quality_score(self, execution_id: str, df: pd.DataFrame) -> DataQualityScore:
        """
        Calculate comprehensive data quality score.

        Args:
            execution_id: Pipeline execution ID
            df: DataFrame to analyze

        Returns:
            DataQualityScore object
        """
        if execution_id not in self.current_metrics:
            logger.warning(f"⚠️ Unknown execution ID: {execution_id}")
            return None

        metrics = self.current_metrics[execution_id]

        # Calculate quality dimensions
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()

        completeness_score = ((total_cells - null_cells) / total_cells) * 100 if total_cells > 0 else 0

        # Validity score based on GX validation results
        validity_score = metrics.validation_success_rate

        # Consistency score based on transformation success
        consistency_score = metrics.transformation_success_rate

        # Timeliness score (placeholder - could be enhanced with actual data freshness checks)
        timeliness_score = 100.0  # Assume current data is timely

        # Overall score (weighted average)
        overall_score = (
            completeness_score * 0.3 +
            validity_score * 0.3 +
            consistency_score * 0.3 +
            timeliness_score * 0.1
        )

        quality_score = DataQualityScore(
            dataset_name=metrics.dataset_name,
            timestamp=datetime.now().isoformat(),
            completeness_score=completeness_score,
            validity_score=validity_score,
            consistency_score=consistency_score,
            timeliness_score=timeliness_score,
            overall_quality_score=overall_score,
            total_records=len(df),
            null_records=int(null_cells),
            type_conversion_errors=len(metrics.errors)
        )

        self.quality_scores.append(quality_score)

        logger.info(f"📊 Data Quality Score: {overall_score:.1f}/100 "
                   f"(Completeness: {completeness_score:.1f}%, "
                   f"Validity: {validity_score:.1f}%, "
                   f"Consistency: {consistency_score:.1f}%)")

        return quality_score

    def finish_pipeline_monitoring(self, execution_id: str) -> PipelineMetrics:
        """
        Finish monitoring a pipeline execution.

        Args:
            execution_id: Pipeline execution ID

        Returns:
            Final metrics for the execution
        """
        if execution_id not in self.current_metrics:
            logger.warning(f"⚠️ Unknown execution ID: {execution_id}")
            return None

        metrics = self.current_metrics[execution_id]
        metrics.end_time = time.time()
        metrics.duration_seconds = metrics.end_time - metrics.start_time

        # Set final status
        if metrics.status == "RUNNING":
            if len(metrics.errors) == 0:
                metrics.status = "SUCCESS"
            else:
                metrics.status = "FAILED"

        # Save metrics to file
        self.save_metrics(metrics)

        logger.info(f"🏁 Pipeline execution completed: {execution_id} "
                   f"(Status: {metrics.status}, Duration: {metrics.duration_seconds:.2f}s)")

        return metrics

    def save_metrics(self, metrics: PipelineMetrics):
        """Save metrics to JSON file for historical tracking."""

        metrics_file = self.log_directory / f"metrics_{metrics.execution_id}.json"

        try:
            with open(metrics_file, 'w') as f:
                json.dump(asdict(metrics), f, indent=2, default=str)

            logger.info(f"💾 Metrics saved to {metrics_file}")

        except Exception as e:
            logger.error(f"❌ Failed to save metrics: {e}")

    def get_recent_metrics(self, hours: int = 24) -> List[PipelineMetrics]:
        """
        Get metrics from recent pipeline executions.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent PipelineMetrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = []

        # Read metrics files
        for metrics_file in self.log_directory.glob("metrics_*.json"):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)

                # Check if within time range
                timestamp = datetime.fromisoformat(data['timestamp'])
                if timestamp >= cutoff_time:
                    recent_metrics.append(data)

            except Exception as e:
                logger.warning(f"⚠️ Could not read metrics file {metrics_file}: {e}")

        return recent_metrics

    def generate_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive monitoring report.

        Returns:
            Dictionary containing monitoring summary
        """
        recent_metrics = self.get_recent_metrics(24)

        # Calculate aggregate statistics
        total_executions = len(recent_metrics)
        successful_executions = len([m for m in recent_metrics if m.get('status') == 'SUCCESS'])
        failed_executions = len([m for m in recent_metrics if m.get('status') == 'FAILED'])

        avg_duration = 0
        avg_success_rate = 0

        if recent_metrics:
            durations = [m.get('duration_seconds', 0) for m in recent_metrics if m.get('duration_seconds')]
            success_rates = [m.get('transformation_success_rate', 0) for m in recent_metrics]

            avg_duration = sum(durations) / len(durations) if durations else 0
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0

        report = {
            'report_timestamp': datetime.now().isoformat(),
            'time_period_hours': 24,
            'execution_summary': {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate_percent': (successful_executions / total_executions * 100) if total_executions > 0 else 0
            },
            'performance_metrics': {
                'average_duration_seconds': avg_duration,
                'average_transformation_success_rate': avg_success_rate
            },
            'quality_scores': [asdict(score) for score in self.quality_scores[-10:]]  # Last 10 scores
        }

        return report


# Context manager for easy monitoring
class monitor_pipeline:
    """
    Context manager for monitoring pipeline executions.

    Usage:
        with monitor_pipeline("business_licenses") as monitor:
            # Your pipeline code here
            result = some_pipeline_function()
            monitor.log_success_metrics(...)
    """

    def __init__(self, dataset_name: str, monitor: GXPipelineMonitor = None):
        self.dataset_name = dataset_name
        self.monitor = monitor or GXPipelineMonitor()
        self.execution_id = None

    def __enter__(self):
        self.execution_id = self.monitor.start_pipeline_monitoring(self.dataset_name)
        return self.monitor, self.execution_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception
            error_msg = f"{exc_type.__name__}: {exc_val}"
            self.monitor.log_error(self.execution_id, error_msg, "ERROR")

        self.monitor.finish_pipeline_monitoring(self.execution_id)
        return False  # Don't suppress exceptions


# Convenience function for quick monitoring setup
def create_pipeline_monitor(log_directory: str = "data/monitoring") -> GXPipelineMonitor:
    """
    Create and configure a pipeline monitor.

    Args:
        log_directory: Directory for monitoring logs

    Returns:
        Configured GXPipelineMonitor instance
    """
    return GXPipelineMonitor(log_directory)


if __name__ == "__main__":
    # Example usage
    monitor = create_pipeline_monitor()

    # Example monitoring session
    with monitor_pipeline("test_dataset", monitor) as (mon, exec_id):
        # Simulate pipeline work
        import time
        time.sleep(1)

        # Log some metrics
        test_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mon.log_data_metrics(exec_id, test_df, test_df)
        mon.log_transformation_results(exec_id, 2, 2)
        mon.log_validation_results(exec_id, 5, 4, 1)

        # Calculate quality score
        quality_score = mon.calculate_data_quality_score(exec_id, test_df)

    # Generate report
    report = monitor.generate_monitoring_report()
    print("📊 Monitoring Report Generated")
    print(f"Recent executions: {report['execution_summary']['total_executions']}")
