#!/usr/bin/env python3
"""
Schema Documentation Script
Fetches complete schema information for all datasets and writes to Google Sheets
"""

import requests
import yaml
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import os

# Add src to path to import modules
sys.path.append(str(Path(__file__).parent / "src"))

from sheets import open_sheet, upsert_worksheet, overwrite_with_dataframe
from config import load_settings, load_datasets_yaml
from logging_setup import setup_logger

logger = setup_logger()

def get_dataset_metadata(domain, dataset_id):
    """Get comprehensive metadata for a dataset including field definitions"""

    base_url = f"https://{domain}/resource/{dataset_id}.json"

    # Get field metadata from SODA2 headers
    try:
        r = requests.get(base_url, params={"$limit": 1}, timeout=30)
        if r.status_code == 200:
            # Extract SODA2 metadata from headers
            fields_header = r.headers.get('X-SODA2-Fields', '[]')
            types_header = r.headers.get('X-SODA2-Types', '[]')

            # Parse the JSON arrays from headers
            import json
            fields = json.loads(fields_header)
            types = json.loads(types_header)

            # Get sample data to understand field values
            sample_data = r.json()

            # Build comprehensive field metadata
            field_metadata = []
            for i, field in enumerate(fields):
                field_info = {
                    'field_name': field,
                    'data_type': types[i] if i < len(types) else 'unknown',
                    'sample_value': str(sample_data[0].get(field, ''))[:100] if sample_data else '',
                    'description': get_field_description(field, types[i] if i < len(types) else 'unknown'),
                    'usage_notes': get_usage_notes(field, types[i] if i < len(types) else 'unknown')
                }
                field_metadata.append(field_info)

            return field_metadata
        else:
            logger.error(f"Failed to get metadata for {dataset_id}: {r.status_code}")
            return []
    except Exception as e:
        logger.error(f"Exception getting metadata for {dataset_id}: {e}")
        return []

def get_field_description(field_name, data_type):
    """Generate human-readable descriptions for fields based on name and type"""

    field_lower = field_name.lower()

    # Common field descriptions
    descriptions = {
        'id': 'Unique identifier for the record',
        'date': 'Date when the event occurred',
        'time': 'Time when the event occurred',
        'name': 'Name or title of the entity',
        'description': 'Detailed description or explanation',
        'type': 'Category or classification of the record',
        'status': 'Current state or condition',
        'code': 'Numeric or alphanumeric identifier',
        'number': 'Sequential or reference number',
        'address': 'Physical location address',
        'city': 'City name',
        'state': 'State or province',
        'zip': 'Postal/ZIP code',
        'phone': 'Contact phone number',
        'email': 'Contact email address',
        'latitude': 'Geographic latitude coordinate',
        'longitude': 'Geographic longitude coordinate',
        'location': 'Geographic location data',
        'community_area': 'Chicago community area identifier',
        'ward': 'Chicago ward number',
        'precinct': 'Police precinct number',
        'count': 'Count or quantity',
        'total': 'Sum or total value',
        'amount': 'Monetary amount',
        'fee': 'Fee or charge amount',
        'cost': 'Cost or expense amount',
        'price': 'Price or value',
        'area': 'Geographic area identifier',
        'neighborhood': 'Neighborhood name',
        'district': 'Administrative district',
        'region': 'Geographic or administrative region'
    }

    # Try to match field name patterns
    for pattern, desc in descriptions.items():
        if pattern in field_lower:
            return desc

    # Type-based descriptions
    if data_type == 'floating_timestamp':
        return 'Date and time information'
    elif data_type == 'number':
        return 'Numeric value'
    elif data_type == 'text':
        return 'Text or string information'
    elif data_type == 'location':
        return 'Geographic location coordinates'

    return 'Field information'

