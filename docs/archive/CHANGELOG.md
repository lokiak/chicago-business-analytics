# Chicago SMB Market Radar - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation structure in `docs/` folder
- Developer logs organized by year/month/day
- Technical reference documentation
- Workflow documentation
- Changelog tracking

### Changed
- **BREAKING**: Complete refactoring of data pipeline
- **BREAKING**: Removed weekly aggregation functionality
- **BREAKING**: Simplified data processing pipeline

### Deprecated
- Weekly aggregation functions (`daily_to_weekly`, `add_baselines`)
- License normalization and category mapping
- Momentum analysis and baseline calculations

### Removed
- GROUP BY constraints from Socrata queries
- Complex weekly analysis logic
- Unused import dependencies
- Legacy transformation utilities

### Fixed
- Socrata API GROUP BY constraint violations
- SQL query syntax errors
- Import dependency issues

### Security
- No security changes in this release

## [1.0.0] - 2025-08-25

### Added
- Initial project setup
- Socrata API integration for Chicago open data
- Google Sheets export functionality
- Business licenses data fetching (r5kz-chrr)
- Building permits data fetching (ydr8-5enu)
- CTA ridership data fetching (6iiy-9s97)
- Weekly data aggregation and analysis
- Business intelligence brief generation
- Local data backup and storage
- Comprehensive logging and error handling

### Technical Features
- Automatic pagination handling for large datasets
- Exponential backoff retry logic for API failures
- Dynamic Google Sheets worksheet creation
- Column formatting and styling automation
- Data validation and quality checks
- Configuration management via YAML files
- Environment variable configuration support

### Data Sources
- **Business Licenses**: Chicago business license information
- **Building Permits**: Chicago building permit data
- **CTA Boardings**: Chicago Transit Authority ridership data

### Output Destinations
- Google Sheets with multiple worksheet tabs
- Local JSON backup files
- Markdown business intelligence briefs
- Comprehensive logging output

---

## Version History

### Version 1.0.0 (Initial Release)
- **Release Date**: August 25, 2025
- **Status**: Initial development version
- **Features**: Complete data pipeline with weekly aggregation

### Version 2.0.0 (Refactored Release)
- **Release Date**: August 25, 2025
- **Status**: Major refactoring
- **Features**: Simplified pipeline, expanded data fields, no weekly aggregation

---

## Migration Guide

### From Version 1.0.0 to 2.0.0

#### Breaking Changes
1. **Weekly Aggregation Removed**: The system no longer generates weekly aggregated data
2. **Data Processing Simplified**: Complex transformations and analysis removed
3. **Output Structure Changed**: New Google Sheets tabs for full datasets

#### Data Access Changes
- **Before**: Weekly aggregated data in `Licenses_Weekly`, `Permits_Weekly`, `CTA_Weekly`
- **After**: Full datasets in `Business_Licenses_Full`, `Building_Permits_Full`, `CTA_Full`

#### Configuration Updates
- **Removed**: `BASELINE_WEEKS` environment variable (no longer used)
- **Maintained**: All other environment variables remain the same

#### Code Changes Required
- **Weekly Analysis**: If you depend on weekly aggregated data, you'll need to implement this in your analysis tools
- **Data Processing**: If you need data transformations, implement them after data export
- **Reports**: Update any systems that depend on the weekly brief generation

---

## Future Roadmap

### Version 2.1.0 (Planned)
- Data validation and quality checks
- Schema validation for field availability
- Enhanced error handling and notifications
- Performance monitoring and metrics

### Version 2.2.0 (Planned)
- Incremental data updates
- Data lineage tracking
- Advanced filtering and query options
- Real-time data processing capabilities

### Version 3.0.0 (Long-term)
- Multiple data source support
- Distributed processing capabilities
- Advanced analytics and machine learning
- Real-time dashboard and alerts

---

## Contributing

When contributing to this project, please:

1. **Update this changelog** with your changes
2. **Follow the existing format** for entries
3. **Use clear, descriptive language** for changes
4. **Include breaking changes** in the appropriate section
5. **Reference issue numbers** when applicable

### Changelog Entry Format
```markdown
### Added
- New feature description

### Changed
- Change description

### Deprecated
- Deprecated feature description

### Removed
- Removed feature description

### Fixed
- Bug fix description

### Security
- Security-related change description
```

---

## Support

For questions about this changelog or the project:

- **Documentation**: See `docs/` folder for comprehensive guides
- **Developer Logs**: Check `docs/YYYY/MM/DD.md` for recent changes
- **Issues**: Report bugs or request features through the project's issue tracker
- **Contributions**: Follow the contributing guidelines for code changes
