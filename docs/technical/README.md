# Technical Reference

Detailed technical documentation for developers and advanced users of the Chicago SMB Market Radar project.

## 📋 Technical Documentation

### Core Components
- **[API Reference](api-reference.md)** - Complete code documentation and function references
- **[Data Schema & Validation](schema-validation.md)** - Dataset schemas, validation rules, and data models
- **[Migration Guides](migration-guides.md)** - Version upgrade paths and breaking changes
- **[Troubleshooting](troubleshooting.md)** - Common issues, error messages, and solutions

### Architecture Overview

```
Chicago SMB Market Radar
├── Data Ingestion Layer (Step 2)
│   ├── Socrata API Client
│   ├── Schema Validation  
│   └── Error Handling
├── Transform Layer (Step 3)
│   ├── Great Expectations Framework
│   ├── Pattern-based Cleaning
│   └── Business Rule Engine
├── Validation Layer (Step 4)
│   ├── Data Quality Checks
│   ├── Expectation Suites
│   └── Quality Reporting
└── Output Layer (Step 5-6)
    ├── Google Sheets Integration
    ├── Report Generation
    └── Automation Framework
```

## 🔧 System Requirements

### Minimum Requirements
- **Python**: 3.8+
- **Memory**: 4GB RAM
- **Storage**: 2GB free space
- **Network**: Internet access for Chicago Open Data Portal

### Recommended Requirements  
- **Python**: 3.11+
- **Memory**: 8GB RAM
- **Storage**: 5GB free space
- **CPU**: Multi-core processor for parallel processing

### Dependencies
- **Core**: pandas, numpy, requests, python-dateutil
- **Data Quality**: great-expectations>=0.18.0
- **Google Integration**: gspread, google-auth
- **Utilities**: PyYAML, python-dotenv, markdown

## 🏗️ Architecture Components

### Data Ingestion (`step2_data_ingestion/`)
```python
# Key components
socrata_client.py         # Chicago Open Data API client
config_manager.py         # Configuration management
schema.py                 # Data schema definitions  
geographic_data_integration.py  # Geographic data processing
```

### Data Transformation (`step3_transform_model/`)
```python
# Great Expectations integration
gx_data_cleaning.py       # Smart cleaning framework
desired_schema.py         # Target schema definitions
expectation_suites.py     # Validation rule sets
pipeline_integration.py   # Integration layer
```

### Shared Utilities (`shared/`)
```python  
sheets_client.py          # Google Sheets integration
utils.py                  # Common utilities
constants.py              # Project constants
logging_setup.py          # Logging configuration
```

## 🔍 Data Flow

### 1. Data Ingestion
```
Chicago Open Data → Socrata API → Raw DataFrames → Schema Validation
```

### 2. Data Transformation  
```
Raw Data → Pattern Detection → Type Conversion → Business Rules → Clean Data
```

### 3. Data Validation
```
Clean Data → Expectation Suites → Quality Metrics → Validation Report
```

### 4. Data Output
```
Validated Data → Google Sheets → Reports → Automated Briefings
```

## 📊 Data Models

### Business Licenses Schema
```python
{
    "id": "string",              # Primary key
    "license_start_date": "datetime",  # Critical for analysis
    "community_area": "Int64",   # 1-77, Chicago areas
    "license_description": "category",  # Business type
    "latitude": "float64",       # Chicago bounds: 41.6-42.1
    "longitude": "float64"       # Chicago bounds: -87.9--87.5
}
```

### Building Permits Schema
```python
{
    "permit_": "string",         # Primary key
    "issue_date": "datetime",    # Critical for analysis
    "total_fee": "currency",     # Monetary amount
    "work_type": "category",     # Permit category
    "community_area": "Int64"    # Geographic reference
}
```

## 🔒 Security Considerations

### API Access
- Chicago Open Data Portal uses public APIs (no authentication required)
- Rate limiting handled automatically with retries
- HTTPS connections enforced

### Google Sheets Integration
- Service account authentication (recommended)
- JSON credentials file (keep secure)
- Minimal required permissions (Sheets API only)

### Data Privacy
- All Chicago data is public domain
- No personal information processed
- Aggregated analysis only

## 📈 Performance Characteristics

### Processing Times (typical dataset sizes)
- **Business Licenses** (2,000 records): ~30 seconds
- **Building Permits** (8,000 records): ~45 seconds  
- **CTA Boardings** (600 records): ~15 seconds
- **Complete Pipeline**: ~2-3 minutes

### Memory Usage
- **Peak memory**: ~500MB during processing
- **Persistent memory**: ~100MB for caching
- **Google Sheets**: Minimal overhead

### Optimization Tips
- Use `head()` parameter for testing with smaller datasets
- Enable caching for repeated analysis  
- Process datasets individually for large volumes
- Monitor memory usage with `pandas.info()`

## 🔬 Testing Framework

### Unit Tests
```bash
# Run unit tests (when implemented)
python -m pytest tests/

# Test specific modules
python -m pytest tests/test_data_ingestion.py
```

### Integration Tests
```bash
# Test end-to-end pipeline
make run-step2
make run-step3  
make run-step4
```

### Data Quality Tests
```bash
# Run Great Expectations validation
python -c "
from step3_transform_model.gx_data_cleaning import SmartDataCleaner
cleaner = SmartDataCleaner()
# Validation runs automatically during cleaning
"
```

## 🛠️ Development Setup

### Development Environment
```bash
# Install development dependencies
pip install -r requirements.txt
pip install jupyter pytest black flake8

# Set up pre-commit hooks (optional)
pre-commit install
```

### Code Style
- **Formatting**: Black (automatic formatting)
- **Linting**: Flake8 (code quality)
- **Type hints**: Encouraged but not required
- **Docstrings**: Google style

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality  
4. Update documentation
5. Submit pull request

See [Contributing Guidelines](../about/contributing.md) for detailed information.

---

**🔍 Need more specific information?** Check the individual reference documents or explore the source code with detailed inline documentation.