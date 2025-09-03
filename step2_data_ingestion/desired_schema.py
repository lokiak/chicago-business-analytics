"""
Chicago SMB Market Radar - Desired Schema Definitions

This module defines the DESIRED/TARGET schema for all datasets after cleaning and transformation.
It mirrors the structure of the original schema.py but with improved datatypes and validation rules
optimized for analysis and Great Expectations validation.

Key improvements:
- More precise numeric types (Int64 vs float64)
- Currency/monetary fields properly typed
- Enhanced validation patterns
- Analysis-ready field configurations
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import re

class DesiredDataType(Enum):
    """Enhanced data type enumeration for desired schema validation."""
    STRING = "string"
    INTEGER = "Int64"           # Pandas nullable integer
    FLOAT = "float64"
    CURRENCY = "currency"       # Special monetary type
    PERCENTAGE = "percentage"   # Special percentage type
    DATE = "datetime64[ns]"
    BOOLEAN = "bool"
    CATEGORY = "category"       # For categorical data
    GEOJSON = "geojson"
    ZIPCODE = "zipcode"         # Special zipcode handling
    PHONE = "phone"             # Phone number format
    EMAIL = "email"             # Email format

@dataclass
class FieldPattern:
    """Pattern-based field type detection rules."""
    keywords: List[str] = field(default_factory=list)
    regex_pattern: Optional[str] = None
    target_type: DesiredDataType = DesiredDataType.STRING
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    transformation_rules: List[str] = field(default_factory=list)

@dataclass
class DesiredFieldDefinition:
    """Enhanced field definition for desired schema."""
    name: str
    desired_type: DesiredDataType
    description: str
    required: bool = True
    nullable: bool = False
    validation_rules: Optional[Dict[str, Any]] = None
    business_rules: Optional[List[str]] = None
    transformation_notes: Optional[str] = None
    analysis_priority: str = "medium"  # low, medium, high, critical

@dataclass
class DesiredDatasetSchema:
    """Complete desired schema definition for a dataset."""
    name: str
    description: str
    fields: List[DesiredFieldDefinition]
    primary_key: Optional[str] = None
    date_field: Optional[str] = None
    area_field: Optional[str] = None
    area_name_field: Optional[str] = None
    business_rules: Optional[List[str]] = None
    quality_thresholds: Optional[Dict[str, float]] = None

class FieldTypeDetector:
    """Pattern-based field type detection system."""

    DETECTION_PATTERNS = [
        # Monetary/Currency fields
        FieldPattern(
            keywords=["fee", "paid", "cost", "price", "amount", "total", "subtotal"],
            target_type=DesiredDataType.CURRENCY,
            validation_rules={"min_value": 0, "max_value": 1000000},
            transformation_rules=["remove_currency_symbols", "convert_to_float"]
        ),

        # Geographic coordinates
        FieldPattern(
            keywords=["latitude", "lat"],
            target_type=DesiredDataType.FLOAT,
            validation_rules={"min_value": -90, "max_value": 90},
            transformation_rules=["ensure_decimal_precision"]
        ),
        FieldPattern(
            keywords=["longitude", "lon", "lng"],
            target_type=DesiredDataType.FLOAT,
            validation_rules={"min_value": -180, "max_value": 180},
            transformation_rules=["ensure_decimal_precision"]
        ),

        # Administrative areas and codes
        FieldPattern(
            keywords=["community_area", "ward", "precinct", "district"],
            target_type=DesiredDataType.INTEGER,
            validation_rules={"min_value": 0, "max_value": 200},
            transformation_rules=["convert_to_integer", "handle_nulls_as_unknown"]
        ),

        # ZIP codes
        FieldPattern(
            keywords=["zip", "postal"],
            target_type=DesiredDataType.ZIPCODE,
            validation_rules={"pattern": r"^\d{5}(-\d{4})?$"},
            transformation_rules=["standardize_zip_format", "handle_invalid_zips"]
        ),

        # Date fields
        FieldPattern(
            keywords=["date", "created", "issued", "start", "end", "expiration"],
            target_type=DesiredDataType.DATE,
            validation_rules={"not_future": True, "not_before_1900": True},
            transformation_rules=["parse_flexible_dates", "handle_null_dates"]
        ),

        # Status/Category fields
        FieldPattern(
            keywords=["status", "type", "category", "description"],
            target_type=DesiredDataType.CATEGORY,
            validation_rules={"allowed_values": "detect_from_data"},
            transformation_rules=["standardize_categories", "handle_unknown_categories"]
        ),

        # Identifiers
        FieldPattern(
            keywords=["id", "number", "account"],
            target_type=DesiredDataType.STRING,
            validation_rules={"not_null": True, "unique": "preferred"},
            transformation_rules=["trim_whitespace", "standardize_format"]
        )
    ]

    @classmethod
    def detect_field_type(cls, field_name: str, sample_data: Any = None) -> DesiredDataType:
        """Detect desired field type based on name patterns and sample data."""
        field_lower = field_name.lower()

        for pattern in cls.DETECTION_PATTERNS:
            if any(keyword in field_lower for keyword in pattern.keywords):
                return pattern.target_type

        # Default fallback
        return DesiredDataType.STRING

class ChicagoDesiredSchemas:
    """Desired schema definitions optimized for analysis."""

    # Business Licenses Desired Schema
    BUSINESS_LICENSES = DesiredDatasetSchema(
        name="business_licenses",
        description="Chicago Business Licenses - Analysis Ready",
        primary_key="id",
        date_field="license_start_date",
        area_field="community_area",
        area_name_field="community_area_name",
        quality_thresholds={
            "completeness_required": 0.95,
            "completeness_optional": 0.10,
            "validity_rate": 0.90
        },
        business_rules=[
            "license_start_date <= expiration_date",
            "community_area between 1 and 77",
            "latitude between 41.6 and 42.1",
            "longitude between -87.9 and -87.5"
        ],
        fields=[
            # Core identifiers
            DesiredFieldDefinition("id", DesiredDataType.STRING, "Unique record identifier", True, analysis_priority="critical"),
            DesiredFieldDefinition("license_id", DesiredDataType.STRING, "License ID number", True, analysis_priority="high"),
            DesiredFieldDefinition("account_number", DesiredDataType.STRING, "Account number", False, analysis_priority="low"),
            DesiredFieldDefinition("site_number", DesiredDataType.CATEGORY, "Site number (categorized)", False, analysis_priority="low"),

            # Business information
            DesiredFieldDefinition("legal_name", DesiredDataType.STRING, "Legal business name", True, analysis_priority="high"),
            DesiredFieldDefinition("doing_business_as_name", DesiredDataType.STRING, "DBA name", False, analysis_priority="medium"),
            DesiredFieldDefinition("license_code", DesiredDataType.CATEGORY, "License code (categorized)", False, analysis_priority="high"),
            DesiredFieldDefinition("license_number", DesiredDataType.STRING, "License number", False, analysis_priority="medium"),
            DesiredFieldDefinition("license_description", DesiredDataType.CATEGORY, "License description (categorized)", True, analysis_priority="critical"),
            DesiredFieldDefinition("business_activity_id", DesiredDataType.STRING, "Business activity ID", False, analysis_priority="medium"),
            DesiredFieldDefinition("business_activity", DesiredDataType.CATEGORY, "Business activity (categorized)", False, analysis_priority="high"),

            # Location information - CRITICAL for analysis
            DesiredFieldDefinition("address", DesiredDataType.STRING, "Business address", True, analysis_priority="high"),
            DesiredFieldDefinition("city", DesiredDataType.CATEGORY, "City (should be Chicago)", True, analysis_priority="medium"),
            DesiredFieldDefinition("state", DesiredDataType.CATEGORY, "State (should be IL)", True, analysis_priority="low"),
            DesiredFieldDefinition("zip_code", DesiredDataType.ZIPCODE, "ZIP code (5-digit format)", False, analysis_priority="medium"),
            DesiredFieldDefinition("ward", DesiredDataType.INTEGER, "Ward number (1-50)", False, analysis_priority="high"),
            DesiredFieldDefinition("precinct", DesiredDataType.INTEGER, "Precinct number", False, analysis_priority="low"),
            DesiredFieldDefinition("police_district", DesiredDataType.INTEGER, "Police district", False, analysis_priority="medium"),
            DesiredFieldDefinition("community_area", DesiredDataType.INTEGER, "Community area number (1-77)", True, analysis_priority="critical"),
            DesiredFieldDefinition("community_area_name", DesiredDataType.CATEGORY, "Community area name", True, analysis_priority="critical"),
            DesiredFieldDefinition("neighborhood", DesiredDataType.CATEGORY, "Neighborhood name", False, analysis_priority="medium"),

            # Geographic coordinates - CRITICAL for mapping
            DesiredFieldDefinition("latitude", DesiredDataType.FLOAT, "Latitude coordinate (Chicago bounds)", False,
                                 validation_rules={"min_value": 41.6, "max_value": 42.1}, analysis_priority="high"),
            DesiredFieldDefinition("longitude", DesiredDataType.FLOAT, "Longitude coordinate (Chicago bounds)", False,
                                 validation_rules={"min_value": -87.9, "max_value": -87.5}, analysis_priority="high"),

            # Processed location data (from flattened 'location' field)
            DesiredFieldDefinition("location_latitude", DesiredDataType.FLOAT, "Latitude from processed location", False, analysis_priority="medium"),
            DesiredFieldDefinition("location_longitude", DesiredDataType.FLOAT, "Longitude from processed location", False, analysis_priority="medium"),
            DesiredFieldDefinition("location_human_address", DesiredDataType.STRING, "Human readable address", False, analysis_priority="low"),

            # Application workflow - IMPORTANT for timeline analysis
            DesiredFieldDefinition("application_type", DesiredDataType.CATEGORY, "Type of application", True, analysis_priority="high"),
            DesiredFieldDefinition("application_created_date", DesiredDataType.DATE, "Application creation date", False, analysis_priority="high"),
            DesiredFieldDefinition("application_requirements_complete", DesiredDataType.DATE, "Requirements completion date", False, analysis_priority="medium"),
            DesiredFieldDefinition("payment_date", DesiredDataType.DATE, "Payment date", False, analysis_priority="medium"),
            DesiredFieldDefinition("license_approved_for_issuance", DesiredDataType.DATE, "License approval date", False, analysis_priority="medium"),
            DesiredFieldDefinition("date_issued", DesiredDataType.DATE, "License issue date", False, analysis_priority="high"),

            # License lifecycle - CRITICAL for trend analysis
            DesiredFieldDefinition("license_start_date", DesiredDataType.DATE, "License start date", True, analysis_priority="critical"),
            DesiredFieldDefinition("expiration_date", DesiredDataType.DATE, "License expiration date", False, analysis_priority="high"),
            DesiredFieldDefinition("license_status", DesiredDataType.CATEGORY, "Current license status", True, analysis_priority="critical"),

            # Additional fields for improved success rate
            DesiredFieldDefinition("conditional_approval", DesiredDataType.BOOLEAN, "Conditional approval flag (Y/N)", False, analysis_priority="medium"),
            DesiredFieldDefinition("ward_precinct", DesiredDataType.CATEGORY, "Ward-Precinct combination", False, analysis_priority="low"),
            DesiredFieldDefinition("ssa", DesiredDataType.INTEGER, "Special Service Area number", False, analysis_priority="low"),
            DesiredFieldDefinition("license_status_change_date", DesiredDataType.DATE, "Status change date", False, analysis_priority="low"),
        ]
    )

    # Building Permits Desired Schema
    BUILDING_PERMITS = DesiredDatasetSchema(
        name="building_permits",
        description="Chicago Building Permits - Analysis Ready",
        primary_key="id",
        date_field="issue_date",
        area_field="community_area",
        quality_thresholds={
            "completeness_required": 0.95,
            "completeness_optional": 0.05,
            "validity_rate": 0.85
        },
        business_rules=[
            "issue_date >= application_start_date",
            "total_fee >= 0",
            "processing_time >= 0"
        ],
        fields=[
            # Core identifiers
            DesiredFieldDefinition("id", DesiredDataType.STRING, "Unique record identifier", True, analysis_priority="critical"),
            DesiredFieldDefinition("permit_", DesiredDataType.STRING, "Permit number", True, analysis_priority="high"),

            # Permit information
            DesiredFieldDefinition("permit_status", DesiredDataType.CATEGORY, "Current permit status", True, analysis_priority="critical"),
            DesiredFieldDefinition("permit_milestone", DesiredDataType.CATEGORY, "Current milestone", False, analysis_priority="medium"),
            DesiredFieldDefinition("permit_type", DesiredDataType.CATEGORY, "Type of permit", True, analysis_priority="high"),
            DesiredFieldDefinition("review_type", DesiredDataType.CATEGORY, "Review type", False, analysis_priority="medium"),

            # Dates - CRITICAL for timeline analysis
            DesiredFieldDefinition("application_start_date", DesiredDataType.DATE, "Application start date", False, analysis_priority="high"),
            DesiredFieldDefinition("issue_date", DesiredDataType.DATE, "Permit issue date", True, analysis_priority="critical"),
            DesiredFieldDefinition("processing_time", DesiredDataType.INTEGER, "Processing time in days", False,
                                 validation_rules={"min_value": 0, "max_value": 3650}, analysis_priority="high"),

            # Location information
            DesiredFieldDefinition("street_number", DesiredDataType.STRING, "Street number", False, analysis_priority="medium"),
            DesiredFieldDefinition("street_direction", DesiredDataType.CATEGORY, "Street direction", False, analysis_priority="low"),
            DesiredFieldDefinition("street_name", DesiredDataType.STRING, "Street name", False, analysis_priority="medium"),
            DesiredFieldDefinition("community_area", DesiredDataType.INTEGER, "Community area number", False, analysis_priority="high"),

            # Work information
            DesiredFieldDefinition("work_type", DesiredDataType.CATEGORY, "Type of work", False, analysis_priority="high"),
            DesiredFieldDefinition("work_description", DesiredDataType.STRING, "Work description", False, analysis_priority="medium"),

            # Financial information - All CURRENCY type for proper analysis
            DesiredFieldDefinition("building_fee_paid", DesiredDataType.CURRENCY, "Building fee paid", False, analysis_priority="medium"),
            DesiredFieldDefinition("zoning_fee_paid", DesiredDataType.CURRENCY, "Zoning fee paid", False, analysis_priority="low"),
            DesiredFieldDefinition("other_fee_paid", DesiredDataType.CURRENCY, "Other fees paid", False, analysis_priority="low"),
            DesiredFieldDefinition("subtotal_paid", DesiredDataType.CURRENCY, "Subtotal paid", False, analysis_priority="medium"),
            DesiredFieldDefinition("building_fee_unpaid", DesiredDataType.CURRENCY, "Building fee unpaid", False, analysis_priority="low"),
            DesiredFieldDefinition("zoning_fee_unpaid", DesiredDataType.CURRENCY, "Zoning fee unpaid", False, analysis_priority="low"),
            DesiredFieldDefinition("other_fee_unpaid", DesiredDataType.CURRENCY, "Other fees unpaid", False, analysis_priority="low"),
            DesiredFieldDefinition("subtotal_unpaid", DesiredDataType.CURRENCY, "Subtotal unpaid", False, analysis_priority="medium"),
            DesiredFieldDefinition("building_fee_waived", DesiredDataType.CURRENCY, "Building fee waived", False, analysis_priority="low"),
            DesiredFieldDefinition("zoning_fee_waived", DesiredDataType.CURRENCY, "Zoning fee waived", False, analysis_priority="low"),
            DesiredFieldDefinition("other_fee_waived", DesiredDataType.CURRENCY, "Other fee waived", False, analysis_priority="low"),
            DesiredFieldDefinition("subtotal_waived", DesiredDataType.CURRENCY, "Subtotal waived", False, analysis_priority="low"),
            DesiredFieldDefinition("total_fee", DesiredDataType.CURRENCY, "Total fee amount", False, analysis_priority="high"),
        ]
    )

    # CTA Boardings Desired Schema
    CTA_BOARDINGS = DesiredDatasetSchema(
        name="cta_boardings",
        description="Chicago Transit Authority Daily Boarding Totals - Analysis Ready",
        primary_key="service_date",
        date_field="service_date",
        quality_thresholds={
            "completeness_required": 1.0,  # All fields required
            "validity_rate": 0.95
        },
        business_rules=[
            "total_rides >= 0",
            "service_date not in future"
        ],
        fields=[
            DesiredFieldDefinition("service_date", DesiredDataType.DATE, "Service date", True, analysis_priority="critical"),
            DesiredFieldDefinition("total_rides", DesiredDataType.INTEGER, "Total daily rides", True,
                                 validation_rules={"min_value": 0, "max_value": 2000000}, analysis_priority="critical"),
        ]
    )

class DesiredSchemaManager:
    """Manager for desired schema operations and validation."""

    @staticmethod
    def get_desired_schema(dataset_name: str) -> DesiredDatasetSchema:
        """Get desired schema for a specific dataset."""
        schemas = {
            "business_licenses": ChicagoDesiredSchemas.BUSINESS_LICENSES,
            "building_permits": ChicagoDesiredSchemas.BUILDING_PERMITS,
            "cta_boardings": ChicagoDesiredSchemas.CTA_BOARDINGS,
        }

        if dataset_name not in schemas:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        return schemas[dataset_name]

    @staticmethod
    def get_critical_fields(dataset_name: str) -> List[str]:
        """Get critical analysis fields for a dataset."""
        schema = DesiredSchemaManager.get_desired_schema(dataset_name)
        return [field.name for field in schema.fields if field.analysis_priority == "critical"]

    @staticmethod
    def get_currency_fields(dataset_name: str) -> List[str]:
        """Get currency/monetary fields for a dataset."""
        schema = DesiredSchemaManager.get_desired_schema(dataset_name)
        return [field.name for field in schema.fields if field.desired_type == DesiredDataType.CURRENCY]

    @staticmethod
    def get_category_fields(dataset_name: str) -> List[str]:
        """Get categorical fields for a dataset."""
        schema = DesiredSchemaManager.get_desired_schema(dataset_name)
        return [field.name for field in schema.fields if field.desired_type == DesiredDataType.CATEGORY]

    @staticmethod
    def get_business_rules(dataset_name: str) -> List[str]:
        """Get business validation rules for a dataset."""
        schema = DesiredSchemaManager.get_desired_schema(dataset_name)
        return schema.business_rules or []

    @staticmethod
    def generate_transformation_plan(dataset_name: str, current_dtypes: Dict[str, str]) -> Dict[str, Dict]:
        """Generate a transformation plan comparing current vs desired types."""
        schema = DesiredSchemaManager.get_desired_schema(dataset_name)
        transformation_plan = {}

        for field in schema.fields:
            if field.name in current_dtypes:
                current_type = current_dtypes[field.name]
                desired_type = field.desired_type.value

                if current_type != desired_type:
                    transformation_plan[field.name] = {
                        'current_type': current_type,
                        'desired_type': desired_type,
                        'validation_rules': field.validation_rules,
                        'priority': field.analysis_priority
                    }

        return transformation_plan

# Convenience functions for common operations
def get_desired_business_licenses_fields() -> List[str]:
    """Get all desired business licenses field names."""
    return [field.name for field in ChicagoDesiredSchemas.BUSINESS_LICENSES.fields]

def get_desired_currency_fields(dataset_name: str) -> List[str]:
    """Get desired currency fields for analysis."""
    return DesiredSchemaManager.get_currency_fields(dataset_name)

def get_transformation_priority_fields(dataset_name: str) -> Dict[str, List[str]]:
    """Get fields grouped by transformation priority."""
    schema = DesiredSchemaManager.get_desired_schema(dataset_name)
    priority_fields = {"critical": [], "high": [], "medium": [], "low": []}

    for field in schema.fields:
        priority_fields[field.analysis_priority].append(field.name)

    return priority_fields
