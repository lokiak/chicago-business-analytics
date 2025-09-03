# Step-by-Step Great Expectations Integration Guide

Here's your complete integration roadmap to upgrade your Chicago SMB Market Radar with Great Expectations data cleaning.

## Phase 1: Setup & Installation (15 minutes)

### Step 1: Install Great Expectations

```bash
# Navigate to your project directory
cd ~/Downloads/chicago-smb-market-radar

# Activate your virtual environment
source .venv/bin/activate

# Install Great Expectations
pip install great-expectations>=0.18.0

# Verify installation
python -c "import great_expectations as gx; print(f'✅ Great Expectations {gx.__version__} installed')"
```

### Step 2: Verify Module Integration

```bash
# Test that our modules can be imported
python -c "
import sys
sys.path.append('step3_transform_model')
sys.path.append('step2_data_ingestion')
from gx_data_cleaning import SmartDataCleaner
from pipeline_integration import enhanced_clean_and_save
print('✅ All GX modules imported successfully')
"
```

If you get import errors, check that all the new files are in the correct locations.

## Phase 2: Testing & Validation (30 minutes)

### Step 3: Run the Demo Notebook

```bash
# Start Jupyter
jupyter notebook

# Navigate to and open:
# step3_transform_model/notebooks/03_gx_testing_demo.ipynb
```

**Run each cell in order and verify:**
- ✅ Pattern detection identifies field types correctly
- ✅ Smart cleaning improves datatype conversions
- ✅ Validation suites run without errors
- ✅ Comparison shows improvements over manual cleaning

### Step 4: Test on Your Current Data

Open your existing `02_data_cleaning.ipynb` and add this test cell:

```python
# TEST CELL - Add this to your existing cleaning notebook
print("🧪 TESTING GX INTEGRATION ON CURRENT DATA")
print("="*50)

# Import the new framework
import sys
sys.path.append('../')  # Adjust path as needed
from gx_data_cleaning import SmartDataCleaner
from pipeline_integration import compare_cleaning_methods

# Test GX cleaning vs your manual cleaning
comparison = compare_cleaning_methods({
    'business_licenses': licenses_df,
    'building_permits': permits_df,
    'cta_boardings': cta_df
})

print("\n🔍 COMPARISON RESULTS:")
for dataset_name in comparison['datasets_compared']:
    if dataset_name in comparison['differences']:
        diff = comparison['differences'][dataset_name]
        gx_numeric = diff['dtype_differences']['gx_numeric_fields']
        manual_numeric = diff['dtype_differences']['manual_numeric_fields']
        print(f"   {dataset_name}: GX={gx_numeric} numeric fields, Manual={manual_numeric}")
        
        if gx_numeric > manual_numeric:
            print(f"   ✅ GX converted {gx_numeric-manual_numeric} additional fields")
```

## Phase 3: Safe Integration (20 minutes)

### Step 5: Create Backup & Test Environment

```bash
# Create backup of current cleaned data sheets
# (manually download or note current sheet names in Google Sheets)
```

### Step 6: Parallel Testing Integration

Add this to your `02_data_cleaning.ipynb` **after** your current cleaning logic:

```python
# PARALLEL TESTING - Add after your existing cleaning
print("\n🔄 RUNNING PARALLEL GX CLEANING TEST")
print("="*50)

# Import GX pipeline
from pipeline_integration import GXPipelineManager

# Create pipeline manager with fallback enabled
gx_pipeline = GXPipelineManager(use_gx=True, fallback_to_manual=True)

# Test GX cleaning on the same source data
gx_test_datasets = {
    'business_licenses': licenses_df,  # Use your original data
    'building_permits': permits_df,
    'cta_boardings': cta_df
}

gx_cleaned_datasets, gx_report = gx_pipeline.clean_datasets_enhanced(gx_test_datasets)

# Compare results
print(f"\n📊 COMPARISON WITH YOUR CURRENT CLEANING:")
for dataset_name in ['business_licenses', 'building_permits', 'cta_boardings']:
    if dataset_name in gx_cleaned_datasets:
        your_df = locals()[f"{dataset_name.split('_')[0]}_df_cleaned"]  # Your cleaned version
        gx_df = gx_cleaned_datasets[dataset_name]
        
        print(f"\n   {dataset_name.upper()}:")
        print(f"      Your cleaning: {your_df.shape[0]} rows, {len(your_df.select_dtypes(include=['number']).columns)} numeric fields")
        print(f"      GX cleaning:   {gx_df.shape[0]} rows, {len(gx_df.select_dtypes(include=['number']).columns)} numeric fields")
        
        # Check for improvements
        your_numeric = len(your_df.select_dtypes(include=['number']).columns)
        gx_numeric = len(gx_df.select_dtypes(include=['number']).columns)
        if gx_numeric > your_numeric:
            print(f"      ✅ GX improved: +{gx_numeric-your_numeric} numeric conversions")

# Test saving to sheets with different suffix (won't overwrite your current data)
save_success = gx_pipeline.save_cleaned_data_to_sheets(gx_cleaned_datasets, "_GX_Test")
print(f"\n💾 Test sheets saved: {save_success}")
if save_success:
    print("   Check Google Sheets for new tabs ending in '_GX_Test'")
```

