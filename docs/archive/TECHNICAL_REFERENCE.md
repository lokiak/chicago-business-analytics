# Chicago SMB Market Radar - Technical Reference

## Code Architecture

### Project Structure
```
src/
├── main.py              # Main execution script
├── socrata.py           # Socrata API client
├── sheets.py            # Google Sheets integration
├── config.py            # Configuration management
├── transform.py          # Data transformation utilities (legacy)
├── brief.py             # Report generation
└── logging_setup.py     # Logging configuration
```

### Key Classes and Functions

#### SocrataClient (`src/socrata.py`)
**Purpose**: Handles all Socrata API interactions

**Key Methods**:
```python
def get(self, dataset_id: str, params, limit: int = 50000, retries: int = 3, backoff: float = 1.5):
    """
    Fetch data from Socrata with automatic pagination and retry logic

    Args:
        dataset_id: Socrata dataset identifier
        params: Query parameters (select, where, order, etc.)
        limit: Records per request (max 50,000)
        retries: Number of retry attempts
        backoff: Exponential backoff multiplier
    """
```

**Features**:
- Automatic pagination handling
- Exponential backoff retry logic
- Comprehensive error logging
- Request timeout management (60 seconds)

#### Google Sheets Integration (`src/sheets.py`)
**Purpose**: Manages Google Sheets operations

**Key Functions**:
```python
def open_sheet(sheet_id: str, creds_path: str):
    """Authenticate and open Google Sheet"""

def upsert_worksheet(sh, title: str, rows: int = 1000, cols: int = 26):
    """Create or update worksheet with specified dimensions"""

def overwrite_with_dataframe(ws, df: pd.DataFrame):
    """Replace worksheet content with DataFrame data"""
```

**Features**:
- Automatic worksheet creation/updating
- Column formatting (dates, numbers)
- Frozen header rows
- Dynamic sizing

## Configuration Management

### Environment Variables
**Required**:
```bash
export GOOGLE_CREDS_PATH="path/to/service-account.json"
export SHEET_ID="your_google_sheet_id"
```

**Optional**:
```bash
export DAYS_LOOKBACK=90          # Default: 90 days
export ENABLE_PERMITS=true       # Default: false
export ENABLE_CTA=true           # Default: false
export BASELINE_WEEKS=13         # Default: 13 (legacy)
```

### Dataset Configuration (`configs/datasets.yaml`)
```yaml
domain: data.cityofchicago.org
datasets:
  business_licenses:
    id: r5kz-chrr
    date_field: license_start_date
    area_field: community_area
    area_name_field: community_area_name
    description_field: license_description
    application_type_field: application_type
    issue_value: ISSUE

  building_permits:
    id: ydr8-5enu
    date_field: issue_date
    area_field: community_area

  cta_boardings:
    id: 6iiy-9s97
    date_field: service_date
    total_field: total_rides
```

## Socrata Query Language (SOQL)

### Query Structure
**Basic Format**:
```python
params = {
    "$select": "field1, field2, field3",
    "$where": "condition1 AND condition2",
    "$order": "field_name",
    "$limit": 50000,
    "$offset": 0
}
```

### Field Selection
**Expanded Business Licenses**:
```python
"$select": ",".join([
    "id", "license_id", "account_number", "site_number",
    "legal_name", "doing_business_as_name", "address",
    "city", "state", "zip_code", "ward", "precinct",
    "ward_precinct", "police_district", "community_area",
    "community_area_name", "neighborhood", "license_code",
    "license_description", "business_activity_id",
    "business_activity", "license_number", "application_type",
    "application_created_date", "application_requirements_complete",
    "payment_date", "conditional_approval", "license_start_date",
    "expiration_date", "license_approved_for_issuance",
    "date_issued", "license_status", "license_status_change_date",
    "ssa", "latitude", "longitude", "location"
])
```

**Expanded Building Permits**:
```python
"$select": ",".join([
    "id", "permit_", "permit_status", "permit_milestone",
    "permit_type", "review_type", "application_start_date",
    "issue_date", "processing_time", "street_number",
    "street_direction", "street_name", "work_type",
    "work_description", "building_fee_paid", "zoning_fee_paid",
    "other_fee_paid", "subtotal_paid", "building_fee_unpaid",
    "zoning_fee_unpaid", "other_fee_unpaid", "subtotal_unpaid",
    "building_fee_waived", "building_fee_subtotal",
    "zoning_fee_subtotal", "other_fee_subtotal",
    "zoning_fee_waived", "other_fee_waived", "subtotal_waived",
    "total_fee", "community_area"
])
```

