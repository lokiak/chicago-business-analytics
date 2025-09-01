"""
Chicago SMB Market Radar - Data Schema Definitions

This module defines the schema for all datasets used in the Chicago SMB Market Radar project.
It provides a centralized source of truth for field definitions, data types, and validation rules.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DataType(Enum):
    """Data type enumeration for schema validation."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    GEOJSON = "geojson"

@dataclass
class FieldDefinition:
    """Definition of a single field in a dataset."""
    name: str
    data_type: DataType
    description: str
    required: bool = True
    nullable: bool = False
    validation_rules: Optional[Dict[str, Any]] = None

@dataclass
class DatasetSchema:
    """Complete schema definition for a dataset."""
    name: str
    description: str
    fields: List[FieldDefinition]
    primary_key: Optional[str] = None
    date_field: Optional[str] = None
    area_field: Optional[str] = None
    area_name_field: Optional[str] = None

class ChicagoDataSchemas:
    """Centralized schema definitions for all Chicago datasets."""

    # Business Licenses Schema
    BUSINESS_LICENSES = DatasetSchema(
        name="business_licenses",
        description="Chicago Business Licenses dataset",
        primary_key="id",
        date_field="license_start_date",
        area_field="community_area",
        area_name_field="community_area_name",
        fields=[
            # Core identifiers
            FieldDefinition("id", DataType.STRING, "Unique record identifier", True),
            FieldDefinition("license_id", DataType.STRING, "License ID number", True),
            FieldDefinition("account_number", DataType.STRING, "Account number", False),
            FieldDefinition("site_number", DataType.STRING, "Site number", False),

            # Business information
            FieldDefinition("legal_name", DataType.STRING, "Legal business name", True),
            FieldDefinition("doing_business_as_name", DataType.STRING, "DBA name", False),
            FieldDefinition("license_code", DataType.STRING, "License code", False),
            FieldDefinition("license_number", DataType.STRING, "License number", False),
            FieldDefinition("license_description", DataType.STRING, "License description", True),
            FieldDefinition("business_activity_id", DataType.STRING, "Business activity ID", False),
            FieldDefinition("business_activity", DataType.STRING, "Business activity description", False),

            # Location information
            FieldDefinition("address", DataType.STRING, "Business address", True),
            FieldDefinition("city", DataType.STRING, "City", True),
            FieldDefinition("state", DataType.STRING, "State", True),
            FieldDefinition("zip_code", DataType.STRING, "ZIP code", False),
            FieldDefinition("ward", DataType.INTEGER, "Ward number", False),
            FieldDefinition("precinct", DataType.INTEGER, "Precinct number", False),
            FieldDefinition("ward_precinct", DataType.STRING, "Ward-precinct combination", False),
            FieldDefinition("police_district", DataType.INTEGER, "Police district", False),
            FieldDefinition("community_area", DataType.INTEGER, "Community area number", True),
            FieldDefinition("community_area_name", DataType.STRING, "Community area name", True),
            FieldDefinition("neighborhood", DataType.STRING, "Neighborhood name", False),
            FieldDefinition("ssa", DataType.STRING, "Special Service Area", False),

            # Geographic coordinates
            FieldDefinition("latitude", DataType.FLOAT, "Latitude coordinate", False),
            FieldDefinition("longitude", DataType.FLOAT, "Longitude coordinate", False),

            # Flattened location data (processed from original 'location' field)
            FieldDefinition("location_latitude", DataType.FLOAT, "Latitude from flattened location", False),
            FieldDefinition("location_longitude", DataType.FLOAT, "Longitude from flattened location", False),
            FieldDefinition("location_human_address", DataType.STRING, "Human readable address from location", False),

            # Application and processing
            FieldDefinition("application_type", DataType.STRING, "Type of application", True),
            FieldDefinition("application_created_date", DataType.DATE, "Application creation date", False),
            FieldDefinition("application_requirements_complete", DataType.DATE, "Requirements completion date", False),
            FieldDefinition("payment_date", DataType.DATE, "Payment date", False),
            FieldDefinition("conditional_approval", DataType.DATE, "Conditional approval date", False),
            FieldDefinition("license_approved_for_issuance", DataType.DATE, "License approval date", False),
            FieldDefinition("date_issued", DataType.DATE, "License issue date", False),

            # License status and dates
            FieldDefinition("license_start_date", DataType.DATE, "License start date", True),
            FieldDefinition("expiration_date", DataType.DATE, "License expiration date", False),
            FieldDefinition("license_status", DataType.STRING, "Current license status", True),
            FieldDefinition("license_status_change_date", DataType.DATE, "Status change date", False),
        ]
    )

    # Building Permits Schema
    BUILDING_PERMITS = DatasetSchema(
        name="building_permits",
        description="Chicago Building Permits dataset",
        primary_key="id",
        date_field="issue_date",
        area_field="community_area",
        fields=[
            # Core identifiers
            FieldDefinition("id", DataType.STRING, "Unique record identifier", True),
            FieldDefinition("permit_", DataType.STRING, "Permit number", True),

            # Permit information
            FieldDefinition("permit_status", DataType.STRING, "Current permit status", True),
            FieldDefinition("permit_milestone", DataType.STRING, "Current milestone", False),
            FieldDefinition("permit_type", DataType.STRING, "Type of permit", True),
            FieldDefinition("review_type", DataType.STRING, "Review type", False),

            # Dates
            FieldDefinition("application_start_date", DataType.DATE, "Application start date", False),
            FieldDefinition("issue_date", DataType.DATE, "Permit issue date", True),
            FieldDefinition("processing_time", DataType.INTEGER, "Processing time in days", False),

            # Location information
            FieldDefinition("street_number", DataType.STRING, "Street number", False),
            FieldDefinition("street_direction", DataType.STRING, "Street direction", False),
            FieldDefinition("street_name", DataType.STRING, "Street name", False),
            FieldDefinition("community_area", DataType.INTEGER, "Community area number", False),

            # Work information
            FieldDefinition("work_type", DataType.STRING, "Type of work", False),
            FieldDefinition("work_description", DataType.STRING, "Work description", False),

            # Financial information
            FieldDefinition("building_fee_paid", DataType.FLOAT, "Building fee paid", False),
            FieldDefinition("zoning_fee_paid", DataType.FLOAT, "Zoning fee paid", False),
            FieldDefinition("other_fee_paid", DataType.FLOAT, "Other fees paid", False),
            FieldDefinition("subtotal_paid", DataType.FLOAT, "Subtotal paid", False),
            FieldDefinition("building_fee_unpaid", DataType.FLOAT, "Building fee unpaid", False),
            FieldDefinition("zoning_fee_unpaid", DataType.FLOAT, "Zoning fee unpaid", False),
            FieldDefinition("other_fee_unpaid", DataType.FLOAT, "Other fees unpaid", False),
            FieldDefinition("subtotal_unpaid", DataType.FLOAT, "Subtotal unpaid", False),
            FieldDefinition("building_fee_waived", DataType.FLOAT, "Building fee waived", False),
            FieldDefinition("building_fee_subtotal", DataType.FLOAT, "Building fee subtotal", False),
            FieldDefinition("zoning_fee_subtotal", DataType.FLOAT, "Zoning fee subtotal", False),
            FieldDefinition("other_fee_subtotal", DataType.FLOAT, "Other fee subtotal", False),
            FieldDefinition("zoning_fee_waived", DataType.FLOAT, "Zoning fee waived", False),
            FieldDefinition("other_fee_waived", DataType.FLOAT, "Other fee waived", False),
            FieldDefinition("subtotal_waived", DataType.FLOAT, "Subtotal waived", False),
            FieldDefinition("total_fee", DataType.FLOAT, "Total fee amount", False),
        ]
    )

    # CTA Boardings Schema
    CTA_BOARDINGS = DatasetSchema(
        name="cta_boardings",
        description="Chicago Transit Authority Daily Boarding Totals",
        primary_key="service_date",
        date_field="service_date",
        fields=[
            FieldDefinition("service_date", DataType.DATE, "Service date", True),
            FieldDefinition("total_rides", DataType.INTEGER, "Total daily rides", True),
        ]
    )

