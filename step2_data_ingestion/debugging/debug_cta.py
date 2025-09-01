#!/usr/bin/env python3
"""
Debug script to investigate CTA dataset schema and data availability
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd

def test_cta_dataset():
    """Test CTA dataset to understand schema and data availability"""

    dataset_id = "6iiy-9s97"
    base_url = f"https://data.cityofchicago.org/resource/{dataset_id}.json"

    print("=== CTA Dataset Investigation ===")
    print(f"Dataset ID: {dataset_id}")
    print(f"Base URL: {base_url}")

    # Test 1: Get basic schema
    print("\n1. Getting basic schema...")
    try:
        r = requests.get(base_url, params={"$limit": 5}, timeout=30)
        print(f"Status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            print(f"Records returned: {len(data)}")

            if data:
                print(f"Columns: {list(data[0].keys())}")
                print(f"Sample record:")
                for key, value in data[0].items():
                    print(f"  {key}: {value}")

                # Check date range in the dataset
                print(f"\nSample of all {len(data)} records:")
                for i, record in enumerate(data):
                    print(f"  Record {i+1}: service_date={record.get('service_date')}, total_rides={record.get('total_rides')}")
            else:
                print("No records returned")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

    # Test 2: Check date range availability
    print("\n2. Checking date range availability...")
    try:
        # Get min and max dates
        r = requests.get(base_url, params={
            "$select": "min(service_date) as min_date, max(service_date) as max_date",
            "$limit": 1
        }, timeout=30)

        if r.status_code == 200:
            data = r.json()
            if data:
                print(f"Date range in dataset:")
                print(f"  Min date: {data[0].get('min_date')}")
                print(f"  Max date: {data[0].get('max_date')}")
        else:
            print(f"Date range query failed: {r.text}")
    except Exception as e:
        print(f"Date range query exception: {e}")

    # Test 3: Check recent data (last 30 days)
    print("\n3. Checking recent data availability...")
    recent_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    print(f"Looking for data since: {recent_date}")

    try:
        r = requests.get(base_url, params={
            "$select": "service_date, total_rides",
            "$where": f"service_date >= '{recent_date}'",
            "$order": "service_date DESC",
            "$limit": 10
        }, timeout=30)

        if r.status_code == 200:
            data = r.json()
            print(f"Recent records found: {len(data)}")
            for record in data:
                print(f"  {record.get('service_date')}: {record.get('total_rides')} total rides")
        else:
            print(f"Recent data query failed: {r.text}")
    except Exception as e:
        print(f"Recent data query exception: {e}")

    # Test 4: Check data for different date ranges
    print("\n4. Testing different date ranges...")
    test_dates = [
        (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),   # 1 week ago
        (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # 1 month ago
        (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),  # 3 months ago
        (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), # 1 year ago
        '2024-01-01',  # Fixed date
        '2023-01-01',  # Fixed date
    ]

    for test_date in test_dates:
        try:
            r = requests.get(base_url, params={
                "$select": "count(1) as record_count",
                "$where": f"service_date >= '{test_date}'",
                "$limit": 1
            }, timeout=30)

            if r.status_code == 200:
                data = r.json()
                count = data[0].get('record_count', 0) if data else 0
                print(f"  Records since {test_date}: {count}")
            else:
                print(f"  Query failed for {test_date}: {r.text[:100]}")
        except Exception as e:
            print(f"  Exception for {test_date}: {e}")

    # Test 5: Check the exact query being used
    print("\n5. Testing the exact query from the application...")
    lookback_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    exact_params = {
        '$select': 'service_date as day, sum(total_rides) as boardings',
        '$where': f"service_date >= '{lookback_date}'",
        '$group': 'day',
        '$order': 'day',
        '$limit': 50000,
        '$offset': 0
    }

    print(f"Exact query params: {exact_params}")

    try:
        r = requests.get(base_url, params=exact_params, timeout=60)
        print(f"Exact query status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            print(f"Exact query results: {len(data)} records")
            if data:
                print("Sample results:")
                for i, record in enumerate(data[:5]):
                    print(f"  {record}")
        else:
            print(f"Exact query failed: {r.text}")
    except Exception as e:
        print(f"Exact query exception: {e}")

if __name__ == "__main__":
    test_cta_dataset()
