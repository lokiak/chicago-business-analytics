# Chicago SMB Market Radar — Restructuring Plan

## Overview

This document outlines the optimal restructuring of the Chicago SMB Market Radar project to align with the BI 0→1 Framework, creating a clear step-by-step flow that matches the framework stages.

## Current Issues

### 1. **Mixed Responsibilities**
- `src/` contains both ingestion (Step 2) and transformation (Step 3) logic
- No clear separation between framework steps
- Automation scripts are isolated from the main flow

### 2. **Unclear Flow**
- Hard to understand which files belong to which framework step
- No clear progression from one step to the next
- Notebooks don't clearly map to framework steps

### 3. **Scattered Components**
- Scripts, notebooks, and source code are in separate directories
- No unified entry point for each framework step
- Difficult to understand the complete workflow

## Proposed Structure

```
chicago-smb-market-radar/
├── docs/                          # Documentation (unchanged)
├── configs/                       # Configuration (unchanged)
├── data/                          # Data storage (unchanged)
├── reports/                       # Generated reports (unchanged)
│
├── step1_scope_strategy/          # ✅ COMPLETED
│   ├── README.md                  # Requirements, stakeholders, success metrics
│   ├── requirements.md            # Business requirements
│   ├── stakeholder_analysis.md    # User mapping
│   └── success_metrics.md         # KPI definitions
│
├── step2_data_ingestion/          # ✅ COMPLETED
│   ├── __init__.py
│   ├── socrata_client.py          # API client (from src/socrata.py)
│   ├── data_fetcher.py            # Data fetching logic (from src/main.py)
│   ├── config_manager.py          # Configuration (from src/config.py)
│   ├── pipeline.py                # Main ingestion pipeline
│   └── notebooks/
│       ├── 01_api_exploration.ipynb
│       └── 02_data_quality_check.ipynb
│
├── step3_transform_model/         # 🔄 PARTIALLY COMPLETED
│   ├── __init__.py
│   ├── transformers.py            # Data transformations (from src/transform.py)
│   ├── aggregators.py             # Weekly aggregations
│   ├── category_mapper.py         # Business category mapping
│   ├── trend_calculator.py        # Trend metrics and baselines
│   ├── pipeline.py                # Main transformation pipeline
│   └── notebooks/
│       ├── 01_data_transformation.ipynb
│       ├── 02_weekly_aggregations.ipynb
│       ├── 03_trend_analysis.ipynb
│       └── 04_business_metrics.ipynb
│
├── step4_load_validate/           # ❌ NOT STARTED
│   ├── __init__.py
│   ├── validators.py              # Data validation framework
│   ├── quality_monitor.py         # Data quality monitoring
│   ├── schema_validator.py        # Schema validation
│   ├── pipeline.py                # Main validation pipeline
│   └── notebooks/
│       ├── 01_data_validation.ipynb
│       └── 02_quality_assessment.ipynb
│
├── step5_visualize_report/        # ❌ NOT STARTED
│   ├── __init__.py
│   ├── dashboard_builder.py       # Dashboard creation
│   ├── report_generator.py        # Report generation (from src/brief.py)
│   ├── kpi_calculator.py          # Executive KPIs
│   ├── pipeline.py                # Main visualization pipeline
│   └── notebooks/
│       ├── 01_dashboard_design.ipynb
│       ├── 02_kpi_analysis.ipynb
│       └── 03_report_generation.ipynb
│
├── step6_automate_scale/          # ❌ NOT STARTED
│   ├── __init__.py
│   ├── scheduler.py               # Job scheduling
│   ├── monitor.py                 # System monitoring
│   ├── alerting.py                # Alert system
│   ├── pipeline.py                # Main automation pipeline
│   └── scripts/
│       ├── run_full_pipeline.py   # Complete pipeline execution
│       ├── health_check.py        # System health checks
│       └── setup_automation.py    # Automation setup
│
├── shared/                        # Shared utilities
│   ├── __init__.py
│   ├── logging_setup.py           # Logging (from src/logging_setup.py)
│   ├── sheets_client.py           # Google Sheets (from src/sheets.py)
│   ├── utils.py                   # Common utilities
│   └── constants.py               # Project constants
│
├── main.py                        # Main entry point
├── requirements.txt               # Dependencies
├── Makefile                       # Build automation
└── README.md                      # Project overview
```