class SchemaManager:
    """Manager class for schema operations and validation."""

    @staticmethod
    def get_schema(dataset_name: str) -> DatasetSchema:
        """Get schema for a specific dataset."""
        schemas = {
            "business_licenses": ChicagoDataSchemas.BUSINESS_LICENSES,
            "building_permits": ChicagoDataSchemas.BUILDING_PERMITS,
            "cta_boardings": ChicagoDataSchemas.CTA_BOARDINGS,
        }

        if dataset_name not in schemas:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        return schemas[dataset_name]

    @staticmethod
    def get_field_names(dataset_name: str, field_types: Optional[List[DataType]] = None) -> List[str]:
        """Get field names for a dataset, optionally filtered by type."""
        schema = SchemaManager.get_schema(dataset_name)

        if field_types is None:
            return [field.name for field in schema.fields]

        return [field.name for field in schema.fields if field.data_type in field_types]

    @staticmethod
    def get_required_fields(dataset_name: str) -> List[str]:
        """Get required field names for a dataset."""
        schema = SchemaManager.get_schema(dataset_name)
        return [field.name for field in schema.fields if field.required]

    @staticmethod
    def get_date_fields(dataset_name: str) -> List[str]:
        """Get date field names for a dataset."""
        return SchemaManager.get_field_names(dataset_name, [DataType.DATE, DataType.DATETIME])

    @staticmethod
    def get_geographic_fields(dataset_name: str) -> List[str]:
        """Get geographic field names for a dataset."""
        geographic_types = [DataType.FLOAT, DataType.GEOJSON, DataType.STRING]
        return [field.name for field in SchemaManager.get_schema(dataset_name).fields
                if field.data_type in geographic_types and
                any(geo_term in field.name.lower() for geo_term in ['lat', 'lon', 'location', 'area', 'ward', 'precinct', 'address'])]

    @staticmethod
    def get_business_fields(dataset_name: str) -> List[str]:
        """Get business-related field names for a dataset."""
        business_terms = ['license', 'business', 'permit', 'activity', 'description']
        schema = SchemaManager.get_schema(dataset_name)
        return [field.name for field in schema.fields
                if any(term in field.name.lower() for term in business_terms)]

    @staticmethod
    def get_query_fields(dataset_name: str, include_all: bool = True) -> List[str]:
        """Get fields to include in API queries."""
        schema = SchemaManager.get_schema(dataset_name)

        if include_all:
            return [field.name for field in schema.fields]

        # Return essential fields for basic queries
        essential_fields = []
        for field in schema.fields:
            if (field.required or
                field.name in [schema.primary_key, schema.date_field, schema.area_field, schema.area_name_field] or
                field.data_type in [DataType.DATE, DataType.DATETIME]):
                essential_fields.append(field.name)

        return essential_fields

    @staticmethod
    def validate_field_exists(dataset_name: str, field_name: str) -> bool:
        """Validate that a field exists in the dataset schema."""
        schema = SchemaManager.get_schema(dataset_name)
        return any(field.name == field_name for field in schema.fields)

    @staticmethod
    def get_field_definition(dataset_name: str, field_name: str) -> Optional[FieldDefinition]:
        """Get field definition for a specific field."""
        schema = SchemaManager.get_schema(dataset_name)
        for field in schema.fields:
            if field.name == field_name:
                return field
        return None

# Convenience functions for common operations
def get_business_licenses_fields() -> List[str]:
    """Get all business licenses field names."""
    return SchemaManager.get_field_names("business_licenses")

def get_building_permits_fields() -> List[str]:
    """Get all building permits field names."""
    return SchemaManager.get_field_names("building_permits")

def get_cta_boardings_fields() -> List[str]:
    """Get all CTA boardings field names."""
    return SchemaManager.get_field_names("cta_boardings")

def get_required_business_licenses_fields() -> List[str]:
    """Get required business licenses field names."""
    return SchemaManager.get_required_fields("business_licenses")

def get_date_fields_for_dataset(dataset_name: str) -> List[str]:
    """Get date fields for a specific dataset."""
    return SchemaManager.get_date_fields(dataset_name)

def get_geographic_fields_for_dataset(dataset_name: str) -> List[str]:
    """Get geographic fields for a specific dataset."""
    return SchemaManager.get_geographic_fields(dataset_name)
