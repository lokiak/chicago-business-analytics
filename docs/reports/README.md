# Reports & Analysis

Generated reports, analysis notebooks, and insights from Chicago's SMB data.

## 📊 Available Reports

### Weekly Reports
Automated weekly briefs analyzing Chicago SMB activity:

- **[Latest Weekly Report](weekly/)** - Most recent analysis
- **[Historical Reports](weekly/)** - Archive of past reports
- **[Report Generation Guide](../guides/custom-reports.md)** - Create your own reports

### Analysis Notebooks
Interactive Jupyter notebooks for deep-dive analysis:

- **[Data Exploration](analysis/)** - Initial data investigation
- **[Business Intelligence Analysis](analysis/)** - Strategic insights
- **[Geographic Analysis](analysis/)** - Spatial patterns and trends
- **[Time Series Analysis](analysis/)** - Temporal trends and forecasting

## 🎯 Key Insights Dashboard

### Recent Findings

**Business License Trends:**
- 📈 New licenses up 12% week-over-week
- 🏪 Restaurant/retail leading new business categories
- 🗺️ Loop and River North showing highest activity

**Building Permit Activity:**
- 🏗️ Construction permits increased 8% this month
- 💰 Total permit fees: $2.3M this quarter
- 📍 South Side showing increased development activity

**Economic Indicators:**
- 🚇 CTA ridership correlates with business license issuance
- 📊 Weekend ridership patterns predict Monday business activity
- 🏙️ Community area 8 (Near North) leads in business density

## 📅 Report Schedule

### Automated Generation
- **Daily**: CTA ridership updates
- **Weekly**: Business license summary (Mondays at 6 AM CT)
- **Monthly**: Comprehensive analysis report
- **Quarterly**: Strategic insights and trend analysis

### Manual Reports
- **Ad-hoc Analysis**: Custom date ranges and filters  
- **Stakeholder Reports**: Executive summaries
- **Deep Dive Studies**: Specific business sectors or geographic areas

## 📈 Report Types

### 1. Executive Briefings
**Purpose**: High-level insights for decision makers
**Format**: Markdown with key metrics and visualizations
**Frequency**: Weekly
**Example**: [Weekly Brief W35](weekly/brief_2025-W35.md)

### 2. Technical Analysis  
**Purpose**: Detailed data analysis for analysts
**Format**: Jupyter notebooks with code and commentary
**Frequency**: On-demand
**Example**: [Business Analysis Notebook](analysis/)

### 3. Geographic Reports
**Purpose**: Community area and ward-level insights
**Format**: Maps and geographic visualizations
**Frequency**: Monthly
**Example**: [Geographic Analysis Guide](../guides/geographic-data.md)

### 4. Trend Reports
**Purpose**: Time series analysis and forecasting
**Format**: Charts, trend lines, and statistical analysis
**Frequency**: Quarterly
**Tools**: Python, pandas, matplotlib/plotly

## 🔍 Report Insights

### Business Intelligence Metrics

**Growth Indicators:**
- New business license applications
- Permit volume and value trends
- Geographic expansion patterns
- Seasonal variations

**Economic Health:**
- Business closure/renewal rates
- Construction investment levels
- Employment proxy indicators
- Public transit usage correlation

**Geographic Analysis:**
- Community area business density
- Ward-level development activity
- Transportation accessibility impact
- Demographic correlation analysis

## 📊 Data Visualizations

### Standard Chart Types
- **Time Series**: License trends over time
- **Geographic Maps**: Community area heat maps  
- **Bar Charts**: Business category breakdowns
- **Scatter Plots**: Correlation analysis

### Interactive Dashboards
- **Business Activity Dashboard**: Real-time metrics
- **Geographic Explorer**: Interactive maps
- **Trend Analyzer**: Custom date range analysis
- **Comparison Tool**: Before/after analysis

## 🛠️ Creating Custom Reports

### Quick Custom Analysis
```python
# Load the latest cleaned data
import pandas as pd
from shared.sheets_client import load_sheet_data

# Access cleaned data
licenses_df = pd.read_pickle('data/processed/licenses_df_cleaned.pkl')

# Create your custom analysis
custom_analysis = licenses_df.groupby('community_area_name').size()
print(custom_analysis.head(10))
```

### Advanced Report Generation
1. **Use Report Templates**: Start with existing notebook templates
2. **Follow Naming Conventions**: `report_YYYY-MM-DD_topic.md`
3. **Include Metadata**: Date range, data sources, methodology
4. **Add Visualizations**: Charts, maps, and summary tables
5. **Provide Context**: Business implications and recommendations

### Automated Report Pipeline
```bash
# Generate weekly report
python scripts/generate_weekly_report.py

# Create custom date range report  
python scripts/generate_custom_report.py --start 2025-01-01 --end 2025-01-31

# Export to multiple formats
python scripts/export_report.py --format pdf,html,excel
```

## 📋 Report Archive

### 2025 Reports
- **Week 35**: [Business Activity Summary](weekly/brief_2025-W35.md)
- **Week 34**: [Monthly Review](weekly/brief_2025-W34.md)
- **[Full Archive](weekly/)**: Complete historical reports

### Analysis Studies
- **Q3 2025**: Geographic Business Distribution Analysis
- **Q2 2025**: Post-COVID Business Recovery Patterns
- **Q1 2025**: Construction Permit Trend Analysis

## 🎯 Using Reports

### For Business Stakeholders
- **Executive Summary**: Key metrics and trends
- **Geographic Insights**: Area-specific opportunities
- **Competitive Analysis**: Market positioning data

### For City Planners
- **Development Patterns**: Construction and business trends  
- **Economic Indicators**: Business health metrics
- **Resource Planning**: Service demand forecasting

### For Researchers
- **Raw Data Access**: Cleaned datasets for analysis
- **Methodology Documentation**: Reproducible analysis
- **Statistical Validation**: Data quality metrics

## 📬 Report Distribution

### Automated Distribution
- **Stakeholder Email**: Weekly summaries via automated system
- **Google Sheets**: Live dashboards with real-time data
- **Web Dashboard**: Interactive online reports

### Manual Sharing
- **PDF Export**: Professional reports for presentations
- **Excel Export**: Data for further analysis
- **Interactive Notebooks**: Jupyter notebooks for technical users

---

**📌 Need a specific report or analysis?** Check our [Custom Reports Guide](../guides/custom-reports.md) or explore the [Technical Reference](../technical/) for advanced analysis techniques.