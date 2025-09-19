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

# Import monitoring system
try:
    from .gx_monitoring import GXPipelineMonitor, monitor_pipeline, PipelineMetrics
    MONITORING_AVAILABLE = True
except ImportError:
    try:
        from gx_monitoring import GXPipelineMonitor, monitor_pipeline, PipelineMetrics
        MONITORING_AVAILABLE = True
    except ImportError:
        MONITORING_AVAILABLE = False
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

    def __init__(self, gx_context_path: Optional[str] = None, enable_monitoring: bool = True):
        """Initialize the smart data cleaner."""
        self.gx_context_path = gx_context_path or str(Path(__file__).parent / "gx")
        self.context = None
        self.cleaning_history = []

        # Initialize monitoring if available
        self.enable_monitoring = enable_monitoring and MONITORING_AVAILABLE
        if self.enable_monitoring:
            self.monitor = GXPipelineMonitor("data/monitoring")
            logger.info("🔍 Monitoring enabled for GX pipeline")
        else:
            self.monitor = None
            if enable_monitoring and not MONITORING_AVAILABLE:
                logger.warning("⚠️ Monitoring requested but not available")

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
        """Create a batch request for DataFrame validation using correct GX 1.x API."""
        try:
            # Use the correct GX 1.x approach for runtime data
            datasource_name = "chicago_smb_pandas_datasource"

            # Try to get or create datasource
            try:
                datasource = self.context.data_sources.get(datasource_name)
            except:
                datasource = self.context.data_sources.add_pandas(name=datasource_name)

            # Get or create data asset
            try:
                asset = datasource.get_asset(dataset_name)
            except:
                asset = datasource.add_dataframe_asset(name=dataset_name)

            # Create batch request with correct GX 1.x API - options parameter with dataframe key
            return asset.build_batch_request(options={"dataframe": df})

        except Exception as e:
            logger.warning(f"Failed to create batch request via datasource: {e}")
            logger.error(f"Full error details: {e}")
            return None

    def _standardize_id_field(self, value, field_name: str) -> str:
        """Standardize mixed-type ID fields for consistency."""
        try:
            if pd.isna(value) or value == '' or str(value).lower() in ['none', 'nan']:
                return None

            # Convert to string and clean
            str_val = str(value).strip()

            # Handle pipe-separated multiple IDs (like business_activity_id)
            if '|' in str_val:
                # Keep as-is for multiple IDs, just clean whitespace
                parts = [part.strip() for part in str_val.split('|')]
                return ' | '.join(parts)

            # For permit numbers, preserve alpha prefixes
            if field_name.lower() in ['permit_', 'permit_number'] and str_val.startswith(('B', 'E', 'P', 'N')):
                return str_val.upper()

            # For numeric-like IDs, standardize format but keep as string
            if str_val.replace('.', '').replace('-', '').isdigit():
                # Remove trailing .0 if present
                if str_val.endswith('.0'):
                    str_val = str_val[:-2]
                return str_val

            # Default: return cleaned string
            return str_val

        except Exception:
            # Fallback: convert to string
            return str(value) if value is not None else None

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
        # Start monitoring if enabled
        execution_id = None
        if self.enable_monitoring:
            execution_id = self.monitor.start_pipeline_monitoring(dataset_name)
            self.monitor.log_data_metrics(execution_id, df)

        try:
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

            # Remove duplicate coordinate fields (prefer latitude/longitude over location_* variants)
            cleaned_df = self._deduplicate_coordinate_fields(cleaned_df)

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

            successful_transformations = sum(1 for t in transformation_log if t['success'])
            total_transformations = len(transformation_log)
            success_rate = (successful_transformations / total_transformations * 100) if total_transformations > 0 else 0

            print(f"   Successful transformations: {successful_transformations}")
            print(f"   Success rate: {success_rate:.1f}% ({successful_transformations}/{total_transformations})")

            # Log monitoring metrics if enabled
            if self.enable_monitoring and execution_id:
                self.monitor.log_data_metrics(execution_id, df, cleaned_df)
                self.monitor.log_transformation_results(execution_id, total_transformations, successful_transformations)

                # Log any errors
                failed_transformations = [t for t in transformation_log if not t['success']]
                for failed in failed_transformations:
                    error_msg = f"Field '{failed['field']}': {failed.get('error', 'Unknown error')}"
                    self.monitor.log_error(execution_id, error_msg, "ERROR")

                # Calculate data quality score
                quality_score = self.monitor.calculate_data_quality_score(execution_id, cleaned_df)

                # Finish monitoring
                final_metrics = self.monitor.finish_pipeline_monitoring(execution_id)

            return cleaned_df

        except Exception as e:
            # Log error to monitoring if enabled
            if self.enable_monitoring and execution_id:
                self.monitor.log_error(execution_id, f"Pipeline failure: {str(e)}", "ERROR")
                self.monitor.finish_pipeline_monitoring(execution_id)

            # Re-raise the exception
            raise e

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
                # Standardize ZIP codes and convert to category
                df[field] = (df[field].astype(str)
                                   .str.extract(r'(\d{5})')[0]
                                   .fillna('00000'))
                # Convert to category since ZIP codes have limited unique values
                df[field] = df[field].astype('category')
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Standardized ZIP code format and converted to category'
                }

            # String transformations
            elif desired_type == 'string':
                # Handle mixed-type ID fields intelligently
                if any(keyword in field.lower() for keyword in ['id', 'permit', 'license_number', 'account']):
                    # Special handling for ID fields with mixed types
                    df[field] = df[field].apply(lambda x: self._standardize_id_field(x, field))
                else:
                    # Regular string cleaning
                    df[field] = (df[field].astype(str)
                                       .str.strip()
                                       .replace('nan', '')
                                       .replace('None', ''))
                    # Replace empty strings with None for better data quality
                    df[field] = df[field].replace('', None)
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Converted to cleaned string'
                }

            # Float transformations
            elif desired_type == 'float64':
                # Handle empty/null values in geographic coordinates
                if any(keyword in field.lower() for keyword in ['latitude', 'longitude', 'lat', 'lng', 'coord']):
                    # Replace empty strings with NaN for geographic fields
                    df[field] = df[field].replace('', None)
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    # Keep as float64 with NaN for missing coordinates
                else:
                    # Regular numeric conversion
                    df[field] = pd.to_numeric(df[field], errors='coerce').astype('float64')
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Converted to float64'
                }

            # Boolean transformations
            elif desired_type == 'bool':
                # Convert Y/N, True/False, 1/0 to boolean
                def convert_to_bool(val):
                    if pd.isna(val) or val == '' or str(val).lower() in ['none', 'nan']:
                        return None
                    val_str = str(val).lower().strip()
                    if val_str in ['y', 'yes', 'true', '1', 'active']:
                        return True
                    elif val_str in ['n', 'no', 'false', '0', 'inactive']:
                        return False
                    else:
                        return None

                df[field] = df[field].apply(convert_to_bool)
                # Convert to nullable boolean
                df[field] = df[field].astype('boolean')
                return {
                    'success': True,
                    'dataframe': df,
                    'transformation': f'Converted to boolean'
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

        # Add geo-friendly columns for building permits (for Looker Studio)
        # This runs outside the try/except to ensure it always executes
        if dataset_name == 'building_permits':
            self._add_geo_columns_for_building_permits(df)

        return df

    def _add_geo_columns_for_building_permits(self, df: pd.DataFrame) -> None:
        """Add geo-friendly columns for Looker Studio visualization."""
        try:
            # Check if we have the required address components
            address_components = ['street_number', 'street_direction', 'street_name']
            has_address_data = all(col in df.columns for col in address_components)

            if has_address_data:
                # Create full_address column for Google Maps (Address type in Looker Studio)
                def create_full_address(row):
                    parts = []

                    # Add street number if available
                    if pd.notna(row.get('street_number')) and str(row.get('street_number')).strip():
                        parts.append(str(row['street_number']).strip())

                    # Add street direction if available
                    if pd.notna(row.get('street_direction')) and str(row.get('street_direction')).strip():
                        parts.append(str(row['street_direction']).strip())

                    # Add street name if available
                    if pd.notna(row.get('street_name')) and str(row.get('street_name')).strip():
                        parts.append(str(row['street_name']).strip())

                    # Combine with Chicago, Illinois
                    if parts:
                        street_address = ' '.join(parts)
                        return f"{street_address}, Chicago, Illinois"
                    else:
                        return "Chicago, Illinois"  # Fallback for incomplete addresses

                df['full_address'] = df.apply(create_full_address, axis=1)
                print(f"   ✅ Added full_address column for Google Maps visualization")

                # Create city column for Geo charts (City type in Looker Studio)
                df['city'] = 'Chicago'
                print(f"   ✅ Added city column for Geo chart visualization")

                # Log some examples for verification
                non_empty_addresses = df[df['full_address'] != 'Chicago, Illinois']['full_address'].head(3)
                if not non_empty_addresses.empty:
                    print(f"   📍 Sample addresses: {list(non_empty_addresses)}")

            else:
                print(f"   ⚠️  Missing address components for geo columns")

        except Exception as e:
            print(f"   ⚠️  Error adding geo columns: {e}")

        return df

    def _deduplicate_coordinate_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate coordinate fields, preferring standard latitude/longitude over location_* variants.

        Args:
            df: DataFrame that may contain duplicate coordinate fields

        Returns:
            DataFrame with deduplicated coordinate fields
        """
        # Check for duplicate coordinate fields
        has_lat = 'latitude' in df.columns
        has_lon = 'longitude' in df.columns
        has_location_lat = 'location_latitude' in df.columns
        has_location_lon = 'location_longitude' in df.columns

        dropped_fields = []

        # If we have both latitude and location_latitude, prefer latitude
        if has_lat and has_location_lat:
            # Copy non-null values from location_latitude to latitude if latitude is null
            null_mask = df['latitude'].isnull()
            if null_mask.any() and df['location_latitude'].notnull().any():
                df.loc[null_mask, 'latitude'] = df.loc[null_mask, 'location_latitude']

            # Drop the duplicate field
            df = df.drop(columns=['location_latitude'])
            dropped_fields.append('location_latitude')

        # If we have both longitude and location_longitude, prefer longitude
        if has_lon and has_location_lon:
            # Copy non-null values from location_longitude to longitude if longitude is null
            null_mask = df['longitude'].isnull()
            if null_mask.any() and df['location_longitude'].notnull().any():
                df.loc[null_mask, 'longitude'] = df.loc[null_mask, 'location_longitude']

            # Drop the duplicate field
            df = df.drop(columns=['location_longitude'])
            dropped_fields.append('location_longitude')

        # If we only have location_* fields, rename them to standard names
        elif has_location_lat and not has_lat:
            df = df.rename(columns={'location_latitude': 'latitude'})
            dropped_fields.append('location_latitude → latitude')

        elif has_location_lon and not has_lon:
            df = df.rename(columns={'location_longitude': 'longitude'})
            dropped_fields.append('location_longitude → longitude')

        if dropped_fields:
            print(f"\n🔧 Coordinate field deduplication:")
            for field in dropped_fields:
                print(f"   ✅ {field}")

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
                # Use correct GX 1.x API for deletion
                self.context.suites.delete(suite_name)
            except:
                pass

            try:
                # Use correct GX 1.x API
                import great_expectations as gx
                suite = self.context.suites.add_or_update(gx.ExpectationSuite(name=suite_name))
            except Exception as e:
                logger.warning(f"Could not create expectation suite via add_or_update: {e}")
                try:
                    # Try to get existing suite
                    suite = self.context.suites.get(suite_name)
                except:
                    # Create new suite
                    suite = self.context.suites.add(gx.ExpectationSuite(name=suite_name))

            # Get desired schema for creating expectations
            desired_schema = DesiredSchemaManager.get_desired_schema(dataset_name)

            # Add basic expectations
            expectations_added = 0

            # Table-level expectations using correct GX 1.x API
            import great_expectations as gx
            suite.add_expectation(gx.expectations.ExpectTableRowCountToBeBetween(min_value=1))
            expectations_added += 1

            # Field-level expectations
            for field in desired_schema.fields:
                if field.name not in df.columns:
                    continue

                # Column exists expectation
                suite.add_expectation(gx.expectations.ExpectColumnToExist(column=field.name))
                expectations_added += 1

                # Required field expectations
                if field.required and not field.nullable:
                    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column=field.name))
                    expectations_added += 1

                # Type-specific expectations
                if field.desired_type == DesiredDataType.INTEGER:
                    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeOfType(column=field.name, type_="int"))
                    expectations_added += 1

                elif field.desired_type == DesiredDataType.DATE:
                    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeOfType(column=field.name, type_="datetime64"))
                    expectations_added += 1

                elif field.desired_type == DesiredDataType.CURRENCY:
                    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeOfType(column=field.name, type_="float"))
                    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column=field.name, min_value=0))
                    expectations_added += 2

                # Validation rules from field definition
                if field.validation_rules:
                    for rule_name, rule_value in field.validation_rules.items():
                        if rule_name == "min_value" and rule_name == "max_value":
                            suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
                                column=field.name,
                                min_value=field.validation_rules.get("min_value"),
                                max_value=field.validation_rules.get("max_value")
                            ))
                            expectations_added += 1

            # Save the suite using GX 1.x API
            # Note: In GX 1.x, suites are automatically saved when added to context

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
                # Create batch request
                batch_request = self._create_batch_request(df, dataset_name)
                if batch_request is None:
                    print(f"   ❌ Could not create batch request")
                    return None

                # Create validator
                validator = self.context.get_validator(
                    batch_request=batch_request,
                    expectation_suite_name=suite.name
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
                        # Use correct GX 1.x attribute 'type' instead of 'expectation_type'
                        expectation = result.expectation_config.type
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
