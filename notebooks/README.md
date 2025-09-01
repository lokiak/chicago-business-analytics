# Chicago SMB Market Radar — Analysis Notebooks

This directory contains Jupyter notebooks for analyzing Chicago small business data from the Google Sheets data warehouse.

## Notebook Structure

### 01_data_exploration.ipynb
**Purpose:** Initial data exploration and quality assessment
- Connect to Google Sheets data warehouse
- Load business licenses, building permits, and CTA data
- Perform data quality assessment
- Set up reusable analysis functions

### 02_business_analysis.ipynb
**Purpose:** Business intelligence and KPI analysis
- Analyze business license trends and patterns
- Identify high-growth neighborhoods and business types
- Calculate key performance indicators (KPIs)
- Generate actionable business insights

### 03_trend_analysis.ipynb (Planned)
**Purpose:** Time-series analysis and forecasting
- Weekly aggregations and trend calculations
- Seasonal analysis and pattern recognition
- Momentum indices and growth metrics
- Predictive modeling for business trends

### 04_geographic_analysis.ipynb (Planned)
**Purpose:** Geographic and neighborhood analysis
- Community area performance analysis
- Geographic clustering and hotspots
- Neighborhood comparison metrics
- Spatial correlation analysis

### 05_executive_dashboard.ipynb (Planned)
**Purpose:** Executive summary and dashboard preparation
- Executive KPI calculations
- Summary statistics and key metrics
- Dashboard data preparation
- Report generation

## Utility Functions

### utils.py
Contains reusable functions for all notebooks:
- Data loading and saving functions
- Data quality assessment tools
- Visualization helpers
- Statistical analysis functions
- Time series analysis utilities

## Getting Started

1. **Prerequisites:**
   - Python 3.11+
   - Jupyter Notebook or JupyterLab
   - Required packages (see requirements.txt)
   - Google Sheets API credentials configured

2. **Environment Setup:**
   ```bash
   # Activate virtual environment
   source venv/bin/activate

   # Install additional notebook dependencies
   pip install jupyter matplotlib seaborn plotly

   # Start Jupyter
   jupyter notebook
   ```

3. **Running Analysis:**
   - Start with `01_data_exploration.ipynb` to load and explore data
   - Run `02_business_analysis.ipynb` for detailed business insights
   - Use subsequent notebooks for specialized analysis

## Data Flow

```
Google Sheets (Data Warehouse)
    ↓
01_data_exploration.ipynb (Load & Explore)
    ↓
02_business_analysis.ipynb (Business Intelligence)
    ↓
03_trend_analysis.ipynb (Time Series)
    ↓
04_geographic_analysis.ipynb (Spatial Analysis)
    ↓
05_executive_dashboard.ipynb (Executive Summary)
```

## Key Features

- **Automated Data Loading:** Functions to load data from Google Sheets
- **Data Quality Assessment:** Comprehensive data quality checks
- **Reusable Functions:** Common analysis functions in utils.py
- **Performance Optimization:** Pickle file caching for faster loading
- **Visualization:** Consistent plotting styles and themes
- **Documentation:** Comprehensive docstrings and comments

## Best Practices

1. **Data Loading:** Always try to load from pickle files first for performance
2. **Error Handling:** Use try-except blocks for robust data loading
3. **Documentation:** Document insights and findings in markdown cells
4. **Reproducibility:** Set random seeds for consistent results
5. **Performance:** Use vectorized operations and avoid loops when possible

## Troubleshooting

### Common Issues

1. **Google Sheets Connection Error:**
   - Check .env file configuration
   - Verify Google credentials path
   - Ensure sheet ID is correct

2. **Import Errors:**
   - Make sure virtual environment is activated
   - Check that all required packages are installed
   - Verify Python path includes src directory

3. **Data Loading Issues:**
   - Check worksheet names in Google Sheets
   - Verify column names match expected format
   - Check for data type inconsistencies

### Getting Help

- Check the main project README.md for setup instructions
- Review the BI_FRAMEWORK_STRATEGIC_PLAN.md for project context
- Examine the src/ directory for core functionality
- Check logs for detailed error messages

## Contributing

When adding new notebooks:
1. Follow the naming convention: `##_descriptive_name.ipynb`
2. Include comprehensive markdown documentation
3. Use functions from utils.py when possible
4. Add data quality checks and error handling
5. Document key insights and findings
6. Update this README with new notebook descriptions
