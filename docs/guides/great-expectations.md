# Great Expectations Data Cleaning Framework

A comprehensive, automated data cleaning solution for the Chicago SMB Market Radar project built on Great Expectations, pattern recognition, and domain expertise.

## Overview

This framework upgrades your existing manual data cleaning workflow with:

- **Pattern-based field detection** - Automatically detects currency, date, geographic, and categorical fields
- **Smart data transformations** - Handles Chicago-specific business rules and constraints  
- **Comprehensive validation** - 60+ pre-built expectations covering data quality and business logic
- **Seamless integration** - Drop-in replacement for existing cleaning functions
- **Fallback reliability** - Automatically falls back to manual cleaning if needed

## Quick Start

### 1. Installation

```bash
pip install great-expectations>=0.18.0
```

### 2. Drop-in Replacement

Replace your existing cleaning code with:

```python
from pipeline_integration import enhanced_clean_and_save

# Instead of your current cleaning workflow:
cleaned_datasets, report = enhanced_clean_and_save(datasets, use_gx=True)
```

### 3. Test Drive

Run the demo notebook to see it in action:

```bash
jupyter notebook step3_transform_model/notebooks/03_gx_testing_demo.ipynb
```

## Architecture

```
step3_transform_model/
├── gx_data_cleaning.py         # Core smart cleaning engine
├── desired_schema.py           # Target schema with proper datatypes  
├── expectation_suites.py       # Pre-built Chicago SMB validation rules
├── pipeline_integration.py     # Drop-in replacement functions
└── notebooks/
    └── 03_gx_testing_demo.ipynb # Testing and demonstration
```

## Key Features

### 🔍 Smart Field Detection

Automatically detects and converts field types based on naming patterns:

- **Currency fields**: `fee`, `paid`, `cost` → proper float with validation
- **Geographic fields**: `latitude`, `longitude` → Chicago coordinate bounds
- **Administrative**: `community_area`, `ward` → integer with Chicago ranges
- **Dates**: `created`, `issued`, `start` → datetime with business logic
- **Categories**: `status`, `type` → categorical with allowed values

### 🏛️ Chicago-Specific Business Rules

Pre-built validation for Chicago SMB data:

- Community areas must be 1-77
- Coordinates within Chicago bounds (41.6-42.1 lat, -87.9--87.5 lng)
- ZIP codes start with 606, 607, or 608
- Ward numbers 1-50
- License start dates before expiration dates

### 📊 Comprehensive Validation

60+ expectations across all datasets:

- **Business Licenses**: 25 expectations (geographic, temporal, categorical)
- **Building Permits**: 20 expectations (financial, process, geographic)
- **CTA Boardings**: 8 expectations (ridership bounds, temporal)

### 🔄 Seamless Integration

Three integration options:

1. **Full Replacement**: Use `enhanced_clean_and_save()` 
2. **Gradual Adoption**: Run alongside existing cleaning with `compare_cleaning_methods()`
3. **Validation Only**: Keep manual cleaning, add GX validation

## Usage Examples

### Basic Usage

```python
from gx_data_cleaning import SmartDataCleaner

cleaner = SmartDataCleaner()
cleaned_df = cleaner.execute_smart_cleaning(df, 'business_licenses')
```

### Batch Processing

```python
from gx_data_cleaning import batch_clean_datasets

cleaned_datasets = batch_clean_datasets({
    'business_licenses': licenses_df,
    'building_permits': permits_df, 
    'cta_boardings': cta_df
})
```

### Pipeline Integration

```python
from pipeline_integration import enhanced_clean_and_save

# Drop-in replacement for existing workflow
cleaned_datasets, report = enhanced_clean_and_save(datasets)

# Saves to Google Sheets with '_GX_Cleaned' suffix
# Includes comprehensive validation reporting
```

### Method Comparison

```python
from pipeline_integration import compare_cleaning_methods

comparison = compare_cleaning_methods(datasets)
# Compare GX vs manual cleaning side-by-side
```

## Validation Results

The framework tracks comprehensive metrics:

```python
{
    'validation_success': True,
    'success_rate': 0.95,
    'expectations_met': 23,
    'total_expectations': 25,
    'quality_improvements': {
        'numeric_conversions': 6,
        'datetime_conversions': 4,
        'business_rules_applied': 8
    }
}
```

## Field Type Detection

### Automatic Pattern Matching

| Field Pattern | Detected Type | Validation Rules | Example |
|--------------|---------------|------------------|---------|
| `*fee*`, `*paid*`, `*cost*` | Currency | min: 0, max: 1M | `building_fee_paid` |
| `*latitude*`, `*lat*` | Float | Chicago bounds | `latitude` |
| `community_area*` | Integer | 1-77 | `community_area` |
| `*date*`, `*created*` | DateTime | Not future | `license_start_date` |
| `*status*`, `*type*` | Category | Allowed values | `permit_status` |

