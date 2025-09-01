#!/usr/bin/env python3
"""
Comprehensive debug script to test all datasets and investigate schemas
"""

import requests
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path

def load_config():
    """Load the datasets configuration"""
    config_path = Path("configs/datasets.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_dataset_schema(domain, dataset_id, dataset_name):
    """Test a dataset to understand its schema and data availability"""

    base_url = f"https://{domain}/resource/{dataset_id}.json"

    print(f"\n=== {dataset_name.upper()} DATASET ({dataset_id}) ===")
    print(f"URL: {base_url}")

    # Test 1: Get basic schema
    print("\n1. Schema Analysis:")
    try:
        r = requests.get(base_url, params={"$limit": 3}, timeout=30)
        print(f"   Status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            print(f"   Records returned: {len(data)}")

            if data:
                print(f"   Columns ({len(data[0])}): {list(data[0].keys())}")

                # Show sample data
                print(f"   Sample records:")
                for i, record in enumerate(data[:2]):
                    print(f"     Record {i+1}:")
                    for key, value in record.items():
                        if len(str(value)) > 50:
                            value = str(value)[:47] + "..."
                        print(f"       {key}: {value}")
                    print()

                # Identify potential date/time columns
                date_columns = [key for key in data[0].keys() if 'date' in key.lower() or 'time' in key.lower()]
                print(f"   Potential date columns: {date_columns}")

                # Identify potential numeric columns
                numeric_columns = []
                for key, value in data[0].items():
                    try:
                        float(value)
                        numeric_columns.append(key)
                    except (ValueError, TypeError):
                        pass
                print(f"   Potential numeric columns: {numeric_columns}")

            else:
                print("   No records returned")
        else:
            print(f"   Error: {r.text}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 2: Check date range availability (if we found date columns)
    print("\n2. Date Range Analysis:")
    try:
        # Try to get date range for any date column we found
        if 'data' in locals() and data and date_columns:
            for date_col in date_columns[:2]:  # Test first 2 date columns
                try:
                    r = requests.get(base_url, params={
                        "$select": f"min({date_col}) as min_date, max({date_col}) as max_date",
                        "$limit": 1
                    }, timeout=30)

                    if r.status_code == 200:
                        date_data = r.json()
                        if date_data:
                            print(f"   {date_col}:")
                            print(f"     Min: {date_data[0].get('min_date')}")
                            print(f"     Max: {date_data[0].get('max_date')}")
                    else:
                        print(f"   {date_col}: Query failed - {r.text[:100]}")
                except Exception as e:
                    print(f"   {date_col}: Exception - {e}")
        else:
            print("   No date columns found or no data available")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 3: Check recent data availability
    print("\n3. Recent Data Availability:")
    if 'data' in locals() and data and date_columns:
        test_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        for date_col in date_columns[:1]:  # Test primary date column
            try:
                r = requests.get(base_url, params={
                    "$select": "count(1) as record_count",
                    "$where": f"{date_col} >= '{test_date}'",
                    "$limit": 1
                }, timeout=30)

                if r.status_code == 200:
                    count_data = r.json()
                    count = count_data[0].get('record_count', 0) if count_data else 0
                    print(f"   Records since {test_date} ({date_col}): {count}")
                else:
                    print(f"   Query failed for {date_col}: {r.text[:100]}")
            except Exception as e:
                print(f"   Exception for {date_col}: {e}")
    else:
        print("   No date columns available for testing")

def test_all_datasets():
    """Test all datasets defined in the configuration"""

    print("Chicago SMB Market Radar - Dataset Debug Tool")
    print("=" * 50)

    try:
        cfg = load_config()
        domain = cfg['domain']
        datasets = cfg['datasets']

        print(f"Domain: {domain}")
        print(f"Datasets to test: {list(datasets.keys())}")

        for name, config in datasets.items():
            dataset_id = config['id']
            test_dataset_schema(domain, dataset_id, name)

    except Exception as e:
        print(f"Error loading configuration: {e}")

    print("\n" + "=" * 50)
    print("Debug complete!")

def test_specific_query(dataset_name=None):
    """Test a specific query configuration"""
    if not dataset_name:
        return

    try:
        cfg = load_config()
        domain = cfg['domain']
        ds_config = cfg['datasets'][dataset_name]

        print(f"\n=== TESTING SPECIFIC QUERY: {dataset_name.upper()} ===")
        print(f"Configuration: {ds_config}")

        # Build the actual query used by the application
        if dataset_name == "business_licenses":
            days_lookback = 90
            start_date = (datetime.now() - timedelta(days=days_lookback)).strftime('%Y-%m-%d')

            params = {
                "$select": ",".join([
                    f"{ds_config['area_name_field']}",
                    f"{ds_config['area_field']}",
                    f"{ds_config['description_field']}",
                    f"date_trunc_ymd({ds_config['date_field']}) as day",
                    "count(1) as n"
                ]),
                "$where": f"{ds_config['application_type_field']}='{ds_config['issue_value']}' AND {ds_config['date_field']} >= '{start_date}'",
                "$group": ",".join([ds_config['area_name_field'], ds_config['area_field'], ds_config['description_field'], "day"]),
                "$order": "day",
                "$limit": 10  # Limit for testing
            }

        elif dataset_name == "building_permits":
            days_lookback = 90
            start_date = (datetime.now() - timedelta(days=days_lookback)).strftime('%Y-%m-%d')

            params = {
                "$select": f"{ds_config['area_field']}, date_trunc_ymd({ds_config['date_field']}) as day, count(1) as n",
                "$where": f"{ds_config['date_field']} >= '{start_date}'",
                "$group": f"{ds_config['area_field']}, day",
                "$order": "day",
                "$limit": 10
            }

        elif dataset_name == "cta_boardings":
            days_lookback = 730  # 2 years for CTA
            start_date = (datetime.now() - timedelta(days=days_lookback)).strftime('%Y-%m-%d')

            params = {
                "$select": f"{ds_config['date_field']} as day, sum({ds_config['total_field']}) as boardings",
                "$where": f"{ds_config['date_field']} >= '{start_date}'",
                "$group": "day",
                "$order": "day",
                "$limit": 10
            }

        print(f"Query parameters: {params}")

        url = f"https://{domain}/resource/{ds_config['id']}.json"
        r = requests.get(url, params=params, timeout=60)

        print(f"Response status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Records returned: {len(data)}")
            if data:
                print("Sample results:")
                for i, record in enumerate(data[:3]):
                    print(f"  {i+1}: {record}")
        else:
            print(f"Error response: {r.text}")

    except Exception as e:
        print(f"Exception testing {dataset_name}: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Test specific dataset
        dataset_name = sys.argv[1]
        test_specific_query(dataset_name)
    else:
        # Test all datasets
        test_all_datasets()

        # Also test specific queries
        print("\n" + "=" * 50)
        print("TESTING SPECIFIC APPLICATION QUERIES")
        for dataset in ["business_licenses", "building_permits", "cta_boardings"]:
            test_specific_query(dataset)
