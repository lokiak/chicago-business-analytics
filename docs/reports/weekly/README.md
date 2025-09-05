# Weekly Reports

Automated weekly business intelligence reports generated from Chicago's open data.

## Available Reports

### Recent Reports
- [Week 35 (2025)](brief_2025-W35.md) - Latest weekly summary
- [Week 34 (2025)](brief_2025-W34.md) - Previous week analysis

## Report Format

Each weekly report contains:

- **Executive Summary** - Key metrics and trends
- **Business License Activity** - New licenses and patterns
- **Geographic Analysis** - Community area insights
- **Trend Analysis** - Week-over-week changes
- **Data Quality Metrics** - Validation results

## Automated Generation

Weekly reports are automatically generated every Monday at 6:00 AM CT using GitHub Actions. The process:

1. Fetches latest data from Chicago Open Data Portal
2. Runs data quality validation with Great Expectations
3. Performs trend analysis and calculations
4. Generates markdown report with key insights
5. Updates Google Sheets dashboard

## Archive

Reports are archived by week number and year for historical analysis and trend tracking.