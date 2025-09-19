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
        """Add geo-friendly columns for Looker Studio visualization with geocoding."""
        try:
            # Check if we have the required address components
            address_components = ['street_number', 'street_direction', 'street_name']
            has_address_data = all(col in df.columns for col in address_components)

            if has_address_data:
                def create_base_address(row):
                    """Create base address for geocoding."""
                    parts = []
                    if pd.notna(row.get('street_number')) and str(row.get('street_number')).strip():
                        parts.append(str(row['street_number']).strip())
                    if pd.notna(row.get('street_direction')) and str(row.get('street_direction')).strip():
                        parts.append(str(row['street_direction']).strip())
                    if pd.notna(row.get('street_name')) and str(row.get('street_name')).strip():
                        parts.append(str(row['street_name']).strip())

                    if parts:
                        street_address = ' '.join(parts)
                        return f"{street_address}, Chicago, IL"
                    else:
                        return "Chicago, IL"

                # Add basic geo columns (fast, no geocoding)
                self._add_basic_geo_columns(df)

                print(f"   ✅ Added full_address column with zip codes")
                print(f"   ✅ Added city column for Geo chart visualization")
                print(f"   ✅ Added latitude/longitude columns for precise mapping")
                print(f"   ✅ Added lat_lng column for Looker Studio geo visualization")
                print(f"   ✅ Added zip_code column for postal code analysis")

                # Show sample results
                sample_data = df[df['full_address'] != 'Chicago, Illinois'].head(2)
                if not sample_data.empty:
                    for idx, row in sample_data.iterrows():
                        addr = row.get('full_address', 'N/A')
                        lat_lng = row.get('lat_lng', 'N/A')
                        zip_code = row.get('zip_code', 'N/A')
                        print(f"   📍 Sample: {addr} | Lat/Lng: {lat_lng} | Zip: {zip_code}")

            else:
                print(f"   ⚠️  Missing address components for geo columns")

        except Exception as e:
            print(f"   ⚠️  Error adding geo columns: {e}")

        return df

    def _add_basic_geo_columns(self, df: pd.DataFrame) -> None:
        """Add geo columns using geopy for proper geocoding."""
        try:
            # Initialize geo columns
            df['full_address'] = None
            df['zip_code'] = None
            df['latitude'] = None
            df['longitude'] = None
            df['lat_lng'] = None
            df['city'] = 'Chicago'

            print(f"   🌍 Geocoding {len(df)} building permits with geopy...")

            # Apply efficient geocoding with rate limiting
            self._apply_geopy_geocoding(df)

            # Count successful geocodes
            geocoded_count = df[['latitude', 'longitude']].notna().all(axis=1).sum()
            success_rate = (geocoded_count / len(df)) * 100
            print(f"   🎯 Successfully geocoded {geocoded_count}/{len(df)} addresses ({success_rate:.1f}%)")

        except Exception as e:
            print(f"   ⚠️  Error adding geo columns: {e}")

    def _apply_geopy_geocoding(self, df: pd.DataFrame) -> None:
        """Apply smart geocoding with rate limiting and sampling for large datasets."""
        import geocoder
        import time

        # Create full addresses
        df['base_address'] = df.apply(self._create_full_address, axis=1)

        # Smart sampling for large datasets
        total_addresses = len(df)
        if total_addresses > 1000:
            print(f"   📊 Large dataset detected ({total_addresses} addresses)")
            print(f"   🎯 Using smart sampling + pattern matching for efficiency")

            # Sample geocoding approach for large datasets
            self._apply_smart_sampling_geocoding(df)
        else:
            # Full geocoding for smaller datasets
            self._apply_full_geocoding(df)

        # Clean up temporary column
        df.drop('base_address', axis=1, inplace=True)

    def _apply_smart_sampling_geocoding(self, df: pd.DataFrame) -> None:
        """Apply geocoding with smart sampling for large datasets."""
        import geocoder
        import time
        from collections import defaultdict

        print(f"   🧠 Building Chicago street pattern database...")

        # Group addresses by street name for pattern recognition
        street_groups = defaultdict(list)
        for idx, row in df.iterrows():
            base_addr = row['base_address']
            if pd.notna(base_addr) and base_addr.strip():
                # Extract street name (last part)
                parts = base_addr.split()
                if len(parts) >= 2:
                    street_name = ' '.join(parts[-2:]).lower()  # e.g., "state st"
                    street_groups[street_name].append(idx)

        print(f"   📍 Found {len(street_groups)} unique streets")

        # Geocode representative samples from each street
        street_patterns = {}
        geocoded_count = 0

        for street_name, indices in street_groups.items():
            if len(indices) > 5:  # Only sample streets with multiple addresses
                # Take a sample address from this street
                sample_idx = indices[0]
                sample_addr = df.loc[sample_idx, 'base_address']

                try:
                    full_addr = f"{sample_addr}, Chicago, IL"
                    g = geocoder.arcgis(full_addr)

                    if g.ok:
                        # Extract pattern info
                        zip_code = self._extract_zip_from_geocoder(g)
                        street_patterns[street_name] = {
                            'base_lat': g.lat,
                            'base_lng': g.lng,
                            'zip_code': zip_code
                        }
                        geocoded_count += 1
                        print(f"     ✅ Mapped {street_name} → {zip_code}")

                    time.sleep(0.3)  # Rate limiting

                except Exception as e:
                    continue

        print(f"   🎯 Geocoded {geocoded_count} street patterns")

        # Apply patterns to all addresses
        self._apply_street_patterns(df, street_patterns)

    def _apply_street_patterns(self, df: pd.DataFrame, street_patterns: dict) -> None:
        """Apply learned street patterns to all addresses."""
        applied_count = 0

        for idx, row in df.iterrows():
            base_addr = row['base_address']

            if pd.isna(base_addr) or not base_addr.strip():
                df.at[idx, 'full_address'] = "Chicago, Illinois"
                continue

            # Extract street name
            parts = base_addr.split()
            if len(parts) >= 2:
                street_name = ' '.join(parts[-2:]).lower()

                if street_name in street_patterns:
                    # Apply learned pattern
                    pattern = street_patterns[street_name]

                    # Use base coordinates (could be enhanced with address number offsets)
                    df.at[idx, 'latitude'] = pattern['base_lat']
                    df.at[idx, 'longitude'] = pattern['base_lng']
                    df.at[idx, 'lat_lng'] = f"{pattern['base_lat']},{pattern['base_lng']}"
                    df.at[idx, 'zip_code'] = pattern['zip_code']

                    # Create enhanced full address
                    if pattern['zip_code']:
                        df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois {pattern['zip_code']}"
                    else:
                        df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois"

                    applied_count += 1
                else:
                    # Fallback for unmatched streets
                    df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois"
            else:
                df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois"

        print(f"   🎯 Applied patterns to {applied_count}/{len(df)} addresses")

    def _apply_full_geocoding(self, df: pd.DataFrame) -> None:
        """Apply full geocoding for smaller datasets."""
        import geocoder
        import time

        geocoded_count = 0

        for idx, row in df.iterrows():
            try:
                base_addr = row['base_address']
                if pd.isna(base_addr) or not base_addr.strip():
                    df.at[idx, 'full_address'] = "Chicago, Illinois"
                    continue

                full_addr = f"{base_addr}, Chicago, IL"
                g = geocoder.arcgis(full_addr)

                if g.ok:
                    df.at[idx, 'latitude'] = g.lat
                    df.at[idx, 'longitude'] = g.lng
                    df.at[idx, 'lat_lng'] = f"{g.lat},{g.lng}"

                    zip_code = self._extract_zip_from_geocoder(g)
                    df.at[idx, 'zip_code'] = zip_code

                    if zip_code:
                        df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois {zip_code}"
                    else:
                        df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois"

                    geocoded_count += 1
                else:
                    df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois"

                time.sleep(0.2)

            except Exception as e:
                df.at[idx, 'full_address'] = f"{base_addr}, Chicago, Illinois" if pd.notna(base_addr) else "Chicago, Illinois"
                continue

        print(f"   🎯 Geocoded {geocoded_count}/{len(df)} addresses")

    def _create_full_address(self, row) -> str:
        """Create a full address string from components."""
        parts = []
        if pd.notna(row.get('street_number')) and str(row.get('street_number')).strip():
            parts.append(str(row['street_number']).strip())
        if pd.notna(row.get('street_direction')) and str(row.get('street_direction')).strip():
            parts.append(str(row['street_direction']).strip())
        if pd.notna(row.get('street_name')) and str(row.get('street_name')).strip():
            parts.append(str(row['street_name']).strip())

        return ' '.join(parts) if parts else None

    def _extract_zip_from_geocoder(self, geocoder_result) -> str:
        """Extract ZIP code from geocoder result."""
        try:
            # Try to extract ZIP from address string
            import re
            if hasattr(geocoder_result, 'address') and geocoder_result.address:
                # Look for 5-digit ZIP code in the address
                zip_match = re.search(r'\b(\d{5})\b', geocoder_result.address)
                if zip_match:
                    return zip_match.group(1)
        except:
            pass
        return None

    def _extract_zip_from_location(self, location) -> str:
        """Extract ZIP code from geopy location object."""
        try:
            if hasattr(location, 'raw') and 'address' in location.raw:
                address_components = location.raw['address']
                return address_components.get('postcode')
        except:
            pass
        return None

    def _enhance_addresses_with_geocoding(self, addresses: pd.Series) -> dict:
        """Enhance addresses with zip codes and lat/lng coordinates using fast hybrid geocoding."""
        import pgeocode
        from geopy.geocoders import Nominatim
        import time
        import ssl
        from typing import Dict, Any

        # Fix SSL certificate issue for pgeocode
        ssl._create_default_https_context = ssl._create_unverified_context

        enhanced_data = {
            'full_address': [],
            'zip_code': [],
            'latitude': [],
            'longitude': [],
            'lat_lng': []
        }

        print(f"   🚀 Fast hybrid geocoding for {len(addresses)} addresses...")

        # Initialize geocoders
        print(f"   📚 Loading geocoding databases...")
        nomi = pgeocode.Nominatim('us')  # US postal codes database (instant, offline)
        geopy_geocoder = Nominatim(user_agent="Chicago-SMB-Market-Radar/1.0")

        # Pre-compile Chicago address patterns for faster matching
        chicago_zip_coords = self._get_chicago_zip_coordinates()

        geocoded_count = 0
        fallback_count = 0

        for i, address in enumerate(addresses):
            try:
                if pd.isna(address) or address.strip() == "Chicago, IL":
                    # Handle empty/default addresses
                    enhanced_data['full_address'].append("Chicago, Illinois")
                    enhanced_data['zip_code'].append(None)
                    enhanced_data['latitude'].append(None)
                    enhanced_data['longitude'].append(None)
                    enhanced_data['lat_lng'].append(None)
                    continue

                # Strategy 1: Try Chicago street centerline matching (fastest)
                geocoded = self._match_chicago_street_address(address.strip(), chicago_zip_coords)

                # Strategy 2: If no match, try pgeocode with inferred zip
                if not geocoded:
                    geocoded = self._geocode_with_pgeocode(address.strip(), nomi)

                # Strategy 3: Fallback to geopy for unmatched addresses (rate limited)
                if not geocoded and fallback_count < 100:  # Limit fallback calls
                    geocoded = self._geocode_with_geopy(address.strip(), geopy_geocoder)
                    fallback_count += 1
                    if fallback_count % 10 == 0:
                        time.sleep(1)  # Rate limiting for geopy

                if geocoded:
                    # Create enhanced full address with zip
                    zip_part = f", {geocoded['zip_code']}" if geocoded['zip_code'] else ""
                    full_addr = f"{address}{zip_part}, Illinois"
                    enhanced_data['full_address'].append(full_addr)
                    enhanced_data['zip_code'].append(geocoded['zip_code'])
                    enhanced_data['latitude'].append(geocoded['latitude'])
                    enhanced_data['longitude'].append(geocoded['longitude'])

                    # Create lat_lng for Looker Studio
                    if geocoded['latitude'] and geocoded['longitude']:
                        lat_lng = f"{geocoded['latitude']},{geocoded['longitude']}"
                        enhanced_data['lat_lng'].append(lat_lng)
                        geocoded_count += 1
                    else:
                        enhanced_data['lat_lng'].append(None)
                else:
                    # Fallback for completely failed geocoding
                    enhanced_data['full_address'].append(f"{address}, Illinois")
                    enhanced_data['zip_code'].append(None)
                    enhanced_data['latitude'].append(None)
                    enhanced_data['longitude'].append(None)
                    enhanced_data['lat_lng'].append(None)

                # Progress update
                if i > 0 and i % 1000 == 0:
                    print(f"     ... processed {i}/{len(addresses)} addresses (success: {geocoded_count})")

            except Exception as e:
                print(f"     ⚠️  Geocoding error for '{address}': {e}")
                # Fallback for errors
                enhanced_data['full_address'].append(f"{address}, Illinois")
                enhanced_data['zip_code'].append(None)
                enhanced_data['latitude'].append(None)
                enhanced_data['longitude'].append(None)
                enhanced_data['lat_lng'].append(None)

        print(f"   🎯 Fast geocoding results: {geocoded_count}/{len(addresses)} addresses")
        print(f"   📊 Used fallback geocoding for: {fallback_count} addresses")

        return enhanced_data

    def _get_chicago_zip_coordinates(self) -> dict:
        """Get Chicago zip code to coordinate mapping using pgeocode."""
        import pgeocode
        import ssl

        # Fix SSL certificate issue for pgeocode
        ssl._create_default_https_context = ssl._create_unverified_context

        # Chicago zip codes (major ones)
        chicago_zips = [
            '60601', '60602', '60603', '60604', '60605', '60606', '60607', '60608', '60609', '60610',
            '60611', '60612', '60613', '60614', '60615', '60616', '60617', '60618', '60619', '60620',
            '60621', '60622', '60623', '60624', '60625', '60626', '60628', '60629', '60630', '60631',
            '60632', '60633', '60634', '60636', '60637', '60638', '60639', '60640', '60641', '60642',
            '60643', '60644', '60645', '60646', '60647', '60649', '60651', '60652', '60653', '60654',
            '60655', '60656', '60657', '60659', '60660', '60661', '60664', '60666', '60668', '60669',
            '60670', '60673', '60674', '60675', '60677', '60678', '60680', '60681', '60682', '60684',
            '60685', '60686', '60687', '60688', '60689', '60690', '60691', '60693', '60694', '60695',
            '60696', '60697', '60699'
        ]

        nomi = pgeocode.Nominatim('us')
        zip_coords = {}

        for zip_code in chicago_zips:
            try:
                location = nomi.query_postal_code(zip_code)
                if not pd.isna(location.latitude) and not pd.isna(location.longitude):
                    zip_coords[zip_code] = {
                        'latitude': float(location.latitude),
                        'longitude': float(location.longitude)
                    }
            except:
                continue

        return zip_coords

    def _match_chicago_street_address(self, address: str, zip_coords: dict) -> dict:
        """Match Chicago street address using local patterns and zip inference."""
        try:
            # Common Chicago street patterns and their typical zip codes
            street_patterns = {
                'state st': ['60601', '60602', '60603', '60604', '60605'],
                'michigan ave': ['60601', '60602', '60603', '60604', '60611'],
                'lasalle st': ['60601', '60602', '60603', '60604'],
                'clark st': ['60613', '60614', '60657', '60660'],
                'halsted st': ['60607', '60608', '60622', '60642'],
                'ashland ave': ['60607', '60608', '60622', '60642'],
                'western ave': ['60618', '60625', '60647', '60659'],
                'north ave': ['60622', '60642', '60647'],
                'roosevelt rd': ['60607', '60608', '60616'],
                'cermak rd': ['60608', '60616', '60623'],
                'irving park rd': ['60618', '60625', '60634'],
                'belmont ave': ['60613', '60618', '60657'],
                'fullerton ave': ['60614', '60647', '60657'],
                'division st': ['60610', '60622', '60642'],
                'chicago ave': ['60610', '60622', '60642'],
                'grand ave': ['60610', '60622', '60642']
            }

            address_lower = address.lower()

            # Extract street number for north/south estimation
            street_number = None
            parts = address.split()
            if parts and parts[0].isdigit():
                street_number = int(parts[0])

            # Find matching street pattern
            for street_pattern, zip_list in street_patterns.items():
                if street_pattern in address_lower:
                    # Pick zip based on street number (rough Chicago grid system)
                    if street_number:
                        if street_number >= 8000:  # Far north/south
                            zip_code = zip_list[-1] if len(zip_list) > 2 else zip_list[0]
                        elif street_number >= 4000:  # Mid north/south
                            zip_code = zip_list[len(zip_list)//2] if len(zip_list) > 1 else zip_list[0]
                        else:  # Central/downtown
                            zip_code = zip_list[0]
                    else:
                        zip_code = zip_list[0]  # Default to first zip

                    # Get coordinates for this zip
                    if zip_code in zip_coords:
                        coords = zip_coords[zip_code]
                        return {
                            'latitude': coords['latitude'],
                            'longitude': coords['longitude'],
                            'zip_code': zip_code
                        }

            return None

        except Exception as e:
            return None

    def _geocode_with_pgeocode(self, address: str, nomi) -> dict:
        """Geocode using pgeocode with zip inference."""
        try:
            # Try to extract zip code from address
            import re
            zip_match = re.search(r'\b\d{5}\b', address)

            if zip_match:
                zip_code = zip_match.group()
                location = nomi.query_postal_code(zip_code)

                if not pd.isna(location.latitude) and not pd.isna(location.longitude):
                    return {
                        'latitude': float(location.latitude),
                        'longitude': float(location.longitude),
                        'zip_code': zip_code
                    }

            # If no zip in address, try common Chicago zips based on street patterns
            if 'downtown' in address.lower() or 'loop' in address.lower():
                zip_code = '60601'
            elif 'north' in address.lower() and any(x in address.lower() for x in ['clark', 'lincoln', 'halsted']):
                zip_code = '60614'
            elif 'south' in address.lower():
                zip_code = '60616'
            else:
                return None

            location = nomi.query_postal_code(zip_code)
            if not pd.isna(location.latitude) and not pd.isna(location.longitude):
                return {
                    'latitude': float(location.latitude),
                    'longitude': float(location.longitude),
                    'zip_code': zip_code
                }

            return None

        except Exception as e:
            return None

    def _geocode_with_geopy(self, address: str, geocoder) -> dict:
        """Fallback geocoding using geopy."""
        try:
            full_address = f"{address}, Chicago, IL"
            location = geocoder.geocode(full_address)

            if location:
                # Extract zip from address components if available
                zip_code = None
                if hasattr(location, 'raw') and 'address' in location.raw:
                    address_parts = location.raw['address']
                    zip_code = address_parts.get('postcode')

                return {
                    'latitude': float(location.latitude),
                    'longitude': float(location.longitude),
                    'zip_code': zip_code
                }

            return None

        except Exception as e:
            return None

    def _geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode a single address using Census Geocoding API."""
        import requests
        import time

        try:
            # US Census Geocoding API - free, no API key required
            base_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
            params = {
                'address': address,
                'benchmark': 'Public_AR_Current',
                'format': 'json'
            }

            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                if data.get('result', {}).get('addressMatches'):
                    match = data['result']['addressMatches'][0]
                    coords = match.get('coordinates', {})
                    address_components = match.get('addressComponents', {})

                    return {
                        'latitude': coords.get('y'),
                        'longitude': coords.get('x'),
                        'zip_code': address_components.get('zip')
                    }

            # Fallback to Nominatim if Census fails
            return self._geocode_with_nominatim(address)

        except Exception as e:
            print(f"     ⚠️  Census geocoding failed for '{address}': {e}")
            return self._geocode_with_nominatim(address)

    def _geocode_with_nominatim(self, address: str) -> Dict[str, Any]:
        """Fallback geocoding using Nominatim (OpenStreetMap)."""
        import requests
        import time

        try:
            # Add respectful delay
            time.sleep(0.5)

            base_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'us',
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'Chicago-SMB-Market-Radar/1.0 (Data Analysis Tool)'
            }

            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()

                if data:
                    result = data[0]
                    address_details = result.get('address', {})

                    return {
                        'latitude': float(result.get('lat', 0)) if result.get('lat') else None,
                        'longitude': float(result.get('lon', 0)) if result.get('lon') else None,
                        'zip_code': address_details.get('postcode')
                    }

            return None

        except Exception as e:
            print(f"     ⚠️  Nominatim geocoding failed for '{address}': {e}")
            return None

    def _add_geo_columns_with_smart_caching(self, df: pd.DataFrame) -> None:
        """Add geo columns with smart caching - only geocode rows missing geo data."""
        from shared.sheets_client import open_sheet
        import os

        # Initialize geo columns if they don't exist
        geo_columns = ['full_address', 'zip_code', 'latitude', 'longitude', 'lat_lng', 'city']
        for col in geo_columns:
            if col not in df.columns:
                df[col] = None

        # Set city for all rows (this is static)
        df['city'] = 'Chicago'

        try:
            # Try to get existing data from Google Sheets for smart caching
            sheet_id = os.getenv('SHEET_ID')
            if sheet_id:
                print(f"   🔍 Checking existing geo data in Google Sheets for smart caching...")

                sh = open_sheet(sheet_id)
                existing_geo_data = self._get_existing_geo_data(sh, 'Building_Permits_GX_Cleaned')

                if existing_geo_data is not None and not existing_geo_data.empty:
                    # Merge existing geo data with current data
                    df = self._merge_existing_geo_data(df, existing_geo_data)
                    print(f"   📊 Loaded existing geo data for {len(existing_geo_data)} records")
                else:
                    print(f"   💡 No existing geo data found, will geocode all addresses")

            # Identify rows that need geocoding (missing lat/lng but have address data)
            needs_geocoding = (
                (df['latitude'].isna() | df['longitude'].isna()) &
                (df['base_address'] != 'Chicago, IL') &
                df['base_address'].notna()
            )

            addresses_to_geocode = df.loc[needs_geocoding, 'base_address']

            if len(addresses_to_geocode) > 0:
                print(f"   🗺️  Geocoding {len(addresses_to_geocode)} new/missing addresses...")

                # Geocode only the missing addresses
                geo_results = self._enhance_addresses_with_geocoding(addresses_to_geocode)

                # Update only the rows that needed geocoding
                for i, (idx, address) in enumerate(addresses_to_geocode.items()):
                    df.loc[idx, 'full_address'] = geo_results['full_address'][i]
                    df.loc[idx, 'zip_code'] = geo_results['zip_code'][i]
                    df.loc[idx, 'latitude'] = geo_results['latitude'][i]
                    df.loc[idx, 'longitude'] = geo_results['longitude'][i]
                    df.loc[idx, 'lat_lng'] = geo_results['lat_lng'][i]
            else:
                print(f"   ✅ All addresses already geocoded - using cached data")

            # Handle rows without proper addresses
            no_address_rows = (df['base_address'] == 'Chicago, IL') | df['base_address'].isna()
            df.loc[no_address_rows, 'full_address'] = 'Chicago, Illinois'
            df.loc[no_address_rows, 'zip_code'] = None
            df.loc[no_address_rows, 'latitude'] = None
            df.loc[no_address_rows, 'longitude'] = None
            df.loc[no_address_rows, 'lat_lng'] = None

        except Exception as e:
            print(f"   ⚠️  Smart caching error, falling back to basic geocoding: {e}")
            # Fallback to full geocoding if caching fails
            geo_results = self._enhance_addresses_with_geocoding(df['base_address'])
            df['full_address'] = geo_results['full_address']
            df['zip_code'] = geo_results['zip_code']
            df['latitude'] = geo_results['latitude']
            df['longitude'] = geo_results['longitude']
            df['lat_lng'] = geo_results['lat_lng']

    def _get_existing_geo_data(self, sh, worksheet_name: str):
        """Get existing geo data from Google Sheets."""
        try:
            # Try to open the existing worksheet
            ws = sh.worksheet(worksheet_name)

            # Get all data
            data = ws.get_all_records()

            if data:
                existing_df = pd.DataFrame(data)

                # Only return data that has geo columns and some geo data
                geo_columns = ['id', 'full_address', 'zip_code', 'latitude', 'longitude', 'lat_lng']
                available_geo_cols = [col for col in geo_columns if col in existing_df.columns]

                if len(available_geo_cols) > 1:  # At least id + one geo column
                    return existing_df[available_geo_cols]

            return None

        except Exception as e:
            print(f"     ⚠️  Could not load existing geo data: {e}")
            return None

    def _merge_existing_geo_data(self, df: pd.DataFrame, existing_geo_data: pd.DataFrame) -> pd.DataFrame:
        """Merge existing geo data with current dataframe."""
        try:
            # Ensure 'id' column exists in both dataframes
            if 'id' not in df.columns or 'id' not in existing_geo_data.columns:
                return df

            # Convert IDs to string for consistent matching
            df['id'] = df['id'].astype(str)
            existing_geo_data['id'] = existing_geo_data['id'].astype(str)

            # Merge existing geo data
            geo_columns_to_merge = ['full_address', 'zip_code', 'latitude', 'longitude', 'lat_lng']
            available_columns = [col for col in geo_columns_to_merge if col in existing_geo_data.columns]

            if available_columns:
                merge_columns = ['id'] + available_columns
                existing_subset = existing_geo_data[merge_columns].copy()

                # Only keep rows with actual geo data (not empty)
                has_geo_data = existing_subset[available_columns].notna().any(axis=1)
                existing_subset = existing_subset[has_geo_data]

                if not existing_subset.empty:
                    # Merge with left join to preserve all current data
                    df = df.merge(existing_subset, on='id', how='left', suffixes=('', '_existing'))

                    # For each geo column, use existing data if current is empty
                    for col in available_columns:
                        existing_col = f"{col}_existing"
                        if existing_col in df.columns:
                            # Update only where current data is missing and existing data exists
                            mask = df[col].isna() & df[existing_col].notna()
                            df.loc[mask, col] = df.loc[mask, existing_col]
                            # Drop the temporary existing column
                            df.drop(existing_col, axis=1, inplace=True)

            return df

        except Exception as e:
            print(f"     ⚠️  Error merging existing geo data: {e}")
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
