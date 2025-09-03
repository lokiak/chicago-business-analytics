# Your First Analysis

Run your first Chicago SMB Market Radar analysis and explore the results.

## Quick Start

### 1. Run the Complete Pipeline

```bash
# From the project root directory
make run
```

This command executes all steps of the BI 0→1 Framework:
- **Step 2**: Data ingestion from Chicago Open Data
- **Step 3**: Data transformation and cleaning  
- **Step 4**: Data validation and quality checks
- **Step 5**: Report generation
- **Step 6**: Automation setup

### 2. Watch the Process

You'll see output like this:

```
🚀 Running complete BI 0→1 Framework pipeline...
📊 Running data ingestion...
   ✅ Business Licenses: 2,040 records
   ✅ Building Permits: 8,647 records  
   ✅ CTA Boardings: 668 records
🧹 Running data transformation...
   ✅ Enhanced cleaning with Great Expectations
   📊 Validation: 95% success rate
📈 Generating reports...
   ✅ Weekly brief created: reports/brief_2025-W35.md
🏁 Pipeline completed: 6/6 steps successful
```

### 3. Explore the Results

**Check Google Sheets:**
Your Google Sheet now contains cleaned data:
- `Business_Licenses_GX_Cleaned` - Enhanced business license data
- `Building_Permits_GX_Cleaned` - Cleaned permit data
- `CTA_GX_Cleaned` - Transit ridership data

**Review Generated Reports:**
```bash
# View the latest brief
cat reports/brief_2025-W35.md

# List all reports
ls -la reports/
```

**Explore with Jupyter:**
```bash
# Start Jupyter
jupyter notebook

# Open the analysis notebooks
# - notebooks/01_data_exploration.ipynb
# - notebooks/02_business_analysis.ipynb
```

## Understanding the Data

### Business Licenses Dataset
- **2,000+ records** of Chicago business licenses
- **Community area breakdowns** for geographic analysis
- **License types** categorized for trend analysis
- **Temporal data** for time series analysis

### Building Permits Dataset  
- **8,000+ records** of construction permits
- **Fee information** for economic impact analysis
- **Processing times** for efficiency metrics
- **Geographic distribution** across Chicago

### CTA Ridership Dataset
- **Daily ridership totals** for economic correlation
- **Time series data** for trend analysis
- **Economic indicator** for business activity

## Key Insights from Your First Run

1. **Data Quality**: Great Expectations validation shows 95%+ data quality
2. **Geographic Coverage**: All 77 Chicago community areas represented  
3. **Temporal Range**: Historical data from 2020-present
4. **Business Diversity**: 50+ license types across sectors

## Next Steps

### Dive Deeper
- **[Explore the Framework](../framework/)** - Understand each pipeline step
- **[Try Advanced Cleaning](../guides/great-expectations.md)** - Use Great Expectations features
- **[Set Up Automation](../guides/automation.md)** - Schedule regular updates

### Customize Your Analysis
- **Modify date ranges** in `configs/datasets.yaml`
- **Add new data sources** following the framework
- **Create custom visualizations** in Jupyter notebooks

### Share Your Results
- **Export data** from Google Sheets for presentations
- **Share reports** with stakeholders
- **Schedule automated updates** for regular insights

## Troubleshooting Your First Run

**Pipeline fails at data ingestion:**
- Check internet connection for Chicago Open Data access
- Verify API endpoints in `configs/datasets.yaml`

**Google Sheets not updating:**
- Confirm service account has edit access to your Sheet
- Check `SHEET_ID` in `.env` file

**Great Expectations validation fails:**
- Review data quality issues in the output
- Check if source data format changed
- Run with fallback: `make run` (automatically falls back)

**Missing reports:**
- Ensure `reports/` directory exists
- Check write permissions
- Verify Markdown generation in Step 5

## Understanding the Output

### Data Quality Metrics
```
📊 VALIDATION RESULTS:
   Business Licenses: 95% validation success (23/25 expectations)
   Building Permits: 90% validation success (18/20 expectations) 
   CTA Boardings: 98% validation success (8/8 expectations)
```

### Transformation Summary
```
🔧 DATA TRANSFORMATIONS:
   ✅ 6 fields converted to proper numeric types
   ✅ 4 fields converted to datetime
   ✅ 8 business rules applied
   ✅ Geographic bounds validation applied
```

Congratulations! You've successfully run your first Chicago SMB Market Radar analysis. The system is now processing Chicago's business data and generating insights automatically.