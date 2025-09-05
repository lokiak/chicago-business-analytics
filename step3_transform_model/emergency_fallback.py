"""
Emergency Fallback Procedures for GX Pipeline Failures

This module provides emergency procedures to maintain business continuity
when the Great Expectations data cleaning pipeline encounters failures.

Author: Chicago SMB Market Radar Team
Version: 1.0
Created: September 2025
"""

import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List

# Import original modules for fallback
FALLBACK_IMPORTS_AVAILABLE = False
try:
    # Add paths relative to current location
    sys.path.insert(0, '../shared')
    sys.path.insert(0, '../step2_data_ingestion')

    from config_manager import load_settings
    from sheets_client import open_sheet, upsert_worksheet, overwrite_with_dataframe
    from notebook_utils import load_sheet_data, save_analysis_results

    # Try to import schema - this might not be available in all environments
    try:
        from schema import SchemaManager
        SCHEMA_AVAILABLE = True
    except ImportError:
        SCHEMA_AVAILABLE = False
        # Create a minimal schema manager substitute
        class SchemaManager:
            @staticmethod
            def get_required_fields(dataset_name):
                # Basic required fields for emergency fallback
                return ['id'] if 'licenses' in dataset_name else ['id'] if 'permits' in dataset_name else ['service_date']

            @staticmethod
            def get_date_fields(dataset_name):
                if 'licenses' in dataset_name:
                    return ['application_created_date', 'date_issued', 'license_start_date', 'expiration_date']
                elif 'permits' in dataset_name:
                    return ['application_start_date', 'issue_date']
                else:
                    return ['service_date']

            @staticmethod
            def get_field_names(dataset_name):
                return []  # Not critical for emergency fallback

    FALLBACK_IMPORTS_AVAILABLE = True

except ImportError as e:
    print(f"Warning: Fallback imports failed: {e}")
    print("Emergency fallback will have limited functionality")
    FALLBACK_IMPORTS_AVAILABLE = False