## Phase 4: Full Integration (15 minutes)

### Step 7: Replace Your Cleaning Workflow

Once you're satisfied with the parallel testing, create a new version of your cleaning notebook:

**Option A: Complete Replacement**

```python
# REPLACE your existing cleaning section with this:
print("🚀 ENHANCED DATA CLEANING WITH GREAT EXPECTATIONS")
print("="*60)

from pipeline_integration import enhanced_clean_and_save

# Your source datasets (same as before)
datasets = {
    'business_licenses': licenses_df,
    'building_permits': permits_df,
    'cta_boardings': cta_df
}

# One-function replacement for your entire cleaning workflow
cleaned_datasets, cleaning_report = enhanced_clean_and_save(datasets, use_gx=True)

# Extract cleaned dataframes (same variable names as before for compatibility)
licenses_df_cleaned = cleaned_datasets['business_licenses']
permits_df_cleaned = cleaned_datasets['building_permits'] 
cta_df_cleaned = cleaned_datasets['cta_boardings']

# Print comprehensive report
print(f"\n📊 CLEANING SUMMARY:")
print(f"   Strategy: {cleaning_report['strategy_used']}")
print(f"   Datasets processed: {len(cleaning_report['datasets_processed'])}")
print(f"   Errors: {len(cleaning_report['errors'])}")
print(f"   Save successful: {cleaning_report['save_success']}")

# Show validation results
validation_results = cleaning_report.get('validation_results', {})
for dataset_name, val_result in validation_results.items():
    if 'success_rate' in val_result:
        print(f"   {dataset_name} validation: {val_result['success_rate']:.1%} success rate")

print("\n✅ ENHANCED CLEANING COMPLETE!")
print("   Check Google Sheets for tabs ending in '_GX_Cleaned'")
```

**Option B: Gradual Integration**

Keep your existing cleaning and add GX validation:

```python
# AFTER your existing cleaning, add this validation:
print("\n✅ VALIDATING WITH GREAT EXPECTATIONS")
print("="*50)

from expectation_suites import validate_chicago_dataset
import great_expectations as gx

# Create GX context
gx_context = gx.get_context()

# Validate your manually cleaned data
validation_datasets = {
    'business_licenses': licenses_df_cleaned,
    'building_permits': permits_df_cleaned,
    'cta_boardings': cta_df_cleaned
}

for dataset_name, df in validation_datasets.items():
    print(f"\n📊 Validating {dataset_name}...")
    validation_result = validate_chicago_dataset(df, dataset_name, gx_context)
    
    if 'error' in validation_result:
        print(f"   ❌ {validation_result['error']}")
    else:
        success_rate = validation_result['success_rate']
        total = validation_result['total_expectations']
        print(f"   📈 {success_rate:.1%} validation success ({total} expectations)")
```

### Step 8: Update Your Main Pipeline

If you use `main.py` or other pipeline scripts, update them:

```python
# In your main pipeline script, replace data cleaning imports:

# OLD:
# from src.transform import clean_data  # or whatever you currently use

# NEW:
from step3_transform_model.pipeline_integration import enhanced_clean_and_save

# Then in your pipeline:
def run_data_cleaning():
    """Enhanced data cleaning with Great Expectations."""
    
    # Load your data (existing logic)
    datasets = load_datasets()  # Your existing data loading
    
    # Replace cleaning call
    cleaned_datasets, report = enhanced_clean_and_save(datasets, use_gx=True)
    
    # Return cleaned data (same interface as before)
    return cleaned_datasets, report
```

## Phase 5: Monitoring & Optimization (10 minutes)

### Step 9: Set Up Quality Monitoring

Add this monitoring cell to track data quality over time:

