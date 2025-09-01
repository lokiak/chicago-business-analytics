# Chicago SMB Market Radar — Migration Guide

## Overview

This guide walks you through migrating your current project structure to align with the BI 0→1 Framework, creating a clear step-by-step flow.

## Why Restructure?

### Current Issues
- **Mixed Responsibilities:** `src/` contains both ingestion and transformation logic
- **Unclear Flow:** No clear separation between framework steps
- **Scattered Scripts:** Automation scripts are separate from the main flow
- **Notebook Isolation:** Analysis notebooks don't clearly map to framework steps

### Benefits of New Structure
- **Clear Framework Alignment:** Each directory maps directly to a BI 0→1 Framework step
- **Modular Development:** Each step can be developed independently
- **Scalable Architecture:** Easy to add new features to specific steps
- **Better Documentation:** Each step has its own documentation and notebooks

## Migration Options

### Option 1: Automated Migration (Recommended)
Use the provided restructuring script for a safe, automated migration:

```bash
# Run the restructuring script
python scripts/restructure_project.py
```

### Option 2: Manual Migration
Follow the step-by-step manual process outlined below.

## Automated Migration Process

### Step 1: Backup Your Project
```bash
# Create a backup of your current project
cp -r chicago-smb-market-radar chicago-smb-market-radar-backup
```

### Step 2: Run the Restructuring Script
```bash
# Run the automated restructuring
python scripts/restructure_project.py
```

### Step 3: Verify the New Structure
```bash
# Check the new directory structure
tree -L 3

# Test the new entry point
python main.py --help
```

### Step 4: Update Your Workflow
```bash
# Use the new Makefile commands
make help

# Run individual steps
make run-step2  # Data ingestion
make run-step3  # Transform & model
```

## Manual Migration Process

### Step 1: Create Directory Structure
```bash
# Create the new BI 0→1 Framework directories
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
# Move files to their appropriate BI framework steps
mv src/socrata.py step2_data_ingestion/socrata_client.py
mv src/transform.py step3_transform_model/transformers.py
mv src/brief.py step5_visualize_report/report_generator.py
mv src/sheets.py shared/sheets_client.py
mv src/logging_setup.py shared/logging_setup.py
mv src/utils.py shared/utils.py

# Move notebooks
mv notebooks/01_data_exploration.ipynb step2_data_ingestion/notebooks/01_api_exploration.ipynb
mv notebooks/02_business_analysis.ipynb step3_transform_model/notebooks/01_data_transformation.ipynb
mv notebooks/utils.py shared/notebook_utils.py

# Move scripts
mv scripts/automated_analysis.py step6_automate_scale/scripts/run_full_pipeline.py
mv scripts/monitor_automation.py step6_automate_scale/scripts/health_check.py
```

### Step 3: Create __init__.py Files
```bash
# Create __init__.py files for Python modules
touch step2_data_ingestion/__init__.py
touch step3_transform_model/__init__.py
touch step4_load_validate/__init__.py
touch step5_visualize_report/__init__.py
touch step6_automate_scale/__init__.py
touch shared/__init__.py
```

### Step 4: Update Import Statements
Update all import statements in moved files to reflect the new structure:

```python
# Old imports
from src.socrata import SocrataClient
from src.sheets import open_sheet

# New imports
from step2_data_ingestion.socrata_client import SocrataClient
from shared.sheets_client import open_sheet
```

### Step 5: Create Main Entry Point
Create a new `main.py` file that orchestrates all BI framework steps:

```python
#!/usr/bin/env python3
"""
Chicago SMB Market Radar - Main Entry Point
"""

import argparse
import sys

def run_step(step_number: int):
    """Run a specific BI framework step."""
    # Implementation details in the restructuring script
    pass

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Chicago SMB Market Radar - BI 0→1 Framework")
    parser.add_argument("--steps", type=str, help="Comma-separated list of steps to run")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    parser.add_argument("--step", type=int, help="Run a specific step (1-6)")

    args = parser.parse_args()
    # Implementation details in the restructuring script

if __name__ == "__main__":
    sys.exit(main())
```

## New Project Structure

After migration, your project will have this structure:

```
chicago-smb-market-radar/
├── step1_scope_strategy/          # ✅ COMPLETED
├── step2_data_ingestion/          # ✅ COMPLETED
│   ├── socrata_client.py
│   ├── config_manager.py
│   └── notebooks/
├── step3_transform_model/         # 🔄 PARTIALLY COMPLETED
│   ├── transformers.py
│   └── notebooks/
├── step4_load_validate/           # ❌ NOT STARTED
├── step5_visualize_report/        # ❌ NOT STARTED
├── step6_automate_scale/          # ❌ NOT STARTED
│   └── scripts/
├── shared/                        # Shared utilities
│   ├── sheets_client.py
│   ├── logging_setup.py
│   └── constants.py
├── main.py                        # Main entry point
├── Makefile                       # Updated build automation
└── docs/                          # Documentation
```

## Usage After Migration

### Running Individual Steps
```bash
# Run specific steps
python main.py --step 2  # Data ingestion
python main.py --step 3  # Transform & model
python main.py --steps 2,3,4  # Multiple steps

# Using Makefile
make run-step2
make run-step3
```

### Running Complete Pipeline
```bash
# Run all steps
python main.py --all
make run
```

### Working with Notebooks
```bash
# Step-specific notebooks
jupyter notebook step2_data_ingestion/notebooks/
jupyter notebook step3_transform_model/notebooks/
```

## Post-Migration Tasks

### 1. Update Documentation
- Update README.md to reflect new structure
- Update any internal documentation
- Update CI/CD configurations

### 2. Test Functionality
```bash
# Test each step individually
python main.py --step 2
python main.py --step 3

# Test complete pipeline
python main.py --all
```

### 3. Implement Missing Components
Focus on completing the partially implemented steps:

- **Step 3:** Complete transformation logic
- **Step 4:** Implement validation framework
- **Step 5:** Build visualization components
- **Step 6:** Set up automation

### 4. Update Development Workflow
- Update your IDE configurations
- Update any scripts that reference old paths
- Update team documentation

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check that all `__init__.py` files are created
   - Verify import paths in moved files
   - Update any hardcoded paths

2. **Missing Dependencies**
   - Ensure all required packages are installed
   - Check that shared utilities are accessible

3. **Path Issues**
   - Update any hardcoded file paths
   - Check that data directories are accessible

### Rollback Plan
If you need to rollback:

```bash
# Restore from backup
rm -rf chicago-smb-market-radar
mv chicago-smb-market-radar-backup chicago-smb-market-radar
```

## Benefits After Migration

### 1. Clear Framework Alignment
- Each directory maps directly to a BI 0→1 Framework step
- Easy to understand what belongs where
- Clear progression from one step to the next

### 2. Modular Development
- Each step can be developed independently
- Easy to test individual components
- Clear separation of concerns

### 3. Better Documentation
- Each step has its own documentation
- Clear notebooks for each component
- Easy to understand the complete workflow

### 4. Scalable Architecture
- Easy to add new features to specific steps
- Clear entry points for each framework stage
- Unified pipeline execution

## Next Steps

After successful migration:

1. **Complete Step 3:** Implement missing transformation logic
2. **Build Step 4:** Add data validation framework
3. **Create Step 5:** Build visualization components
4. **Set up Step 6:** Implement automation and monitoring

The new structure provides a solid foundation for completing the remaining BI 0→1 Framework steps and scaling the project effectively.