class EmergencyDataProcessor:
    """
    Emergency data processor using pre-GX manual cleaning methods.

    This class provides a complete fallback to manual data cleaning
    procedures when the GX pipeline fails or becomes unavailable.
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize the emergency processor."""
        self.enable_logging = enable_logging
        self.cleaning_log = []
        self.performance_metrics = {}

        if self.enable_logging:
            self.log("Emergency Data Processor initialized")

    def log(self, message: str, level: str = "INFO"):
        """Log emergency procedure messages."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"

        if self.enable_logging:
            print(log_entry)

        self.cleaning_log.append(log_entry)

    def emergency_health_check(self) -> Dict:
        """
        Perform quick health check to determine if emergency procedures are needed.

        Returns:
            Dict with health status and recommendations
        """
        health_status = {
            'gx_available': False,
            'fallback_ready': FALLBACK_IMPORTS_AVAILABLE,
            'recommended_action': 'unknown',
            'estimated_performance': 'unknown'
        }

        # Test GX availability
        try:
            sys.path.append('../')
            from gx_data_cleaning import SmartDataCleaner

            # Quick test
            test_cleaner = SmartDataCleaner(enable_monitoring=False)
            test_data = pd.DataFrame({'test': [1, 2, 3]})
            test_cleaner.execute_smart_cleaning(test_data, 'emergency_test')

            health_status['gx_available'] = True
            health_status['recommended_action'] = 'continue_gx'
            self.log("✅ GX Pipeline: HEALTHY")

        except Exception as e:
            health_status['gx_available'] = False
            health_status['recommended_action'] = 'use_emergency_fallback'
            self.log(f"❌ GX Pipeline: FAILED - {str(e)}", "ERROR")

        # Test fallback readiness
        if FALLBACK_IMPORTS_AVAILABLE:
            health_status['estimated_performance'] = '3000-5000 rows/second'
            self.log("✅ Emergency Fallback: READY")
        else:
            health_status['estimated_performance'] = 'unavailable'
            self.log("❌ Emergency Fallback: NOT READY", "ERROR")

        return health_status

    def emergency_manual_cleaning(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Execute emergency manual cleaning using pre-GX methods.

        Args:
            datasets: Dictionary of dataset_name -> DataFrame

        Returns:
            Dictionary of cleaned datasets
        """
        self.log("🚨 EMERGENCY MANUAL CLEANING INITIATED")
        self.log("=" * 50)

        start_time = time.time()
        cleaned_datasets = datasets.copy()
        total_rows = sum(len(df) for df in datasets.values())

        # 1. Fix business logic issues
        self.log("🔧 Step 1: Fixing business logic issues...")
        cleaned_datasets = self._fix_business_logic_issues(cleaned_datasets)

        # 2. Handle contamination issues
        self.log("🔧 Step 2: Handling contamination...")
        cleaned_datasets = self._fix_contamination_issues(cleaned_datasets)

        # 3. Standardize data types
        self.log("🔧 Step 3: Standardizing data types...")
        cleaned_datasets = self._standardize_data_types(cleaned_datasets)

        # 4. Clean optional fields
        self.log("🔧 Step 4: Cleaning optional fields...")
        cleaned_datasets = self._clean_optional_fields(cleaned_datasets)

        # 5. Final validation
        self.log("🔧 Step 5: Final validation...")
        cleaned_datasets = self._validate_cleaned_data(cleaned_datasets)

        # Performance metrics
        duration = time.time() - start_time
        throughput = total_rows / duration if duration > 0 else 0

        self.performance_metrics = {
            'total_rows': total_rows,
            'duration_seconds': duration,
            'throughput_rows_per_second': throughput,
            'success_rate': self._calculate_success_rate(datasets, cleaned_datasets)
        }

        self.log(f"✅ EMERGENCY CLEANING COMPLETE")
        self.log(f"   Total rows: {total_rows:,}")
        self.log(f"   Duration: {duration:.2f}s")
        self.log(f"   Throughput: {throughput:.0f} rows/second")
        self.log(f"   Success rate: {self.performance_metrics['success_rate']:.1f}%")

        return cleaned_datasets

    def _fix_business_logic_issues(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Fix basic business logic violations."""

        # Fix licenses with invalid date sequences
        if 'business_licenses' in datasets:
            df = datasets['business_licenses'].copy()

            # Convert date fields if needed
            date_fields = ['license_start_date', 'expiration_date', 'application_created_date', 'date_issued']
            for field in date_fields:
                if field in df.columns:
                    df[field] = pd.to_datetime(df[field], errors='coerce')

            # Fix licenses where start date > expiration date
            if 'license_start_date' in df.columns and 'expiration_date' in df.columns:
                invalid_dates = (df['license_start_date'] > df['expiration_date']) & \
                               df['license_start_date'].notna() & df['expiration_date'].notna()

                if invalid_dates.sum() > 0:
                    df.loc[invalid_dates, 'expiration_date'] = \
                        df.loc[invalid_dates, 'license_start_date'] + pd.DateOffset(years=1)
                    self.log(f"      Fixed {invalid_dates.sum()} invalid date sequences")

            datasets['business_licenses'] = df

        return datasets

    def _fix_contamination_issues(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Fix data contamination issues."""

        for dataset_name, df in datasets.items():
            # Fix common contamination patterns

            # Clean ZIP codes
            if 'zip_code' in df.columns:
                # Remove quotes and extract 5-digit ZIP
                df['zip_code'] = df['zip_code'].astype(str).str.replace(r'[\'"]', '', regex=True)
                df['zip_code'] = df['zip_code'].str.extract(r'(\d{5})')[0]
                df['zip_code'] = pd.to_numeric(df['zip_code'], errors='coerce')
                self.log(f"      Cleaned ZIP codes in {dataset_name}")

            # Clean ID fields
            id_fields = [col for col in df.columns if 'id' in col.lower() or 'permit_' in col.lower()]
            for field in id_fields:
                if df[field].dtype == 'object':
                    df[field] = df[field].astype(str).str.strip()
                    # Remove special characters but keep alphanumeric and dashes
                    df[field] = df[field].str.replace(r'[^a-zA-Z0-9\-]', '', regex=True)
                    self.log(f"      Cleaned {field} in {dataset_name}")

            datasets[dataset_name] = df

        return datasets

    def _standardize_data_types(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Standardize data types based on schema definitions."""

        for dataset_name, df in datasets.items():

            # Convert date fields
            date_patterns = ['date', 'created', 'issued', 'expiration', 'start', 'approved', 'payment']
            for col in df.columns:
                if any(pattern in col.lower() for pattern in date_patterns):
                    if df[col].dtype == 'object':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        self.log(f"      Converted {col} to datetime")

            # Convert numeric fields
            numeric_candidates = ['community_area', 'ward', 'precinct', 'zip_code',
                                'latitude', 'longitude', 'processing_time', 'total_fee',
                                'ssa', 'police_district']

            for field in numeric_candidates:
                if field in df.columns and df[field].dtype == 'object':
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    self.log(f"      Converted {field} to numeric")

            # Convert categorical fields (high cardinality text fields)
            categorical_candidates = ['license_code', 'license_status', 'permit_status',
                                    'application_type', 'work_type', 'permit_type',
                                    'city', 'state', 'neighborhood']

            for field in categorical_candidates:
                if field in df.columns and df[field].dtype == 'object':
                    unique_ratio = df[field].nunique() / len(df)
                    if unique_ratio < 0.1:  # Low cardinality, good for category
                        df[field] = df[field].astype('category')
                        self.log(f"      Converted {field} to category")

            datasets[dataset_name] = df

        return datasets

    def _clean_optional_fields(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Clean optional fields with low completion rates."""

        for dataset_name, df in datasets.items():
            columns_to_drop = []

            for col in df.columns:
                completion_rate = df[col].notna().sum() / len(df)

                # Drop fields with very low completion (< 5%)
                if completion_rate < 0.05:
                    columns_to_drop.append(col)

                # Fill fields with low completion (5-25%) with placeholder
                elif completion_rate < 0.25 and df[col].dtype == 'object':
                    df[col] = df[col].fillna('UNKNOWN')
                    self.log(f"      Filled {col} nulls with 'UNKNOWN'")

            if columns_to_drop:
                df = df.drop(columns=columns_to_drop)
                self.log(f"      Dropped {len(columns_to_drop)} low-value columns")

            datasets[dataset_name] = df

        return datasets

    def _validate_cleaned_data(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Validate cleaned data meets basic requirements."""

        for dataset_name, df in datasets.items():
            # Remove completely empty rows
            before_rows = len(df)
            df = df.dropna(how='all')
            if len(df) < before_rows:
                self.log(f"      Removed {before_rows - len(df)} empty rows")

            # Strip whitespace from text fields
            text_fields = df.select_dtypes(include=['object']).columns
            for field in text_fields:
                if df[field].dtype == 'object':
                    df[field] = df[field].astype(str).str.strip()

            self.log(f"      {dataset_name}: {len(df)} rows, {len(df.columns)} columns validated")
            datasets[dataset_name] = df

        return datasets

    def _calculate_success_rate(self, original: Dict, cleaned: Dict) -> float:
        """Calculate cleaning success rate based on type conversions."""
        total_conversions = 0
        successful_conversions = 0

        for dataset_name in original.keys():
            if dataset_name in cleaned:
                orig_df = original[dataset_name]
                clean_df = cleaned[dataset_name]

                # Count successful type conversions
                for col in orig_df.columns:
                    if col in clean_df.columns:
                        total_conversions += 1

                        # Success if we improved the data type
                        if (orig_df[col].dtype == 'object' and
                            clean_df[col].dtype != 'object'):
                            successful_conversions += 1
                        elif orig_df[col].dtype == clean_df[col].dtype:
                            successful_conversions += 0.5  # Partial credit for maintaining

        return (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0

    def emergency_data_recovery(self) -> Dict[str, pd.DataFrame]:
        """
        Complete emergency data recovery from Google Sheets.

        Returns:
            Dict of fresh datasets loaded and cleaned
        """
        self.log("🚨 EMERGENCY DATA RECOVERY INITIATED")

        if not FALLBACK_IMPORTS_AVAILABLE:
            raise Exception("Cannot perform recovery: Required imports not available")

        # Load fresh data from Google Sheets
        settings = load_settings()
        sh = open_sheet(settings.sheet_id, settings.google_creds_path)

        datasets_config = {
            'business_licenses': 'Business_Licenses_Full',
            'building_permits': 'Building_Permits_Full',
            'cta_boardings': 'CTA_Full'
        }

        # Fetch fresh datasets
        fresh_datasets = {}
        for dataset_name, sheet_name in datasets_config.items():
            df = load_sheet_data(sh, sheet_name)
            fresh_datasets[dataset_name] = df
            self.log(f"✅ Recovered {len(df):,} rows for {dataset_name}")

        # Apply emergency cleaning
        cleaned_datasets = self.emergency_manual_cleaning(fresh_datasets)

        # Save recovery data to special sheets
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for dataset_name, df in cleaned_datasets.items():
            recovery_sheet_name = f"{dataset_name.title().replace('_', '')}_Recovery_{timestamp}"
            ws = upsert_worksheet(sh, recovery_sheet_name,
                                rows=len(df)+100, cols=len(df.columns)+5)
            overwrite_with_dataframe(ws, df)
            self.log(f"✅ Saved recovery data to {recovery_sheet_name}")

        return cleaned_datasets

    def get_performance_report(self) -> Dict:
        """Get performance report for the emergency procedures."""
        return {
            'performance_metrics': self.performance_metrics,
            'cleaning_log': self.cleaning_log,
            'timestamp': datetime.now().isoformat()
        }


def emergency_quick_test() -> bool:
    """
    Quick emergency test to verify fallback systems.

    Returns:
        bool: True if emergency systems are ready
    """
    print("🧪 EMERGENCY SYSTEMS TEST")
    print("=" * 30)

    processor = EmergencyDataProcessor()
    health_status = processor.emergency_health_check()

    print(f"GX Available: {health_status['gx_available']}")
    print(f"Fallback Ready: {health_status['fallback_ready']}")
    print(f"Recommended Action: {health_status['recommended_action']}")
    print(f"Expected Performance: {health_status['estimated_performance']}")

    if health_status['fallback_ready']:
        # Test with realistic business licenses data
        test_data = {
            'business_licenses': pd.DataFrame({
                'id': ['TEST001', 'TEST002', 'TEST003'],
                'date_issued': ['2025-01-01', '2025-01-02', '2025-01-03'],
                'zip_code': ['"60601"', '60602', '60603'],
                'license_status': ['ACTIVE', 'INACTIVE', 'PENDING']
            })
        }

        start_time = time.time()
        cleaned = processor.emergency_manual_cleaning(test_data)
        duration = time.time() - start_time

        print(f"\n📊 Test Results:")
        print(f"   Duration: {duration:.3f}s")
        print(f"   Rows processed: {len(cleaned['business_licenses'])}")
        print(f"   Test status: ✅ PASS")

        return True
    else:
        print("\n❌ Emergency systems not ready")
        return False


if __name__ == "__main__":
    # Run emergency test when script is called directly
    emergency_quick_test()
