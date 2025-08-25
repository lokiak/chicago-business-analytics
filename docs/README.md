# Chicago SMB Market Radar - Documentation

## Overview
This project integrates Chicago's open data sources (Socrata) with business analytics to provide insights into small and medium business market trends.

## Project Structure
```
chicago-smb-market-radar/
├── src/                    # Source code
│   ├── main.py            # Main execution script
│   ├── socrata.py         # Socrata API client
│   ├── sheets.py          # Google Sheets integration
│   ├── config.py          # Configuration management
│   ├── transform.py       # Data transformation utilities
│   ├── brief.py           # Report generation
│   └── logging_setup.py   # Logging configuration
├── configs/                # Configuration files
│   ├── datasets.yaml      # Dataset definitions
│   └── category_map.csv   # Business category mappings
├── data/                   # Data storage
├── reports/                # Generated reports
└── docs/                   # This documentation
    ├── README.md          # This file
    └── 2025/              # Developer logs by year
        └── 08/            # Developer logs by month
            └── 25.md      # Developer log for August 25, 2025
```

## Key Components

### Data Sources
- **Business Licenses**: Chicago business license data (r5kz-chrr)
- **Building Permits**: Chicago building permit data (ydr8-5enu)
- **CTA Boardings**: Chicago Transit Authority ridership data (6iiy-9s97)

### Output Destinations
- **Google Sheets**: Primary data export destination
- **Local JSON**: Raw data backup in data/raw/
- **Reports**: Markdown briefs in reports/

## Workflow
1. **Data Fetching**: Retrieve data from Socrata APIs
2. **Data Processing**: Clean and validate datasets
3. **Data Export**: Write to Google Sheets and local storage
4. **Report Generation**: Create business intelligence briefs

## Configuration
- **Settings**: Environment variables and configuration
- **Dataset Mapping**: Field mappings for each data source
- **Google Sheets**: Authentication and sheet configuration

## Development Logs
Developer logs are organized by date in `docs/YYYY/MM/DD.md` format, documenting:
- Code changes and refactoring
- Bug fixes and improvements
- New features and enhancements
- API changes and data source updates

## Getting Started
1. Set up environment variables
2. Configure Google Sheets credentials
3. Update dataset configurations as needed
4. Run `python -m src.main`

## Recent Updates
See the latest developer logs for recent changes and improvements.
