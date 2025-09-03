"""
Great Expectations Pipeline Integration

This module integrates the GX data cleaning framework into the existing
Chicago SMB Market Radar data pipeline. It provides a seamless way to
upgrade from the current manual cleaning approach to automated, pattern-based
cleaning with comprehensive validation.

Integration points:
- Drop-in replacement for existing cleaning functions
- Compatible with current notebook workflow
- Preserves existing data pipeline structure
- Adds comprehensive validation and reporting
"""

import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add project paths
sys.path.append(str(Path(__file__).parent.parent / "step2_data_ingestion"))
sys.path.append(str(Path(__file__).parent.parent / "shared"))

# Import existing modules
from config_manager import load_settings
from sheets_client import open_sheet, upsert_worksheet, overwrite_with_dataframe

# Import our new GX modules
from gx_data_cleaning import SmartDataCleaner, batch_clean_datasets
from expectation_suites import ChicagoSMBExpectationSuites, create_all_chicago_suites

logger = logging.getLogger(__name__)

class GXPipelineManager:
    """
    Manages the integration of Great Expectations cleaning into the existing pipeline.

    This class serves as a bridge between the existing manual cleaning workflow
    and the new automated GX-based approach, allowing for gradual migration and
    A/B testing of cleaning strategies.
    """

    def __init__(self, use_gx: bool = True, fallback_to_manual: bool = True):
        """
        Initialize the pipeline manager.

        Args:
            use_gx: Whether to use Great Expectations cleaning (default: True)
            fallback_to_manual: Whether to fallback to manual cleaning on GX failure (default: True)
        """
        self.use_gx = use_gx
        self.fallback_to_manual = fallback_to_manual
        self.smart_cleaner = SmartDataCleaner() if use_gx else None
        self.cleaning_results = {}

    def clean_datasets_enhanced(self, datasets: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        """
        Enhanced dataset cleaning with GX integration.

        This is a drop-in replacement for the existing cleaning workflow but with
        Great Expectations validation and smart pattern-based cleaning.

        Args:
            datasets: Dictionary of dataset name -> DataFrame

        Returns:
            Tuple of (cleaned_datasets, cleaning_report)
        """
        print("🚀 ENHANCED DATA CLEANING WITH GREAT EXPECTATIONS")
        print("=" * 60)

        cleaned_datasets = {}
        cleaning_report = {
            'strategy_used': 'great_expectations' if self.use_gx else 'manual',
            'datasets_processed': [],
            'validation_results': {},
            'transformation_summary': {},
            'quality_improvements': {},
            'errors': []
        }

        for dataset_name, df in datasets.items():
            print(f"\n📊 Processing {dataset_name}...")

            try:
                if self.use_gx and self.smart_cleaner:
                    # Use Great Expectations smart cleaning
                    cleaned_df, validation_result = self._gx_clean_and_validate(df, dataset_name)

                    if cleaned_df is not None:
                        cleaned_datasets[dataset_name] = cleaned_df
                        cleaning_report['validation_results'][dataset_name] = validation_result
                        cleaning_report['datasets_processed'].append({
                            'name': dataset_name,
                            'method': 'great_expectations',
                            'success': True,
                            'original_shape': df.shape,
                            'cleaned_shape': cleaned_df.shape
                        })
                    else:
                        raise Exception("GX cleaning returned None")

                else:
                    # Use manual cleaning as fallback
                    cleaned_df = self._manual_clean_dataset(df, dataset_name)
                    cleaned_datasets[dataset_name] = cleaned_df
                    cleaning_report['datasets_processed'].append({
                        'name': dataset_name,
                        'method': 'manual',
                        'success': True,
                        'original_shape': df.shape,
                        'cleaned_shape': cleaned_df.shape
                    })

            except Exception as e:
                error_msg = f"Error cleaning {dataset_name}: {str(e)}"
                print(f"   ❌ {error_msg}")
                cleaning_report['errors'].append(error_msg)

                # Fallback to manual cleaning if enabled
                if self.fallback_to_manual:
                    print(f"   🔄 Falling back to manual cleaning for {dataset_name}")
                    try:
                        cleaned_df = self._manual_clean_dataset(df, dataset_name)
                        cleaned_datasets[dataset_name] = cleaned_df
                        cleaning_report['datasets_processed'].append({
                            'name': dataset_name,
                            'method': 'manual_fallback',
                            'success': True,
                            'original_shape': df.shape,
                            'cleaned_shape': cleaned_df.shape
                        })
                    except Exception as fallback_error:
                        print(f"   ❌ Fallback also failed: {fallback_error}")
                        # Use original dataset as last resort
                        cleaned_datasets[dataset_name] = df
                        cleaning_report['errors'].append(f"Fallback failed for {dataset_name}: {fallback_error}")
                else:
                    # Use original dataset if no fallback
                    cleaned_datasets[dataset_name] = df

        # Generate quality improvement summary
        cleaning_report['quality_improvements'] = self._calculate_quality_improvements(
            datasets, cleaned_datasets
        )

        # Print summary
        self._print_cleaning_summary(cleaning_report)

        return cleaned_datasets, cleaning_report

    def _gx_clean_and_validate(self, df: pd.DataFrame, dataset_name: str) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """Clean dataset using Great Expectations and validate."""
        try:
            # Use smart cleaner
            cleaned_df = self.smart_cleaner.execute_smart_cleaning(df, dataset_name)

            # Run validation
            validation_result = self.smart_cleaner.validate_with_gx(cleaned_df, dataset_name)

            return cleaned_df, validation_result or {}

        except Exception as e:
            print(f"   ❌ GX cleaning failed: {e}")
            return None, {'error': str(e)}

    def _manual_clean_dataset(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """
        Fallback manual cleaning using existing logic.

        This replicates the key transformations from the existing cleaning notebook
        to ensure compatibility when GX cleaning is not available.
        """
        print(f"   🔧 Applying manual cleaning to {dataset_name}")

        cleaned_df = df.copy()

        # Standard cleaning operations
        # 1. Remove completely empty rows
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(how='all')
        if len(cleaned_df) < initial_rows:
            print(f"      Removed {initial_rows - len(cleaned_df)} empty rows")

        # 2. Strip whitespace from text fields
        text_fields = cleaned_df.select_dtypes(include=['object']).columns
        for field in text_fields:
            cleaned_df[field] = cleaned_df[field].astype(str).str.strip()

        # 3. Dataset-specific cleaning
        if dataset_name == 'business_licenses':
            cleaned_df = self._clean_business_licenses_manual(cleaned_df)
        elif dataset_name == 'building_permits':
            cleaned_df = self._clean_building_permits_manual(cleaned_df)
        elif dataset_name == 'cta_boardings':
            cleaned_df = self._clean_cta_manual(cleaned_df)

        return cleaned_df

    def _clean_business_licenses_manual(self, df: pd.DataFrame) -> pd.DataFrame:
        """Manual cleaning specific to business licenses."""
        # Convert date fields
        date_fields = ['application_created_date', 'license_start_date', 'expiration_date',
                      'payment_date', 'date_issued']
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')

        # Convert numeric fields
        numeric_fields = ['community_area', 'ward', 'precinct', 'zip_code', 'latitude', 'longitude']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')

        # Fix date logic issues (start date > expiration date)
        if 'license_start_date' in df.columns and 'expiration_date' in df.columns:
            invalid_dates = df['license_start_date'] > df['expiration_date']
            if invalid_dates.sum() > 0:
                df.loc[invalid_dates, 'expiration_date'] = (
                    df.loc[invalid_dates, 'license_start_date'] + pd.DateOffset(years=1)
                )
                print(f"      Fixed {invalid_dates.sum()} invalid date sequences")

        return df

    def _clean_building_permits_manual(self, df: pd.DataFrame) -> pd.DataFrame:
        """Manual cleaning specific to building permits."""
        # Convert date fields
        date_fields = ['application_start_date', 'issue_date']
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')

        # Convert numeric fields
        numeric_fields = ['community_area', 'processing_time']
        fee_fields = [col for col in df.columns if 'fee' in col.lower()]

        for field in numeric_fields + fee_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')

        # Ensure non-negative fees
        for field in fee_fields:
            if field in df.columns:
                df.loc[df[field] < 0, field] = 0

        return df

    def _clean_cta_manual(self, df: pd.DataFrame) -> pd.DataFrame:
        """Manual cleaning specific to CTA data."""
        # Convert service_date
        if 'service_date' in df.columns:
            df['service_date'] = pd.to_datetime(df['service_date'], errors='coerce')

        # Convert total_rides to integer
        if 'total_rides' in df.columns:
            df['total_rides'] = pd.to_numeric(df['total_rides'], errors='coerce').astype('Int64')

        return df

    def _calculate_quality_improvements(self, original_datasets: Dict[str, pd.DataFrame],
                                      cleaned_datasets: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
        """Calculate quality improvement metrics."""
        improvements = {}

        for dataset_name in original_datasets.keys():
            if dataset_name in cleaned_datasets:
                orig_df = original_datasets[dataset_name]
                clean_df = cleaned_datasets[dataset_name]

                improvements[dataset_name] = {
                    'shape_change': {
                        'rows': f"{orig_df.shape[0]} → {clean_df.shape[0]}",
                        'columns': f"{orig_df.shape[1]} → {clean_df.shape[1]}"
                    },
                    'data_types': {
                        'original_numeric': len(orig_df.select_dtypes(include=['number']).columns),
                        'cleaned_numeric': len(clean_df.select_dtypes(include=['number']).columns),
                        'original_datetime': len(orig_df.select_dtypes(include=['datetime']).columns),
                        'cleaned_datetime': len(clean_df.select_dtypes(include=['datetime']).columns)
                    }
                }

                # Calculate null reduction for key fields
                if dataset_name == 'business_licenses' and 'community_area' in orig_df.columns:
                    orig_nulls = orig_df['community_area'].isnull().sum()
                    clean_nulls = clean_df['community_area'].isnull().sum()
                    improvements[dataset_name]['null_reduction'] = f"{orig_nulls} → {clean_nulls}"

        return improvements

    def _print_cleaning_summary(self, report: Dict[str, Any]):
        """Print a comprehensive cleaning summary."""
        print(f"\n🎯 CLEANING SUMMARY")
        print("=" * 40)
        print(f"Strategy Used: {report['strategy_used'].upper()}")
        print(f"Datasets Processed: {len(report['datasets_processed'])}")

        if report['errors']:
            print(f"Errors Encountered: {len(report['errors'])}")

        # Print per-dataset results
        for dataset_result in report['datasets_processed']:
            name = dataset_result['name']
            method = dataset_result['method']
            orig_shape = dataset_result['original_shape']
            clean_shape = dataset_result['cleaned_shape']

            print(f"\n  {name.upper()}:")
            print(f"    Method: {method}")
            print(f"    Shape: {orig_shape} → {clean_shape}")

            # Print validation results if available
            if name in report.get('validation_results', {}):
                val_result = report['validation_results'][name]
                if 'success_rate' in val_result:
                    print(f"    Validation: {val_result['success_rate']:.1%} success rate")

    def save_cleaned_data_to_sheets(self, cleaned_datasets: Dict[str, pd.DataFrame],
                                  suffix: str = "_GX_Cleaned") -> bool:
        """
        Save cleaned datasets to Google Sheets with GX suffix.

        This maintains compatibility with the existing workflow while clearly
        marking datasets that have been processed with Great Expectations.
        """
        print(f"\n💾 SAVING CLEANED DATA TO GOOGLE SHEETS")
        print("=" * 50)

        try:
            # Load Google Sheets connection
            settings = load_settings()
            sh = open_sheet(settings.sheet_id, settings.google_creds_path)

            # Define cleaned datasets and their target worksheet names
            worksheet_mapping = {
                'business_licenses': f'Business_Licenses{suffix}',
                'building_permits': f'Building_Permits{suffix}',
                'cta_boardings': f'CTA{suffix}'
            }

            saved_count = 0
            for dataset_name, df in cleaned_datasets.items():
                if dataset_name in worksheet_mapping:
                    worksheet_name = worksheet_mapping[dataset_name]

                    try:
                        print(f"\n📤 Saving {worksheet_name}...")
                        print(f"   Rows: {len(df):,}")
                        print(f"   Columns: {len(df.columns)}")

                        # Create or update worksheet
                        ws = upsert_worksheet(sh, worksheet_name,
                                            rows=len(df)+100, cols=len(df.columns)+5)
                        overwrite_with_dataframe(ws, df)

                        print(f"   ✅ SUCCESS: Saved to '{worksheet_name}' tab")
                        saved_count += 1

                    except Exception as e:
                        print(f"   ❌ ERROR saving {worksheet_name}: {str(e)}")
                        return False

            print(f"\n✅ SAVED {saved_count}/{len(cleaned_datasets)} DATASETS TO GOOGLE SHEETS")
            if suffix == "_GX_Cleaned":
                print(f"   🎯 Datasets marked with '{suffix}' suffix for easy identification")

            return saved_count == len(cleaned_datasets)

        except Exception as e:
            print(f"❌ Failed to save to Google Sheets: {e}")
            return False

# Convenience functions for easy integration

def enhanced_clean_and_save(datasets: Dict[str, pd.DataFrame], use_gx: bool = True, save_to_sheets: bool = True) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """
    One-function replacement for the existing clean-and-save workflow.

    This is designed to be a drop-in replacement for the existing notebook workflow.

    Args:
        datasets: Dictionary of DataFrames to clean
        use_gx: Whether to use Great Expectations cleaning (True) or manual fallback (False)
        save_to_sheets: Whether to save results to Google Sheets (True) or skip saving (False)
    """
    # Initialize pipeline manager
    pipeline = GXPipelineManager(use_gx=use_gx, fallback_to_manual=True)

    # Clean datasets
    cleaned_datasets, cleaning_report = pipeline.clean_datasets_enhanced(datasets)

    # Save to Google Sheets if requested
    if save_to_sheets:
        suffix = "_GX_Cleaned" if use_gx else "_Manual_Cleaned"
        save_success = pipeline.save_cleaned_data_to_sheets(cleaned_datasets, suffix)
        cleaning_report['save_success'] = save_success
        cleaning_report['worksheet_suffix'] = suffix
    else:
        cleaning_report['save_success'] = 'skipped'
        cleaning_report['worksheet_suffix'] = 'not_saved'

    return cleaned_datasets, cleaning_report

def compare_cleaning_methods(datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Compare Great Expectations cleaning vs manual cleaning side-by-side.

    This is useful for validating the GX approach and understanding differences.
    """
    print("🔬 COMPARING CLEANING METHODS")
    print("=" * 50)

    # Run both cleaning approaches
    gx_pipeline = GXPipelineManager(use_gx=True, fallback_to_manual=False)
    manual_pipeline = GXPipelineManager(use_gx=False, fallback_to_manual=False)

    gx_cleaned, gx_report = gx_pipeline.clean_datasets_enhanced(datasets)
    manual_cleaned, manual_report = manual_pipeline.clean_datasets_enhanced(datasets)

    # Compare results
    comparison = {
        'datasets_compared': list(datasets.keys()),
        'gx_results': gx_report,
        'manual_results': manual_report,
        'differences': {}
    }

    for dataset_name in datasets.keys():
        if dataset_name in gx_cleaned and dataset_name in manual_cleaned:
            gx_df = gx_cleaned[dataset_name]
            manual_df = manual_cleaned[dataset_name]

            comparison['differences'][dataset_name] = {
                'shape_difference': {
                    'gx_shape': gx_df.shape,
                    'manual_shape': manual_df.shape,
                    'same_shape': gx_df.shape == manual_df.shape
                },
                'dtype_differences': {
                    'gx_numeric_fields': len(gx_df.select_dtypes(include=['number']).columns),
                    'manual_numeric_fields': len(manual_df.select_dtypes(include=['number']).columns)
                }
            }

    print(f"\n📊 COMPARISON COMPLETE")
    print(f"   Datasets compared: {len(comparison['datasets_compared'])}")

    return comparison

if __name__ == "__main__":
    # Example integration
    print("Great Expectations Pipeline Integration")
    print("=" * 50)
    print("This module provides drop-in replacement functions for existing data cleaning workflow.")
    print("\nKey functions:")
    print("  - enhanced_clean_and_save(): Replaces existing clean-and-save workflow")
    print("  - compare_cleaning_methods(): Compare GX vs manual cleaning")
    print("  - GXPipelineManager: Full pipeline management class")
