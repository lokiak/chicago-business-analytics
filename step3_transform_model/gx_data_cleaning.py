"""
Great Expectations Data Cleaning Framework

This module provides automated data cleaning using Great Expectations for the
Chicago SMB Market Radar project. It bridges the gap between raw Socrata data
and analysis-ready datasets using pattern-based field detection and validation.

Key Features:
- Pattern-based field type detection
- Automated data transformation
- Great Expectations validation suites
- Business rule enforcement
- Quality scoring and reporting
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys
import logging
import re
from datetime import datetime

# Add project paths
sys.path.append(str(Path(__file__).parent.parent / "step2_data_ingestion"))
sys.path.append(str(Path(__file__).parent.parent / "shared"))

from schema import SchemaManager
from desired_schema import (
    DesiredSchemaManager, FieldTypeDetector, DesiredDataType,
    ChicagoDesiredSchemas
)

# Great Expectations imports
try:
    import great_expectations as gx
    from great_expectations.core import ExpectationSuite
    GX_AVAILABLE = True
except ImportError:
    print("⚠️  Great Expectations not installed. Run: pip install great-expectations")
    GX_AVAILABLE = False

logger = logging.getLogger(__name__)

class SmartDataCleaner:
    """
    Smart data cleaner that uses pattern recognition and Great Expectations
    to automatically clean and validate Chicago SMB data.
    """

    def __init__(self, gx_context_path: Optional[str] = None):
        """Initialize the smart data cleaner."""
        self.gx_context_path = gx_context_path or str(Path(__file__).parent / "gx")
        self.context = None
        self.cleaning_history = []

        if GX_AVAILABLE:
            self._setup_gx_context()

    def _setup_gx_context(self):
        """Setup Great Expectations context."""
        try:
            # Try to get existing context
            self.context = gx.get_context(context_root_dir=self.gx_context_path)
            logger.info(f"✅ Loaded existing GX context from {self.gx_context_path}")

            # Set up pandas datasource for runtime data validation
            self._setup_pandas_datasource()

        except Exception as e:
            logger.warning(f"⚠️  Could not setup GX context: {e}")
            self.context = None

    def _setup_pandas_datasource(self):
        """Set up pandas datasource for runtime DataFrame validation."""
        try:
            # Check if datasource already exists
            datasource_name = "chicago_smb_pandas_datasource"

            try:
                # Try to get existing datasource using GX 1.x API
                self.context.data_sources.get(datasource_name)
                logger.info(f"✅ Using existing datasource: {datasource_name}")
            except:
                try:
                    # Create new pandas datasource using GX 1.x API
                    self.context.data_sources.add_pandas(name=datasource_name)
                    logger.info(f"✅ Created pandas datasource: {datasource_name}")
                except Exception as create_error:
                    # Fallback to older API if new one doesn't work
                    logger.warning(f"New API failed: {create_error}, trying fallback")
                    # For now, we'll log and continue without datasource setup
                    logger.info("⚠️  Datasource setup skipped - will create at validation time")

        except Exception as e:
            logger.warning(f"⚠️  Could not setup pandas datasource: {e}")

    def _create_batch_request(self, df: pd.DataFrame, dataset_name: str):
        """Create a batch request for DataFrame validation."""
        try:
            # Try to get or create datasource
            datasource_name = "chicago_smb_pandas_datasource"
            try:
                datasource = self.context.data_sources.get(datasource_name)
            except:
                datasource = self.context.data_sources.add_pandas(name=datasource_name)

            # Get or create data asset
            try:
                asset = datasource.get_asset(dataset_name)
            except:
                asset = datasource.add_dataframe_asset(name=dataset_name)

            return asset.build_batch_request(dataframe=df)

        except Exception as e:
            # Fallback approach - use a simple dictionary-based batch request
            return {
                "datasource_name": "chicago_smb_pandas_datasource",
                "data_asset_name": dataset_name,
                "batch_data": df
            }

    def detect_and_plan_transformations(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """
        Analyze a dataset and create a smart transformation plan.

        Args:
            df: The pandas DataFrame to analyze
            dataset_name: Name of the dataset (for schema lookup)

        Returns:
            Dictionary containing transformation plan and analysis
        """
        print(f"\n🔍 ANALYZING {dataset_name.upper().replace('_', ' ')}")
        print("=" * 60)

        # Get current and desired schemas
        try:
            desired_schema = DesiredSchemaManager.get_desired_schema(dataset_name)
        except ValueError:
            logger.error(f"No desired schema found for {dataset_name}")
            return {}

        # Analyze current state
        current_dtypes = {col: str(df[col].dtype) for col in df.columns}

        # Create transformation plan
        transformation_plan = DesiredSchemaManager.generate_transformation_plan(
            dataset_name, current_dtypes
        )

        # Analyze data quality by field
        field_analysis = {}
        for field in desired_schema.fields:
            if field.name in df.columns:
                field_analysis[field.name] = self._analyze_field_quality(
                    df[field.name], field
                )

        # Detect patterns and suggest improvements
        pattern_suggestions = self._detect_field_patterns(df, dataset_name)

        plan = {
            'dataset_name': dataset_name,
            'total_records': len(df),
            'total_fields': len(df.columns),
            'transformation_plan': transformation_plan,
            'field_analysis': field_analysis,
            'pattern_suggestions': pattern_suggestions,
            'business_rules': desired_schema.business_rules,
            'quality_thresholds': desired_schema.quality_thresholds
        }

        self._print_transformation_summary(plan)
        return plan

    def _analyze_field_quality(self, series: pd.Series, field_def) -> Dict[str, Any]:
        """Analyze quality metrics for a single field."""
        return {
            'completeness': (series.notna().sum() / len(series)),
            'unique_values': series.nunique(),
            'null_count': series.isnull().sum(),
            'current_type': str(series.dtype),
            'desired_type': field_def.desired_type.value,
            'analysis_priority': field_def.analysis_priority,
            'sample_values': series.dropna().head(3).tolist()
        }

    def _detect_field_patterns(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, str]:
        """Detect field patterns and suggest transformations."""
        suggestions = {}

        for col in df.columns:
            # Use pattern detector to suggest field type
            detected_type = FieldTypeDetector.detect_field_type(col, df[col].head(10))

            if detected_type != DesiredDataType.STRING:
                current_type = str(df[col].dtype)
                if detected_type.value != current_type:
                    suggestions[col] = f"Convert to {detected_type.value} (detected pattern match)"

        return suggestions

    def _print_transformation_summary(self, plan: Dict[str, Any]):
        """Print a human-readable transformation summary."""
        print(f"📊 TRANSFORMATION ANALYSIS SUMMARY")
        print(f"   Records: {plan['total_records']:,}")
        print(f"   Fields: {plan['total_fields']}")
        print(f"   Transformations needed: {len(plan['transformation_plan'])}")
        print(f"   Pattern suggestions: {len(plan['pattern_suggestions'])}")

        if plan['transformation_plan']:
            print(f"\n🔧 PRIORITY TRANSFORMATIONS:")
            for field, details in plan['transformation_plan'].items():
                priority = details.get('priority', 'medium')
                current = details.get('current_type', 'unknown')
                desired = details.get('desired_type', 'unknown')
                print(f"   {priority.upper()}: {field} ({current} → {desired})")

    def execute_smart_cleaning(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """
        Execute smart data cleaning based on patterns and desired schema.

        Args:
            df: DataFrame to clean
            dataset_name: Name of dataset for schema lookup

        Returns:
            Cleaned DataFrame
        """
        print(f"\n🧹 EXECUTING SMART CLEANING: {dataset_name.upper()}")
        print("=" * 50)

        # Create transformation plan
        plan = self.detect_and_plan_transformations(df, dataset_name)

        # Start with a copy
        cleaned_df = df.copy()
        transformation_log = []

        # Execute transformations in priority order
        transformations = plan.get('transformation_plan', {})

        # Group by priority
        priority_groups = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for field, details in transformations.items():
            priority = details.get('priority', 'medium')
            priority_groups[priority].append((field, details))

        # Execute in priority order
        for priority in ['critical', 'high', 'medium', 'low']:
            if priority_groups[priority]:
                print(f"\n🔧 Applying {priority.upper()} priority transformations...")

                for field, details in priority_groups[priority]:
                    result = self._apply_field_transformation(
                        cleaned_df, field, details, dataset_name
                    )

                    if result['success']:
                        cleaned_df = result['dataframe']
                        transformation_log.append({
                            'field': field,
                            'transformation': result['transformation'],
                            'priority': priority,
                            'success': True
                        })
                        print(f"   ✅ {field}: {result['transformation']}")
                    else:
                        transformation_log.append({
                            'field': field,
                            'error': result['error'],
                            'priority': priority,
                            'success': False
                        })
                        print(f"   ❌ {field}: {result['error']}")

        # Apply business rules validation
        cleaned_df = self._apply_business_rules(cleaned_df, dataset_name)

        # Store cleaning history
        self.cleaning_history.append({
            'dataset_name': dataset_name,
            'timestamp': datetime.now(),
            'original_shape': df.shape,
            'cleaned_shape': cleaned_df.shape,
            'transformations': transformation_log
        })

        print(f"\n✅ SMART CLEANING COMPLETE")
        print(f"   Original: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"   Cleaned:  {cleaned_df.shape[0]} rows, {cleaned_df.shape[1]} columns")
        print(f"   Successful transformations: {sum(1 for t in transformation_log if t['success'])}")

        return cleaned_df

    def _apply_field_transformation(self, df: pd.DataFrame, field: str,
                                   details: Dict, dataset_name: str) -> Dict[str, Any]:
        """Apply a specific field transformation."""
        try:
            current_type = details['current_type']
            desired_type = details['desired_type']

            # Currency transformations
            if desired_type == 'currency':
                # Remove currency symbols and convert to float
                if field in df.columns:
                    df[field] = (df[field].astype(str)
                                      .str.replace('$', '')
                                      .str.replace(',', '')
                                      .str.replace('(', '-')
                                      .str.replace(')', '')
                                      .str.strip())
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    return {
                        'success': True,
                        'dataframe': df,
                        'transformation': f'Converted to currency (float64)'
                    }

            # Integer transformations
            elif desired_type == 'Int64':
                df[field] = pd.to_numeric(df[field], errors='coerce').astype('Int64')
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Converted to nullable integer'
                }

            # Date transformations
            elif desired_type == 'datetime64[ns]':
                df[field] = pd.to_datetime(df[field], errors='coerce')
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Converted to datetime'
                }

            # Category transformations
            elif desired_type == 'category':
                # Clean and categorize
                df[field] = (df[field].astype(str)
                                   .str.strip()
                                   .str.upper()
                                   .astype('category'))
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Converted to category'
                }

            # ZIP code transformations
            elif desired_type == 'zipcode':
                # Standardize ZIP codes
                df[field] = (df[field].astype(str)
                                   .str.extract(r'(\d{5})')[0]
                                   .fillna('00000'))
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Standardized ZIP code format'
                }

            else:
                return {
                    'success': False,
                    'error': f'Unknown desired type: {desired_type}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Transformation failed: {str(e)}'
            }

    def _apply_business_rules(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Apply business validation rules."""
        print(f"\n📋 Applying business rules...")

        try:
            desired_schema = DesiredSchemaManager.get_desired_schema(dataset_name)
            business_rules = desired_schema.business_rules or []

            for rule in business_rules:
                # Simple rule implementations
                if 'community_area between 1 and 77' in rule:
                    if 'community_area' in df.columns:
                        df.loc[~df['community_area'].between(1, 77, inclusive='both'), 'community_area'] = None
                        print(f"   ✅ Applied: {rule}")

                elif 'latitude between' in rule and 'longitude between' in rule:
                    # Chicago coordinate bounds
                    if 'latitude' in df.columns:
                        df.loc[~df['latitude'].between(41.6, 42.1, inclusive='both'), 'latitude'] = None
                    if 'longitude' in df.columns:
                        df.loc[~df['longitude'].between(-87.9, -87.5, inclusive='both'), 'longitude'] = None
                    print(f"   ✅ Applied coordinate bounds validation")

                elif 'total_fee >= 0' in rule:
                    fee_fields = [col for col in df.columns if 'fee' in col.lower()]
                    for fee_field in fee_fields:
                        df.loc[df[fee_field] < 0, fee_field] = 0
                    print(f"   ✅ Applied: Non-negative fees")

        except Exception as e:
            print(f"   ⚠️  Business rules application error: {e}")

        return df

    def create_gx_expectation_suite(self, df: pd.DataFrame, dataset_name: str) -> Optional[ExpectationSuite]:
        """Create a Great Expectations suite for the dataset."""
        if not GX_AVAILABLE or not self.context:
            print("⚠️  Great Expectations not available")
            return None

        print(f"\n📝 CREATING GX EXPECTATION SUITE: {dataset_name}")
        print("-" * 40)

        try:
            # Create expectation suite
            suite_name = f"{dataset_name}_expectations"

            # Delete existing suite if it exists
            try:
                self.context.delete_expectation_suite(suite_name)
            except:
                pass

            try:
                suite = self.context.add_or_update_expectation_suite(suite_name)
            except AttributeError:
                # Fallback for older GX versions
                try:
                    suite = self.context.create_expectation_suite(suite_name)
                except:
                    # If suite already exists, get it
                    suite = self.context.get_expectation_suite(suite_name)

            # Get desired schema for creating expectations
            desired_schema = DesiredSchemaManager.get_desired_schema(dataset_name)

            # Add basic expectations
            expectations_added = 0

            # Table-level expectations
            suite.expect_table_row_count_to_be_between(min_value=1)
            expectations_added += 1

            # Field-level expectations
            for field in desired_schema.fields:
                if field.name not in df.columns:
                    continue

                # Column exists expectation
                suite.expect_column_to_exist(field.name)
                expectations_added += 1

                # Required field expectations
                if field.required and not field.nullable:
                    suite.expect_column_values_to_not_be_null(field.name)
                    expectations_added += 1

                # Type-specific expectations
                if field.desired_type == DesiredDataType.INTEGER:
                    suite.expect_column_values_to_be_of_type(field.name, "int")
                    expectations_added += 1

                elif field.desired_type == DesiredDataType.DATE:
                    suite.expect_column_values_to_be_of_type(field.name, "datetime64")
                    expectations_added += 1

                elif field.desired_type == DesiredDataType.CURRENCY:
                    suite.expect_column_values_to_be_of_type(field.name, "float")
                    suite.expect_column_values_to_be_between(field.name, min_value=0)
                    expectations_added += 2

                # Validation rules from field definition
                if field.validation_rules:
                    for rule_name, rule_value in field.validation_rules.items():
                        if rule_name == "min_value" and rule_name == "max_value":
                            suite.expect_column_values_to_be_between(
                                field.name,
                                min_value=field.validation_rules.get("min_value"),
                                max_value=field.validation_rules.get("max_value")
                            )
                            expectations_added += 1

            # Save the suite
            self.context.save_expectation_suite(suite)

            print(f"   ✅ Created suite with {expectations_added} expectations")
            return suite

        except Exception as e:
            print(f"   ❌ Failed to create GX suite: {e}")
            return None

    def validate_with_gx(self, df: pd.DataFrame, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Validate DataFrame using Great Expectations."""
        if not GX_AVAILABLE or not self.context:
            return None

        print(f"\n✅ VALIDATING WITH GREAT EXPECTATIONS")
        print("-" * 40)

        try:
            # Create or get expectation suite
            suite = self.create_gx_expectation_suite(df, dataset_name)
            if not suite:
                return None

            # Create validator using GX 1.x simplified approach
            try:
                # Use the simplified validator creation approach
                validator = self.context.get_validator(
                    batch_request=self._create_batch_request(df, dataset_name),
                    expectation_suite_name=suite.expectation_suite_name
                )
            except Exception as validator_error:
                print(f"   ❌ Could not create validator: {validator_error}")
                return None

            # Run validation
            results = validator.validate()

            # Extract key metrics
            success_count = results.statistics["successful_expectations"]
            total_count = results.statistics["evaluated_expectations"]
            success_rate = success_count / total_count if total_count > 0 else 0

            print(f"   Expectations met: {success_count}/{total_count} ({success_rate:.1%})")

            # Log any failures
            if not results.success:
                print("   ⚠️  Failed expectations:")
                for result in results.results:
                    if not result.success:
                        expectation = result.expectation_config.expectation_type
                        column = result.expectation_config.kwargs.get('column', 'table')
                        print(f"      {column}: {expectation}")

            return {
                'success': results.success,
                'success_rate': success_rate,
                'total_expectations': total_count,
                'successful_expectations': success_count,
                'failed_expectations': total_count - success_count,
                'results': results
            }

        except Exception as e:
            print(f"   ❌ GX validation failed: {e}")
            return None

    def get_cleaning_report(self) -> Dict[str, Any]:
        """Get a comprehensive cleaning report."""
        return {
            'total_cleaning_sessions': len(self.cleaning_history),
            'cleaning_history': self.cleaning_history,
            'gx_available': GX_AVAILABLE,
            'context_path': self.gx_context_path
        }

# Convenience functions for easy integration
def smart_clean_dataset(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Convenience function to smart clean a single dataset."""
    cleaner = SmartDataCleaner()
    return cleaner.execute_smart_cleaning(df, dataset_name)

def batch_clean_datasets(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Clean multiple datasets using smart cleaning."""
    cleaner = SmartDataCleaner()
    cleaned_datasets = {}

    print("🚀 BATCH SMART CLEANING")
    print("=" * 50)

    for dataset_name, df in datasets.items():
        cleaned_datasets[dataset_name] = cleaner.execute_smart_cleaning(df, dataset_name)

    # Print overall summary
    report = cleaner.get_cleaning_report()
    print(f"\n📊 BATCH CLEANING SUMMARY")
    print(f"   Datasets processed: {len(datasets)}")
    print(f"   Cleaning sessions: {report['total_cleaning_sessions']}")
    print(f"   Great Expectations: {'Available' if report['gx_available'] else 'Not Available'}")

    return cleaned_datasets

if __name__ == "__main__":
    # Example usage
    print("Great Expectations Data Cleaning Framework")
    print("Run this module within your data pipeline to use smart cleaning capabilities.")