### Date Filtering
**Current Implementation**:
```python
# Calculate date 90 days ago
start_date = (datetime.utcnow() - pd.Timedelta(days=days_lookback)).strftime('%Y-%m-%d')

# Apply to query
"$where": f"license_start_date >= '{start_date}'"
```

**Alternative Approaches**:
```python
# Using Socrata date functions
"$where": f"date_trunc_ymd(license_start_date) >= '{start_date}'"

# Using relative dates
"$where": "license_start_date >= 'now() - INTERVAL 90 DAY'"
```

## Data Processing Pipeline

### Current Flow (Simplified)
```python
def fetch_licenses(client, cfg, days_lookback: int):
    # 1. Build query parameters
    params = {
        "$select": "id, license_id, legal_name, ...",
        "$where": f"application_type='ISSUE' AND license_start_date >= '{start_date}'",
        "$order": "license_start_date"
    }

    # 2. Fetch data from Socrata
    data = client.get(ds["id"], params)

    # 3. Convert to DataFrame
    df = pd.DataFrame(data)

    # 4. Log field information
    if data:
        actual_fields = list(data[0].keys())
        logger.info(f"Actual fields received: {actual_fields}")

    # 5. Save local backup
    df.to_json(RAW_DIR / f"licenses_{datetime.utcnow().date().isoformat()}.json")

    # 6. Return DataFrame for export
    return df
```

### Data Validation
**Current Checks**:
```python
# Check for empty datasets
if df.empty:
    return df

# Log field availability
if data:
    actual_fields = list(data[0].keys())
    logger.info(f"Actual fields received: {actual_fields}")
```

**Potential Enhancements**:
```python
def validate_dataset(df, expected_fields, dataset_name):
    """Validate dataset structure and data quality"""

    # Check required fields
    missing_fields = set(expected_fields) - set(df.columns)
    if missing_fields:
        logger.warning(f"{dataset_name}: Missing fields: {missing_fields}")

    # Check data types
    for field in df.columns:
        if 'date' in field.lower():
            df[field] = pd.to_datetime(df[field], errors='coerce')
        elif 'fee' in field.lower() or 'amount' in field.lower():
            df[field] = pd.to_numeric(df[field], errors='coerce')

    # Check for null values in key fields
    key_fields = ['id', 'community_area']
    for field in key_fields:
        if field in df.columns:
            null_count = df[field].isnull().sum()
            if null_count > 0:
                logger.warning(f"{dataset_name}: {null_count} null values in {field}")

    return df
```

## Google Sheets Integration

### Sheet Structure
**Full Dataset Sheets**:
- **Business_Licenses_Full**: Complete business licenses data
- **Building_Permits_Full**: Complete building permits data
- **CTA_Full**: Complete CTA ridership data

**Legacy Weekly Sheets** (now empty):
- **Licenses_Weekly**: Weekly aggregated data (legacy)
- **Permits_Weekly**: Weekly aggregated data (legacy)
- **CTA_Weekly**: Weekly aggregated data (legacy)

### Export Process
```python
def export_to_sheets(lic_df, p_df, cta_df, settings):
    """Export datasets to Google Sheets"""

    # Open Google Sheet
    sh = open_sheet(settings.sheet_id, settings.google_creds_path)

    # Export business licenses
    if not lic_df.empty:
        lic_ws = upsert_worksheet(sh, "Business_Licenses_Full",
                                 rows=len(lic_df)+10, cols=50)
        overwrite_with_dataframe(lic_ws, lic_df)

    # Export building permits
    if not p_df.empty:
        permits_ws = upsert_worksheet(sh, "Building_Permits_Full",
                                    rows=len(p_df)+10, cols=50)
        overwrite_with_dataframe(permits_ws, p_df)

    # Export CTA data
    if not cta_df.empty:
        cta_ws = upsert_worksheet(sh, "CTA_Full",
                                 rows=len(cta_df)+10, cols=20)
        overwrite_with_dataframe(cta_ws, cta_df)
```

### Column Formatting
**Automatic Formatting**:
```python
def overwrite_with_dataframe(ws, df: pd.DataFrame):
    # Convert timestamps to strings
    df_clean = df.copy()
    for col in df_clean.columns:
        if 'datetime' in str(df_clean[col].dtype):
            df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d')

    # Update worksheet
    values = [list(df_clean.columns)] + df_clean.values.tolist()
    ws.update(values)

    # Apply formatting
    set_frozen(ws, rows=1, cols=0)  # Freeze header

    # Format date columns
    for idx, col in enumerate(df_clean.columns, start=1):
        if 'date' in col.lower():
            fmt = CellFormat(numberFormat=NumberFormat(type="DATE", pattern="yyyy-mm-dd"))
            format_cell_range(ws, f"{rowcol_to_a1(2, idx)}:{rowcol_to_a1(10000, idx)}", fmt)
```

