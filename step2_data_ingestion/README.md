# Step 2: Data Ingestion

This directory contains the data ingestion components for Step 2 of the BI 0→1 Framework.

## 🎯 **Overview**

Step 2 focuses on **Data Ingestion** - fetching data from Chicago's open data sources using a schema-driven approach. The `schema.py` file provides centralized field definitions that are used by the main data fetching functions in `src/main.py`.

## 📁 **Directory Structure**

```
step2_data_ingestion/
├── README.md                 # This file
├── __init__.py              # Package initialization
├── schema.py                # 🆕 Centralized schema definitions
├── config_manager.py        # Configuration management (moved from src)
├── socrata_client.py        # Socrata API client (moved from src)
└── notebooks/               # Data exploration notebooks
    └── 01_api_exploration.ipynb
```

**Main data fetching logic**: `src/main.py` (uses schema definitions from this directory)

## 🆕 **New Schema-Driven Approach**

### **Key Benefits**

1. **Single Source of Truth**: All field definitions in one place
2. **Type Safety**: Data types and validation rules defined
3. **Reusability**: Schema can be used across all pipeline steps
4. **Maintainability**: Easy to update when APIs change
5. **Documentation**: Self-documenting field descriptions

### **Schema Components**

#### **1. Field Definitions**
```python
FieldDefinition(
    name="license_id",
    data_type=DataType.STRING,
    description="License ID number",
    required=True,
    nullable=False
)
```

#### **2. Dataset Schemas**
```python
DatasetSchema(
    name="business_licenses",
    description="Chicago Business Licenses dataset",
    primary_key="id",
    date_field="license_start_date",
    area_field="community_area",
    area_name_field="community_area_name",
    fields=[...]
)
```

#### **3. Schema Manager**
```python
# Get all fields for a dataset
fields = SchemaManager.get_field_names("business_licenses")

# Get required fields only
required = SchemaManager.get_required_fields("business_licenses")

# Get date fields
dates = SchemaManager.get_date_fields("business_licenses")

# Get geographic fields
geo = SchemaManager.get_geographic_fields("business_licenses")
```

## 🔧 **Usage Examples**

### **Using Schema in Data Fetching**

The schema is now used in `src/main.py` instead of hardcoded field lists:

```python
# Before (hardcoded):
params = {
    "$select": ",".join([
        "id", "license_id", "account_number", ...  # long hardcoded list
    ])
}

# After (schema-driven):
from schema import SchemaManager
field_names = SchemaManager.get_field_names("business_licenses")
params = {
    "$select": ",".join(field_names)
}
```

### **Running Data Ingestion**

```bash
# Run the main data ingestion (uses schema)
cd src && python main.py
```

### **Schema Validation**

```python
from step2_data_ingestion.schema import SchemaManager

# Validate field exists
exists = SchemaManager.validate_field_exists("business_licenses", "license_id")

# Get field definition
field_def = SchemaManager.get_field_definition("business_licenses", "license_id")
print(f"Field: {field_def.name}, Type: {field_def.data_type}")
```

## 🧪 **Testing**

### **Run Schema Tests**

```bash
# Test schema functionality
python step2_data_ingestion/test_schema.py

# Test specific components
python -c "from step2_data_ingestion.schema import SchemaManager; print(SchemaManager.get_field_names('business_licenses'))"
```

### **Test Data Fetching**

```bash
# Test data fetcher
python -c "from step2_data_ingestion.data_fetcher import create_data_fetcher; fetcher = create_data_fetcher(); print('Fetcher created successfully')"
```

## 📊 **Data Sources**

### **1. Business Licenses**
- **Source**: Chicago Data Portal
- **Fields**: 40+ fields including business info, location, dates
- **Update Frequency**: Daily
- **Lookback**: 90 days (configurable)

### **2. Building Permits**
- **Source**: Chicago Data Portal
- **Fields**: 25+ fields including permit info, location, fees
- **Update Frequency**: Daily
- **Lookback**: 90 days (configurable)

### **3. CTA Boardings**
- **Source**: Chicago Data Portal
- **Fields**: Date, total rides
- **Update Frequency**: Daily
- **Lookback**: 730 days (2 years)

## 🔄 **Pipeline Steps**

1. **Schema Validation**: Validate field definitions
2. **Data Fetching**: Fetch data using schema-driven queries
3. **Quality Validation**: Check data quality and completeness
4. **Raw Data Storage**: Save to JSON files
5. **Google Sheets**: Write to Google Sheets
6. **Summary Generation**: Create ingestion summary

## 🚀 **Running Step 2**

### **Via Main Entry Point**

```bash
# Run Step 2 only
python main.py --step 2

# Run multiple steps including Step 2
python main.py --steps 2,3,4
```

### **Direct Execution**

```bash
# Run pipeline directly
python step2_data_ingestion/pipeline.py

# Run tests
python step2_data_ingestion/test_schema.py
```

## 📈 **Outputs**

### **Raw Data Files**
- `data/raw/business_licenses_YYYY-MM-DD.json`
- `data/raw/building_permits_YYYY-MM-DD.json`
- `data/raw/cta_boardings_YYYY-MM-DD.json`

### **Google Sheets**
- `Business_Licenses_Full` worksheet
- `Building_Permits_Full` worksheet
- `CTA_Full` worksheet

### **Quality Report**
```json
{
  "business_licenses": {
    "status": "good",
    "record_count": 1250,
    "column_count": 42,
    "issues": []
  }
}
```

## 🔧 **Configuration**

### **Environment Variables**
- `SOCRATA_APP_TOKEN`: Socrata API token
- `GOOGLE_CREDS_PATH`: Path to Google credentials
- `SHEET_ID`: Google Sheets ID
- `DAYS_LOOKBACK`: Default lookback period

### **Dataset Configuration**
- `configs/datasets.yaml`: Dataset IDs and field mappings
- `configs/category_map.csv`: Business category mappings

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Missing Fields**: Check schema definitions match API
2. **Data Quality Issues**: Review quality report in logs
3. **API Rate Limits**: Reduce lookback period or add delays
4. **Google Sheets Errors**: Verify credentials and sheet permissions

### **Debug Mode**

```python
# Enable debug logging
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Run with minimal data
pipeline = DataIngestionPipeline()
results = pipeline.run_pipeline(days_lookback=1)
```

## 🔮 **Future Enhancements**

1. **Schema Versioning**: Track schema changes over time
2. **Data Validation**: Add more sophisticated validation rules
3. **Incremental Updates**: Only fetch new/changed data
4. **Error Recovery**: Retry failed requests automatically
5. **Performance Monitoring**: Track ingestion performance metrics

## 📚 **Related Documentation**

- [BI Framework Strategic Plan](../../docs/BI_FRAMEWORK_STRATEGIC_PLAN.md)
- [Technical Reference](../../docs/TECHNICAL_REFERENCE.md)
- [Workflow Guide](../../docs/WORKFLOW.md)
- [Step 3: Transform & Model](../step3_transform_model/README.md)
