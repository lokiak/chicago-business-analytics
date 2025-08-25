# Chicago SMB Market Radar - Workflow Documentation

## Current Workflow Overview

The Chicago SMB Market Radar project follows a simplified data pipeline that fetches complete datasets from Chicago's open data sources and exports them directly to Google Sheets for analysis.

## Data Pipeline Flow

### 1. Data Source Configuration
**Location**: `configs/datasets.yaml`

**Configured Datasets**:
- **Business Licenses** (r5kz-chrr): Business license information
- **Building Permits** (ydr8-5enu): Building permit data
- **CTA Boardings** (6iiy-9s97): Transit ridership data

**Configuration Fields**:
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
```

### 2. Data Fetching Process
**Script**: `src/main.py`

**Process Flow**:
1. **Initialize**: Load settings and configuration
2. **Debug APIs**: Test Socrata endpoints for connectivity
3. **Fetch Data**: Retrieve datasets with expanded field selection
4. **Process Data**: Clean and validate datasets
5. **Export Data**: Write to Google Sheets and local storage
6. **Generate Brief**: Create summary report

### 3. Socrata API Integration
**Client**: `src/socrata.py`

**Key Features**:
- Automatic pagination handling
- Retry logic with exponential backoff
- Comprehensive error logging
- Request timeout management

**Query Structure**:
```python
params = {
    "$select": "id, license_id, legal_name, address, city, state, zip_code, ...",
    "$where": "application_type='ISSUE' AND license_start_date >= '2025-05-27'",
    "$order": "license_start_date"
}
```

**No GROUP BY Constraints**: All queries fetch full datasets directly without aggregation.

### 4. Data Processing
**Current Approach**: Minimal processing, direct export

**Processing Steps**:
1. **Fetch Raw Data**: Get complete datasets from Socrata
2. **Data Validation**: Check for empty datasets and errors
3. **Field Logging**: Log actual fields received from API
4. **Local Backup**: Save raw data to JSON files
5. **Direct Export**: Write to Google Sheets without transformation

**Removed Processing**:
- ❌ Weekly aggregation
- ❌ Baseline calculations
- ❌ Momentum analysis
- ❌ Category mapping
- ❌ License normalization

### 5. Google Sheets Export
**Integration**: `src/sheets.py`

**Export Structure**:
- **Business_Licenses_Full**: Complete business licenses dataset
- **Building_Permits_Full**: Complete building permits dataset
- **CTA_Full**: Complete CTA dataset
- **Weekly Sheets**: Empty sheets maintained for compatibility

**Sheet Features**:
- Automatic worksheet creation/updating
- Column formatting (dates, numbers)
- Frozen header rows
- Dynamic sizing based on data

### 6. Local Data Storage
**Location**: `data/raw/`

**File Naming Convention**:
- `licenses_YYYY-MM-DD.json`
- `permits_YYYY-MM-DD.json`
- `cta_YYYY-MM-DD.json`

**Purpose**: Backup and debugging of raw API responses

## Execution Workflow

### Step 1: Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export GOOGLE_CREDS_PATH="path/to/credentials.json"
export SHEET_ID="your_google_sheet_id"
export DAYS_LOOKBACK=90
export ENABLE_PERMITS=true
export ENABLE_CTA=true
```

### Step 2: Run the Pipeline
```bash
# Execute from project root
python -m src.main
```

### Step 3: Monitor Execution
**Log Output**:
- API connectivity tests
- Data fetching progress
- Field validation results
- Export completion status

**Expected Output**:
```
[INFO] === Socrata API Debug ===
[INFO] Domain: data.cityofchicago.org
[INFO] Dataset ID: r5kz-chrr
[INFO] Basic endpoint test - Status: 200
[INFO] Fetching Business Licenses...
[INFO] Retrieved X license records with expanded fields
[INFO] Writing to Google Sheets...
[INFO] Writing full business licenses dataset with X records and Y columns...
[INFO] Done.
```

## Data Schema

### Business Licenses (40+ Fields)
**Core Fields**:
- `id`: Unique record identifier
- `license_id`: License number
- `legal_name`: Business legal name
- `doing_business_as_name`: DBA name
- `address`: Street address
- `city`, `state`, `zip_code`: Location
- `ward`, `precinct`: Political boundaries
- `community_area`, `community_area_name`: Geographic areas
- `license_code`, `license_description`: License details
- `application_type`: Application type (ISSUE, RENEW, etc.)
- `license_start_date`, `expiration_date`: Validity periods
- `latitude`, `longitude`: Geographic coordinates

### Building Permits (30+ Fields)
**Core Fields**:
- `id`: Unique record identifier
- `permit_`: Permit number
- `permit_status`: Current status
- `permit_type`: Type of permit
- `work_type`: Type of work
- `work_description`: Detailed description
- `street_number`, `street_name`: Address
- `community_area`: Geographic area
- `issue_date`: Permit issue date
- `building_fee_paid`, `zoning_fee_paid`: Fee information

### CTA Data
**Core Fields**:
- `service_date`: Date of service
- `total_rides`: Total ridership count
- `bus`, `rail_boardings`: Mode-specific counts

## Error Handling

### Common Issues
1. **API Connectivity**: Network timeouts, authentication errors
2. **Data Validation**: Empty datasets, missing fields
3. **Google Sheets**: Authentication, permission, quota issues

### Error Recovery
- **Automatic Retries**: 3 attempts with exponential backoff
- **Graceful Degradation**: Continue with available data
- **Comprehensive Logging**: Detailed error information
- **Local Backup**: Raw data saved regardless of export success

## Performance Considerations

### API Limits
- **Socrata**: 50,000 records per request (handled automatically)
- **Google Sheets**: Rate limiting considerations
- **Memory Usage**: Large datasets loaded into memory

### Optimization Strategies
- **Direct Fetching**: No intermediate aggregation
- **Batch Processing**: Automatic pagination handling
- **Efficient Export**: Direct DataFrame to Sheets conversion

## Monitoring and Maintenance

### Health Checks
- **API Connectivity**: Test endpoints before data fetching
- **Data Quality**: Log field availability and data counts
- **Export Success**: Verify Google Sheets updates

### Maintenance Tasks
- **Regular Execution**: Daily/weekly data updates
- **Log Rotation**: Monitor log file sizes
- **Data Validation**: Check for schema changes
- **Performance Monitoring**: Track execution times

## Future Enhancements

### Potential Improvements
- **Data Validation**: Schema validation and data quality checks
- **Incremental Updates**: Delta processing for efficiency
- **Error Notifications**: Alert system for failures
- **Performance Metrics**: Execution time and success rate tracking
- **Data Lineage**: Track data source and transformation history

### Scalability Considerations
- **Large Datasets**: Handle millions of records efficiently
- **Multiple Sources**: Add additional data sources
- **Real-time Updates**: Near real-time data processing
- **Distributed Processing**: Handle multiple datasets concurrently