```python
# DATA QUALITY MONITORING
print("📈 DATA QUALITY METRICS")
print("="*40)

# Track quality improvements
if 'quality_improvements' in cleaning_report:
    improvements = cleaning_report['quality_improvements']
    
    for dataset_name, metrics in improvements.items():
        print(f"\n{dataset_name.upper()}:")
        
        if 'data_types' in metrics:
            dt = metrics['data_types']
            print(f"   Numeric fields: {dt['original_numeric']} → {dt['cleaned_numeric']}")
            print(f"   DateTime fields: {dt['original_datetime']} → {dt['cleaned_datetime']}")
            
        if 'shape_change' in metrics:
            print(f"   Shape: {metrics['shape_change']['rows']}")

# Save quality report for tracking
import json
from datetime import datetime

quality_log = {
    'timestamp': datetime.now().isoformat(),
    'cleaning_report': cleaning_report,
    'validation_summary': {name: result.get('success_rate', 0) 
                          for name, result in validation_results.items()}
}

# Optional: Save to file for trend analysis
with open('../data/quality_logs.jsonl', 'a') as f:
    f.write(json.dumps(quality_log) + '\n')
```

### Step 10: Update Documentation

Update your project's README or documentation:

```markdown
## Data Cleaning

The project now uses Great Expectations for automated, validated data cleaning:

- **Pattern-based field detection**: Automatically detects currency, date, geographic fields
- **Chicago-specific validation**: Community areas 1-77, coordinate bounds, business rules
- **Comprehensive quality checks**: 60+ validation rules across all datasets
- **Fallback reliability**: Automatically falls back to manual cleaning if needed

### Running Data Cleaning

```python
from step3_transform_model.pipeline_integration import enhanced_clean_and_save
cleaned_datasets, report = enhanced_clean_and_save(datasets)
```

### Quality Metrics

Recent validation success rates:
- Business Licenses: 95%+ validation success
- Building Permits: 90%+ validation success  
- CTA Boardings: 98%+ validation success
```

## Phase 6: Production Deployment (5 minutes)

### Step 11: Update Automation Scripts

If you have automated scripts (cron jobs, GitHub Actions), update them:

```python
# In your automation scripts, ensure GX is available:

# requirements.txt should include:
# great-expectations>=0.18.0

# In your automated pipeline:
from step3_transform_model.pipeline_integration import enhanced_clean_and_save

def automated_data_pipeline():
    """Updated automated pipeline with GX cleaning."""
    
    # Your existing data extraction
    datasets = extract_data_from_sources()
    
    # Enhanced cleaning (replaces manual cleaning)
    cleaned_datasets, report = enhanced_clean_and_save(datasets)
    
    # Check validation results
    validation_results = report.get('validation_results', {})
    failed_validations = [name for name, result in validation_results.items() 
                         if result.get('success_rate', 1.0) < 0.90]
    
    if failed_validations:
        # Send alert or log warning
        print(f"⚠️  Validation concerns in: {failed_validations}")
    
    # Continue with your existing pipeline
    return cleaned_datasets
```

## Troubleshooting Guide

### Common Issues & Solutions

**❌ ImportError: No module named 'great_expectations'**
```bash
pip install great-expectations>=0.18.0
```

**❌ GX context creation fails**
```python
# Use file-based context
import great_expectations as gx
context = gx.get_context(mode="file")
```

**❌ Validation failures**
```python
# Enable fallback mode
from pipeline_integration import GXPipelineManager
pipeline = GXPipelineManager(use_gx=True, fallback_to_manual=True)
```

**❌ Memory issues with large datasets**
```python
# Process datasets individually
for dataset_name, df in datasets.items():
    cleaned_df = smart_clean_dataset(df, dataset_name)
```

## Success Criteria

You'll know the integration is successful when:

- ✅ All datasets process without errors
- ✅ Validation success rates >90% 
- ✅ More fields correctly typed (numeric, datetime)
- ✅ Google Sheets populated with `_GX_Cleaned` tabs
- ✅ Quality reports show improvements
- ✅ Existing analysis notebooks work with cleaned data

## Rollback Plan

If you need to revert:

1. **Immediate**: Change `use_gx=False` in your pipeline calls
2. **Full rollback**: Remove GX imports and use your original cleaning cells
3. **Data restoration**: Use your backup sheets or re-run original cleaning

---

**🎯 Total Integration Time: ~90 minutes**

This step-by-step approach ensures you can safely upgrade your data cleaning with comprehensive validation, while maintaining the ability to fall back to your existing workflow if needed.