def get_usage_notes(field_name, data_type):
    """Generate usage notes and examples for fields"""

    field_lower = field_name.lower()

    # Common usage patterns
    usage_notes = {
        'id': 'Primary key, use for unique identification',
        'date': 'Use for date filtering and time-based analysis',
        'time': 'Use for time-based filtering and analysis',
        'name': 'Use for text search and grouping',
        'description': 'Use for content analysis and categorization',
        'type': 'Use for filtering and grouping records',
        'status': 'Use for filtering by current state',
        'code': 'Use for categorization and filtering',
        'number': 'Use for sorting and numeric operations',
        'address': 'Use for geographic analysis and mapping',
        'city': 'Use for geographic filtering and grouping',
        'state': 'Use for geographic filtering and grouping',
        'zip': 'Use for geographic filtering and grouping',
        'latitude': 'Use for mapping and geographic calculations',
        'longitude': 'Use for mapping and geographic calculations',
        'location': 'Use for mapping and geographic analysis',
        'community_area': 'Use for Chicago-specific geographic analysis',
        'ward': 'Use for Chicago political boundary analysis',
        'precinct': 'Use for Chicago police district analysis',
        'count': 'Use for aggregation and statistical analysis',
        'total': 'Use for aggregation and statistical analysis',
        'amount': 'Use for financial analysis and calculations',
        'fee': 'Use for financial analysis and calculations',
        'cost': 'Use for financial analysis and calculations',
        'price': 'Use for financial analysis and calculations'
    }

    # Try to match field name patterns
    for pattern, note in usage_notes.items():
        if pattern in field_lower:
            return note

    # Type-based usage notes
    if data_type == 'floating_timestamp':
        return 'Use for date/time filtering, sorting, and time-based analysis'
    elif data_type == 'number':
        return 'Use for mathematical operations, filtering, and statistical analysis'
    elif data_type == 'text':
        return 'Use for text search, filtering, and grouping operations'
    elif data_type == 'location':
        return 'Use for geographic analysis, mapping, and spatial calculations'

    return 'Use for general data operations'

def get_dataset_summary(domain, dataset_id, dataset_name):
    """Get comprehensive summary information for a dataset"""

    base_url = f"https://{domain}/resource/{dataset_id}.json"

    try:
        # Get total record count
        count_r = requests.get(base_url, params={
            "$select": "count(1) as total_records"
        }, timeout=30)

        total_records = 0
        if count_r.status_code == 200:
            count_data = count_r.json()
            total_records = count_data[0].get('total_records', 0) if count_data else 0

        # Get date range if date fields exist
        date_range = {}
        sample_r = requests.get(base_url, params={"$limit": 1}, timeout=30)
        if sample_r.status_code == 200:
            sample_data = sample_r.json()
            if sample_data:
                # Look for date fields
                date_fields = [key for key in sample_data[0].keys() if 'date' in key.lower() or 'time' in key.lower()]

                for date_field in date_fields[:3]:  # Check first 3 date fields
                    try:
                        date_r = requests.get(base_url, params={
                            "$select": f"min({date_field}) as min_date, max({date_field}) as max_date",
                            "$limit": 1
                        }, timeout=30)

                        if date_r.status_code == 200:
                            date_data = date_r.json()
                            if date_data:
                                date_range[date_field] = {
                                    'min': date_data[0].get('min_date'),
                                    'max': date_data[0].get('max_date')
                                }
                    except Exception as e:
                        logger.warning(f"Could not get date range for {date_field}: {e}")

        # Get last updated information
        last_modified = sample_r.headers.get('Last-Modified', 'Unknown')
        data_out_of_date = sample_r.headers.get('X-SODA2-Data-Out-Of-Date', 'Unknown')

        return {
            'dataset_name': dataset_name,
            'dataset_id': dataset_id,
            'total_records': total_records,
            'date_range': date_range,
            'last_modified': last_modified,
            'data_out_of_date': data_out_of_date,
            'url': base_url
        }

    except Exception as e:
        logger.error(f"Exception getting summary for {dataset_id}: {e}")
        return {
            'dataset_name': dataset_name,
            'dataset_id': dataset_id,
            'total_records': 'Error',
            'date_range': {},
            'last_modified': 'Error',
            'data_out_of_date': 'Error',
            'url': base_url
        }

