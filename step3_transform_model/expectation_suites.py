"""
Pre-built Great Expectations Suites for Chicago SMB Market Radar

This module contains pre-configured expectation suites for each dataset,
eliminating the need to generate them dynamically every time. These suites
embody the business knowledge and data quality requirements specific to
Chicago's SMB data.

Each suite is crafted based on:
- Chicago-specific business rules
- Geographic constraints
- Regulatory requirements
- Data quality patterns observed in the datasets
"""

from typing import Dict, List, Any, Optional
import great_expectations as gx
from great_expectations.core import ExpectationSuite
from great_expectations.expectations.expectation_configuration import ExpectationConfiguration
from datetime import datetime, timedelta

class ChicagoSMBExpectationSuites:
    """Pre-built expectation suites for Chicago SMB datasets."""

    @staticmethod
    def create_business_licenses_suite() -> List[Dict[str, Any]]:
        """Create comprehensive expectations for Business Licenses dataset."""
        return [
            # Table-level expectations
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {
                    "min_value": 100,  # Should have substantial data
                    "max_value": 50000  # Reasonable upper bound
                },
                "meta": {
                    "notes": "Business licenses should have substantial records for meaningful analysis"
                }
            },

            # Core identifier expectations
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "id"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "id"},
                "meta": {"notes": "Primary key must be unique"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "id"},
                "meta": {"criticality": "critical"}
            },

            # Business information expectations
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "legal_name"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "legal_name"},
                "meta": {"notes": "Every business must have a legal name"}
            },
            {
                "expectation_type": "expect_column_value_lengths_to_be_between",
                "kwargs": {"column": "legal_name", "min_value": 2, "max_value": 200},
                "meta": {"notes": "Reasonable business name length"}
            },

            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "license_description"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "license_description"},
                "meta": {"notes": "License type is essential for analysis"}
            },

            # Geographic expectations - Critical for Chicago SMB analysis
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "community_area"},
                "meta": {"criticality": "critical", "chicago_specific": True}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "community_area", "min_value": 1, "max_value": 77},
                "meta": {"notes": "Chicago has exactly 77 community areas", "chicago_specific": True}
            },

            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "community_area_name"},
                "meta": {"criticality": "critical", "chicago_specific": True}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "community_area_name"},
                "meta": {"notes": "Community area names essential for geographic analysis"}
            },

            # Chicago geographic coordinate bounds
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "latitude", "min_value": 41.6, "max_value": 42.1},
                "meta": {"notes": "Chicago latitude bounds", "chicago_specific": True}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "longitude", "min_value": -87.9, "max_value": -87.5},
                "meta": {"notes": "Chicago longitude bounds", "chicago_specific": True}
            },

            # Ward validation (Chicago has 50 wards)
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "ward", "min_value": 1, "max_value": 50},
                "meta": {"notes": "Chicago has 50 wards", "chicago_specific": True}
            },

            # ZIP code expectations
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {"column": "zip_code", "regex": r"^(606|607|608)\d{2}$"},
                "meta": {"notes": "Chicago ZIP codes start with 606, 607, or 608", "chicago_specific": True}
            },

            # Date field expectations
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "license_start_date"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "license_start_date"},
                "meta": {"notes": "Start date is essential for time series analysis"}
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": "license_start_date", "type_": "datetime64"},
                "meta": {"notes": "Must be proper datetime for analysis"}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "license_start_date",
                    "min_value": "2000-01-01",
                    "max_value": datetime.now().strftime("%Y-%m-%d")
                },
                "meta": {"notes": "Reasonable date range for business licenses"}
            },

            # Business rule: start date should be before expiration date
            {
                "expectation_type": "expect_column_pair_values_to_be_in_set",
                "kwargs": {
                    "column_A": "license_start_date",
                    "column_B": "expiration_date",
                    "value_pairs_set": "start_before_expiration"  # Custom validation
                },
                "meta": {"notes": "Business logic: start date must precede expiration"}
            },

            # License status expectations
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "license_status"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "license_status",
                    "value_set": ["ISSUED", "ACTIVE", "EXPIRED", "REVOKED", "SUSPENDED", "CANCELLED"]
                },
                "meta": {"notes": "Standard license status values"}
            },

            # Application type validation
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "application_type"},
                "meta": {"criticality": "high"}
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "application_type",
                    "value_set": ["ISSUE", "RENEW", "C_LOC", "C_EXST"]  # Common types observed
                },
                "meta": {"notes": "Standard application types in Chicago system"}
            },

            # Data quality expectations
            {
                "expectation_type": "expect_column_values_to_not_match_regex",
                "kwargs": {"column": "legal_name", "regex": r"^(test|TEST|dummy|DUMMY)"},
                "meta": {"notes": "Exclude test/dummy records from analysis"}
            },

            # Address validation
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "address"},
                "meta": {"criticality": "high"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "address"},
                "meta": {"notes": "Address required for geographic analysis"}
            },
            {
                "expectation_type": "expect_column_value_lengths_to_be_between",
                "kwargs": {"column": "address", "min_value": 5, "max_value": 200},
                "meta": {"notes": "Reasonable address length"}
            }
        ]

    @staticmethod
    def create_building_permits_suite() -> List[Dict[str, Any]]:
        """Create expectations for Building Permits dataset."""
        return [
            # Table-level expectations
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {"min_value": 50, "max_value": 100000},
                "meta": {"notes": "Building permits dataset size validation"}
            },

            # Core identifiers
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "id"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "id"},
                "meta": {"notes": "Primary key uniqueness"}
            },

            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "permit_"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "permit_"},
                "meta": {"notes": "Permit number is essential"}
            },

            # Permit status validation
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "permit_status"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "permit_status",
                    "value_set": ["PERMIT ISSUED", "PERMIT FINALED", "PERMIT CANCELLED",
                                "REVIEW PENDING", "APPLICATION INCOMPLETE"]
                },
                "meta": {"notes": "Standard permit status values"}
            },

            # Permit type validation
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "permit_type"},
                "meta": {"criticality": "high"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "permit_type"},
                "meta": {"notes": "Permit type essential for categorization"}
            },

            # Date validations
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "issue_date"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": "issue_date", "type_": "datetime64"},
                "meta": {"notes": "Issue date must be datetime for time series"}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "issue_date",
                    "min_value": "1980-01-01",  # Reasonable historical range
                    "max_value": datetime.now().strftime("%Y-%m-%d")
                },
                "meta": {"notes": "Issue dates within reasonable range"}
            },

            # Processing time validation
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "processing_time", "min_value": 0, "max_value": 3650},
                "meta": {"notes": "Processing time in days (0-10 years max)"}
            },

            # Geographic validation (community areas)
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "community_area", "min_value": 1, "max_value": 77},
                "meta": {"notes": "Chicago community areas (1-77)", "chicago_specific": True}
            },

            # Financial field validations - All fees should be non-negative
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "building_fee_paid", "min_value": 0, "max_value": 100000},
                "meta": {"notes": "Building fees should be non-negative and reasonable"}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "zoning_fee_paid", "min_value": 0, "max_value": 50000},
                "meta": {"notes": "Zoning fees should be non-negative"}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "other_fee_paid", "min_value": 0, "max_value": 50000},
                "meta": {"notes": "Other fees should be non-negative"}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "total_fee", "min_value": 0, "max_value": 200000},
                "meta": {"notes": "Total fees should be reasonable and non-negative"}
            },

            # Business rule: total fee should equal sum of component fees
            # (This would require a custom expectation in practice)

            # Work type validation
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "work_type",
                    "value_set": ["EASY PERMIT PROCESS", "PERMIT", "WIRING", "SIGN",
                                "RENOVATION/ALTERATION", "NEW CONSTRUCTION"]
                },
                "meta": {"notes": "Standard work types in Chicago permits"}
            },

            # Street direction validation (Chicago-specific)
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "street_direction",
                    "value_set": ["N", "S", "E", "W", "NE", "NW", "SE", "SW", None]
                },
                "meta": {"notes": "Standard street directions", "chicago_specific": True}
            }
        ]

    @staticmethod
    def create_cta_boardings_suite() -> List[Dict[str, Any]]:
        """Create expectations for CTA Boardings dataset."""
        return [
            # Table-level expectations
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {"min_value": 30, "max_value": 5000},  # ~10 years of daily data
                "meta": {"notes": "CTA data should have substantial daily records"}
            },

            # Service date validation
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "service_date"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "service_date"},
                "meta": {"notes": "Each date should appear once (daily aggregation)"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "service_date"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": "service_date", "type_": "datetime64"},
                "meta": {"notes": "Service date must be datetime"}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "service_date",
                    "min_value": "2010-01-01",  # CTA data availability
                    "max_value": datetime.now().strftime("%Y-%m-%d")
                },
                "meta": {"notes": "CTA data within reasonable historical range"}
            },

            # Total rides validation
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "total_rides"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "total_rides"},
                "meta": {"criticality": "critical"}
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": "total_rides", "type_": "int"},
                "meta": {"notes": "Ride counts should be integers"}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "total_rides",
                    "min_value": 0,  # Could be 0 during shutdowns/holidays
                    "max_value": 2000000  # Peak CTA daily ridership
                },
                "meta": {"notes": "CTA daily ridership within realistic bounds"}
            },

            # Business rules for CTA data
            {
                "expectation_type": "expect_column_mean_to_be_between",
                "kwargs": {"column": "total_rides", "min_value": 200000, "max_value": 800000},
                "meta": {"notes": "Average daily ridership should be within historical norms"}
            },

            # Data quality: no extreme outliers (except during known events)
            {
                "expectation_type": "expect_column_quantile_values_to_be_between",
                "kwargs": {
                    "column": "total_rides",
                    "quantile": 0.99,
                    "min_value": 100000,
                    "max_value": 1500000
                },
                "meta": {"notes": "99th percentile within expected range"}
            }
        ]

    @staticmethod
    def get_all_suites() -> Dict[str, List[Dict[str, Any]]]:
        """Get all pre-built expectation suites."""
        return {
            "business_licenses": ChicagoSMBExpectationSuites.create_business_licenses_suite(),
            "building_permits": ChicagoSMBExpectationSuites.create_building_permits_suite(),
            "cta_boardings": ChicagoSMBExpectationSuites.create_cta_boardings_suite()
        }

    @staticmethod
    def create_gx_suite_from_config(dataset_name: str, context) -> Optional[ExpectationSuite]:
        """Create a Great Expectations suite from the pre-built configuration."""
        suite_configs = ChicagoSMBExpectationSuites.get_all_suites()

        if dataset_name not in suite_configs:
            print(f"❌ No pre-built suite for dataset: {dataset_name}")
            return None

        try:
            # Create expectation suite
            suite_name = f"{dataset_name}_chicago_smb_suite"

            # Delete existing suite if it exists
            try:
                context.delete_expectation_suite(suite_name)
            except:
                pass

            suite = context.create_expectation_suite(suite_name)

            # Add expectations from configuration
            expectations_added = 0
            config_list = suite_configs[dataset_name]

            for expectation_config in config_list:
                expectation_type = expectation_config["expectation_type"]
                kwargs = expectation_config["kwargs"]
                meta = expectation_config.get("meta", {})

                # Create expectation configuration
                exp_config = ExpectationConfiguration(
                    expectation_type=expectation_type,
                    kwargs=kwargs,
                    meta=meta
                )

                # Add to suite
                suite.add_expectation(exp_config)
                expectations_added += 1

            # Save suite
            context.save_expectation_suite(suite)

            print(f"✅ Created {suite_name} with {expectations_added} expectations")
            return suite

        except Exception as e:
            print(f"❌ Failed to create suite for {dataset_name}: {e}")
            return None