### Custom Transformations

```python
# Currency fields get special handling
'building_fee_paid': remove $ symbols, convert to float, validate >= 0

# Geographic fields get bounds checking  
'latitude': convert to float, validate Chicago bounds (41.6-42.1)

# Dates get flexible parsing
'license_start_date': parse multiple formats, validate business logic
```

## Pre-built Expectation Suites

### Business Licenses (25 expectations)
- Core identifiers (id, license_id uniqueness)
- Geographic validation (community areas 1-77, Chicago coordinates)
- Temporal validation (start < expiration dates)
- Business logic (valid status values, application types)

### Building Permits (20 expectations)  
- Permit workflow validation (issue dates, processing times)
- Financial validation (non-negative fees, reasonable amounts)
- Geographic validation (community areas, street directions)
- Work type categorization

### CTA Boardings (8 expectations)
- Daily ridership bounds (0-2M rides)
- Date continuity validation  
- Historical range validation (2010-present)
- Average ridership expectations

## Integration Workflow

### Option A: Full Replacement

```python
# Replace your existing cleaning cell with:
from pipeline_integration import enhanced_clean_and_save

datasets = {
    'business_licenses': licenses_df,
    'building_permits': permits_df,
    'cta_boardings': cta_df
}

cleaned_datasets, report = enhanced_clean_and_save(datasets)

# Automatically saves to Google Sheets with '_GX_Cleaned' suffix
# Provides comprehensive validation reporting
```

### Option B: Gradual Migration

```python
# Compare both methods side-by-side
comparison = compare_cleaning_methods(datasets)

# Use GX for some datasets, manual for others
pipeline = GXPipelineManager(use_gx=True, fallback_to_manual=True)
cleaned_datasets, report = pipeline.clean_datasets_enhanced(datasets)
```

### Option C: Validation Only

```python  
# Keep existing cleaning, add GX validation
from expectation_suites import validate_chicago_dataset

# After your existing cleaning:
validation_results = validate_chicago_dataset(cleaned_df, 'business_licenses', gx_context)
```

## Quality Improvements

Expected improvements over manual cleaning:

### Data Type Conversions
- **Before**: 5 numeric fields, 9 object date fields  
- **After**: 11 numeric fields, 7 proper datetime fields

### Business Rule Enforcement
- Date logic validation (start < expiration)
- Geographic bounds checking (Chicago coordinates)
- Administrative validation (wards 1-50, areas 1-77)
- Financial validation (non-negative fees)

### Data Quality Metrics
- Completeness scoring per field
- Validity rate tracking
- Business rule compliance
- Trend analysis readiness

## Testing & Validation

Run the comprehensive test suite:

```bash
jupyter notebook step3_transform_model/notebooks/03_gx_testing_demo.ipynb
```

Tests include:
- Pattern detection accuracy
- Transformation correctness  
- Validation suite functionality
- Pipeline integration
- Comparison with manual cleaning

## Troubleshooting

### Common Issues

**Great Expectations not installed:**
```bash
pip install great-expectations>=0.18.0
```

**Import errors:**
```python
# Check module availability
try:
    from gx_data_cleaning import SmartDataCleaner
    print("✅ GX modules available")
except ImportError:
    print("❌ Check file paths and dependencies")
```

**Validation failures:**
```python
# Enable fallback to manual cleaning
pipeline = GXPipelineManager(use_gx=True, fallback_to_manual=True)
```

### Performance Considerations

- Pattern detection runs on first 10 sample rows for efficiency
- Validation can be skipped in production if needed
- Fallback ensures pipeline never fails completely

## Migration Checklist

- [ ] Install Great Expectations: `pip install great-expectations>=0.18.0`
- [ ] Run test notebook: `03_gx_testing_demo.ipynb`
- [ ] Compare cleaning methods on your latest data
- [ ] Backup current cleaned data before switching
- [ ] Update pipeline to use `enhanced_clean_and_save()`
- [ ] Monitor validation results and quality metrics
- [ ] Set up alerts for validation failures

## Support

The framework is designed to be:
- **Self-documenting**: Comprehensive logging and reporting
- **Self-healing**: Automatic fallback to manual cleaning
- **Self-improving**: Quality metrics track improvements over time

For issues or enhancements, the modular design allows easy customization of:
- Field detection patterns (`desired_schema.py`)
- Expectation suites (`expectation_suites.py`)  
- Transformation logic (`gx_data_cleaning.py`)
- Integration workflow (`pipeline_integration.py`)

---

**Ready to upgrade your data quality?** Start with the test notebook and see the difference Great Expectations makes for your Chicago SMB Market Radar data pipeline.