## Migration Strategy

### Phase 1: Create New Structure (Week 1)
1. **Create directory structure**
2. **Move existing files to appropriate steps**
3. **Update imports and references**
4. **Test basic functionality**

### Phase 2: Implement Missing Components (Week 2-4)
1. **Complete Step 3 transformations**
2. **Implement Step 4 validation**
3. **Build Step 5 visualization**
4. **Set up Step 6 automation**

### Phase 3: Integration & Testing (Week 5-6)
1. **Integrate all steps**
2. **Test complete pipeline**
3. **Update documentation**
4. **Performance optimization**

## Benefits of This Structure

### 1. **Clear Framework Alignment**
- Each directory maps directly to a BI 0→1 Framework step
- Easy to understand what belongs where
- Clear progression from one step to the next

### 2. **Modular Development**
- Each step can be developed independently
- Easy to test individual components
- Clear separation of concerns

### 3. **Scalable Architecture**
- Easy to add new features to specific steps
- Clear entry points for each framework stage
- Unified pipeline execution

### 4. **Better Documentation**
- Each step has its own documentation
- Clear notebooks for each component
- Easy to understand the complete workflow

## Implementation Plan

### Step 1: Create Directory Structure
```bash
# Create the new directory structure
mkdir -p step1_scope_strategy
mkdir -p step2_data_ingestion/notebooks
mkdir -p step3_transform_model/notebooks
mkdir -p step4_load_validate/notebooks
mkdir -p step5_visualize_report/notebooks
mkdir -p step6_automate_scale/scripts
mkdir -p shared
```

### Step 2: Move Existing Files
```bash
# Move files to appropriate steps
mv src/socrata.py step2_data_ingestion/socrata_client.py
mv src/transform.py step3_transform_model/transformers.py
mv src/brief.py step5_visualize_report/report_generator.py
mv src/sheets.py shared/sheets_client.py
mv src/logging_setup.py shared/logging_setup.py
```

### Step 3: Update Imports
- Update all import statements
- Create proper `__init__.py` files
- Update main entry point

### Step 4: Implement Missing Components
- Complete transformation logic
- Add validation framework
- Build visualization components
- Set up automation

## Entry Points

### Individual Step Execution
```bash
# Run individual steps
python -m step2_data_ingestion.pipeline
python -m step3_transform_model.pipeline
python -m step4_load_validate.pipeline
python -m step5_visualize_report.pipeline
python -m step6_automate_scale.pipeline
```

### Complete Pipeline
```bash
# Run complete pipeline
python main.py --all

# Run specific steps
python main.py --steps 2,3,4
```

### Notebook Analysis
```bash
# Run step-specific notebooks
jupyter notebook step2_data_ingestion/notebooks/
jupyter notebook step3_transform_model/notebooks/
```

## Migration Checklist

### Phase 1: Structure Creation
- [ ] Create directory structure
- [ ] Move existing files
- [ ] Update imports
- [ ] Test basic functionality

### Phase 2: Component Implementation
- [ ] Complete Step 3 transformations
- [ ] Implement Step 4 validation
- [ ] Build Step 5 visualization
- [ ] Set up Step 6 automation

### Phase 3: Integration
- [ ] Integrate all steps
- [ ] Test complete pipeline
- [ ] Update documentation
- [ ] Performance optimization

## Conclusion

This restructuring will create a clear, maintainable, and scalable architecture that directly aligns with the BI 0→1 Framework. Each step will be self-contained with its own notebooks, documentation, and testing, making it easy to develop, test, and maintain individual components while maintaining a clear overall workflow.