# Convenience functions
def create_all_chicago_suites(context) -> Dict[str, ExpectationSuite]:
    """Create all Chicago SMB expectation suites."""
    suites = {}
    dataset_names = ["business_licenses", "building_permits", "cta_boardings"]

    print("🏗️  CREATING CHICAGO SMB EXPECTATION SUITES")
    print("=" * 50)

    for dataset_name in dataset_names:
        suite = ChicagoSMBExpectationSuites.create_gx_suite_from_config(dataset_name, context)
        if suite:
            suites[dataset_name] = suite

    print(f"\n✅ Created {len(suites)}/{len(dataset_names)} expectation suites")
    return suites

def validate_chicago_dataset(df, dataset_name: str, context) -> Dict[str, Any]:
    """Validate a Chicago dataset using pre-built expectations."""
    # Ensure suite exists
    suite = ChicagoSMBExpectationSuites.create_gx_suite_from_config(dataset_name, context)
    if not suite:
        return {"error": f"Could not create suite for {dataset_name}"}

    try:
        # Create validator and run validation
        validator = context.get_validator(
            batch_request=context.sources.add_pandas(dataset_name).add_asset(
                dataset_name
            ).build_batch_request(dataframe=df),
            expectation_suite_name=suite.expectation_suite_name
        )

        results = validator.validate()

        return {
            "dataset_name": dataset_name,
            "validation_success": results.success,
            "expectations_met": results.statistics["successful_expectations"],
            "total_expectations": results.statistics["evaluated_expectations"],
            "success_rate": results.statistics["successful_expectations"] / results.statistics["evaluated_expectations"],
            "results": results
        }

    except Exception as e:
        return {"error": f"Validation failed for {dataset_name}: {e}"}

if __name__ == "__main__":
    # Example usage
    print("Chicago SMB Market Radar - Pre-built Expectation Suites")
    print("=" * 60)

    suites = ChicagoSMBExpectationSuites.get_all_suites()

    for dataset_name, suite_config in suites.items():
        print(f"\n{dataset_name.upper().replace('_', ' ')} SUITE:")
        print(f"  Expectations: {len(suite_config)}")

        # Count by criticality
        critical = sum(1 for exp in suite_config if exp.get("meta", {}).get("criticality") == "critical")
        chicago_specific = sum(1 for exp in suite_config if exp.get("meta", {}).get("chicago_specific", False))

        print(f"  Critical: {critical}")
        print(f"  Chicago-specific: {chicago_specific}")