def create_schema_documentation():
    """Main function to create comprehensive schema documentation"""

    logger.info("Starting schema documentation process...")

    try:
        # Load configuration
        settings = load_settings()
        cfg = load_datasets_yaml()

        logger.info(f"Documenting schemas for domain: {cfg['domain']}")

        # Open Google Sheet
        sh = open_sheet(settings.sheet_id, settings.google_creds_path)

        # Create schema overview sheet
        logger.info("Creating schema overview sheet...")
        overview_ws = upsert_worksheet(sh, "Dataset_Schemas", rows=1000, cols=20)

        # Collect all schema information
        all_schemas = []
        all_summaries = []

        for dataset_name, dataset_config in cfg['datasets'].items():
            logger.info(f"Processing schema for {dataset_name}...")

            # Get dataset summary
            summary = get_dataset_summary(cfg['domain'], dataset_config['id'], dataset_name)
            all_summaries.append(summary)

            # Get field metadata
            field_metadata = get_dataset_metadata(cfg['domain'], dataset_config['id'])

            # Add dataset context to each field
            for field in field_metadata:
                field['dataset_name'] = dataset_name
                field['dataset_id'] = dataset_config['id']
                field['dataset_url'] = summary['url']

            all_schemas.extend(field_metadata)

        # Create overview DataFrame
        overview_data = []
        for summary in all_summaries:
            row = {
                'Dataset Name': summary['dataset_name'],
                'Dataset ID': summary['dataset_id'],
                'Total Records': summary['total_records'],
                'Last Modified': summary['last_modified'],
                'Data Out of Date': summary['data_out_of_date'],
                'URL': summary['url']
            }

            # Add date range information
            for field_name, date_info in summary['date_range'].items():
                row[f'{field_name}_min'] = date_info['min']
                row[f'{field_name}_max'] = date_info['max']

            overview_data.append(row)

        overview_df = pd.DataFrame(overview_data)

        # Create detailed schema DataFrame
        schema_df = pd.DataFrame(all_schemas)

        # Reorder columns for better readability
        if not schema_df.empty:
            column_order = [
                'dataset_name', 'dataset_id', 'field_name', 'data_type',
                'description', 'usage_notes', 'sample_value', 'dataset_url'
            ]
            # Only include columns that exist
            existing_columns = [col for col in column_order if col in schema_df.columns]
            schema_df = schema_df[existing_columns]

        # Write to Google Sheets
        logger.info("Writing overview to Google Sheets...")
        overwrite_with_dataframe(overview_ws, overview_df)

        # Create detailed schema sheet
        logger.info("Creating detailed schema sheet...")
        schema_ws = upsert_worksheet(sh, "Field_Details", rows=len(schema_df) + 100, cols=len(schema_df.columns) + 5)
        overwrite_with_dataframe(schema_ws, schema_df)

        # Create field type summary sheet
        logger.info("Creating field type summary sheet...")
        if not schema_df.empty:
            type_summary = schema_df.groupby(['dataset_name', 'data_type']).size().reset_index(name='count')
            type_summary = type_summary.sort_values(['dataset_name', 'count'], ascending=[True, False])

            type_ws = upsert_worksheet(sh, "Field_Types_Summary", rows=len(type_summary) + 100, cols=10)
            overwrite_with_dataframe(type_ws, type_summary)

        logger.info("Schema documentation completed successfully!")
        logger.info(f"Overview sheet: Dataset_Schemas")
        logger.info(f"Detailed schema: Field_Details")
        logger.info(f"Field types summary: Field_Types_Summary")

        return True

    except Exception as e:
        logger.error(f"Error creating schema documentation: {e}")
        return False

if __name__ == "__main__":
    success = create_schema_documentation()
    if success:
        print("Schema documentation completed successfully!")
    else:
        print("Schema documentation failed. Check logs for details.")
        sys.exit(1)