## Error Handling and Logging

### Logging Configuration
**Setup** (`src/logging_setup.py`):
```python
def setup_logger():
    """Configure logging for the application"""

    # Create logger
    logger = logging.getLogger("market_radar")
    logger.setLevel(logging.INFO)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
```

### Error Recovery Strategies
**Socrata API Errors**:
```python
# Automatic retry with exponential backoff
for attempt in range(retries):
    try:
        r = requests.get(url, params=p, timeout=60)
        if r.status_code == 200:
            break
    except requests.exceptions.RequestException as e:
        if attempt == retries - 1:
            raise RuntimeError(f"Failed after {retries} attempts: {e}")

        # Wait before retry
        wait_time = backoff * (attempt + 1)
        time.sleep(wait_time)
```

**Google Sheets Errors**:
```python
try:
    ws = upsert_worksheet(sh, title, rows, cols)
    overwrite_with_dataframe(ws, df)
except Exception as e:
    logger.error(f"Failed to export to sheet {title}: {e}")
    # Continue with other exports
```

## Performance Optimization

### Memory Management
**Large Dataset Handling**:
```python
# Process data in chunks for very large datasets
def process_large_dataset(df, chunk_size=10000):
    """Process large datasets in chunks to manage memory"""

    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        # Process chunk
        yield chunk
```

**Efficient Data Types**:
```python
# Use appropriate data types to reduce memory usage
def optimize_dataframe(df):
    """Optimize DataFrame memory usage"""

    for col in df.columns:
        if df[col].dtype == 'object':
            # Convert to category if low cardinality
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')

        elif df[col].dtype == 'int64':
            # Use smaller integer types
            if df[col].min() >= 0:
                if df[col].max() < 255:
                    df[col] = df[col].astype('uint8')
                elif df[col].max() < 65535:
                    df[col] = df[col].astype('uint16')

    return df
```

### API Optimization
**Batch Processing**:
```python
# Use Socrata's built-in pagination
def fetch_all_data(client, dataset_id, params):
    """Fetch all data using automatic pagination"""

    all_data = []
    offset = 0

    while True:
        batch_params = params.copy()
        batch_params['$offset'] = offset
        batch_params['$limit'] = 50000

        batch = client.get(dataset_id, batch_params)
        all_data.extend(batch)

        if len(batch) < 50000:
            break

        offset += 50000

    return all_data
```

## Testing and Validation

### Unit Testing
**Example Test Structure**:
```python
import unittest
from unittest.mock import Mock, patch
import pandas as pd

class TestSocrataClient(unittest.TestCase):

    def setUp(self):
        self.client = SocrataClient("test.domain")

    def test_fetch_licenses(self):
        """Test license data fetching"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [
                {'id': '1', 'legal_name': 'Test Business'}
            ]

            result = fetch_licenses(self.client, {}, 90)
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), 1)
```

### Integration Testing
**End-to-End Test**:
```python
def test_full_pipeline():
    """Test complete data pipeline"""

    # Mock external dependencies
    with patch('src.sheets.open_sheet') as mock_sheet:
        with patch('src.socrata.SocrataClient.get') as mock_get:

            # Setup mocks
            mock_get.return_value = [{'id': '1', 'legal_name': 'Test'}]
            mock_sheet.return_value = Mock()

            # Run pipeline
            main()

            # Verify exports
            mock_sheet.assert_called()
```

## Deployment and Operations

### Environment Setup
**Production Requirements**:
```bash
# Python dependencies
pip install -r requirements.txt

# Environment variables
export GOOGLE_CREDS_PATH="/path/to/production/creds.json"
export SHEET_ID="production_sheet_id"
export DAYS_LOOKBACK=90
export ENABLE_PERMITS=true
export ENABLE_CTA=true

# Logging
export LOG_LEVEL=INFO
export LOG_FILE="/var/log/market_radar.log"
```

**Scheduling**:
```bash
# Cron job for daily execution
0 2 * * * cd /path/to/project && python -m src.main >> /var/log/market_radar.log 2>&1
```

### Monitoring
**Health Checks**:
```python
def health_check():
    """Check system health and data quality"""

    checks = {
        'socrata_connectivity': check_socrata_api(),
        'google_sheets_access': check_sheets_access(),
        'data_freshness': check_data_freshness(),
        'export_success': check_recent_exports()
    }

    return all(checks.values()), checks
```

**Metrics Collection**:
```python
def collect_metrics():
    """Collect performance and quality metrics"""

    return {
        'execution_time': execution_duration,
        'records_fetched': total_records,
        'api_calls': api_call_count,
        'export_success_rate': export_success_rate,
        'memory_usage': memory_usage_mb
    }
```
