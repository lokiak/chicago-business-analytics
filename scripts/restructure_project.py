#!/usr/bin/env python3
"""
Chicago SMB Market Radar - Project Restructuring Script

This script restructures the project to align with the BI 0→1 Framework,
creating a clear step-by-step flow that matches the framework stages.
"""

import os
import shutil
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create the new BI 0→1 Framework directory structure."""
    logger.info("🏗️ Creating BI 0→1 Framework directory structure...")

    directories = [
        "step1_scope_strategy",
        "step2_data_ingestion/notebooks",
        "step3_transform_model/notebooks",
        "step4_load_validate/notebooks",
        "step5_visualize_report/notebooks",
        "step6_automate_scale/scripts",
        "shared"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

    # Create __init__.py files
    init_files = [
        "step2_data_ingestion/__init__.py",
        "step3_transform_model/__init__.py",
        "step4_load_validate/__init__.py",
        "step5_visualize_report/__init__.py",
        "step6_automate_scale/__init__.py",
        "shared/__init__.py"
    ]

    for init_file in init_files:
        Path(init_file).touch()
        logger.info(f"✅ Created __init__.py: {init_file}")

def move_existing_files():
    """Move existing files to their appropriate BI framework steps."""
    logger.info("📁 Moving existing files to BI framework steps...")

    # File mappings: (source, destination, description)
    file_mappings = [
        # Step 2: Data Ingestion
        ("src/socrata.py", "step2_data_ingestion/socrata_client.py", "Socrata API client"),
        ("src/config.py", "step2_data_ingestion/config_manager.py", "Configuration management"),

        # Step 3: Transform & Model
        ("src/transform.py", "step3_transform_model/transformers.py", "Data transformations"),

        # Step 5: Visualize & Report
        ("src/brief.py", "step5_visualize_report/report_generator.py", "Report generation"),

        # Shared utilities
        ("src/sheets.py", "shared/sheets_client.py", "Google Sheets client"),
        ("src/logging_setup.py", "shared/logging_setup.py", "Logging setup"),
        ("src/utils.py", "shared/utils.py", "Common utilities"),

        # Notebooks
        ("notebooks/01_data_exploration.ipynb", "step2_data_ingestion/notebooks/01_api_exploration.ipynb", "API exploration notebook"),
        ("notebooks/02_business_analysis.ipynb", "step3_transform_model/notebooks/01_data_transformation.ipynb", "Data transformation notebook"),
        ("notebooks/utils.py", "shared/notebook_utils.py", "Notebook utilities"),

        # Scripts
        ("scripts/automated_analysis.py", "step6_automate_scale/scripts/run_full_pipeline.py", "Full pipeline execution"),
        ("scripts/monitor_automation.py", "step6_automate_scale/scripts/health_check.py", "Health check script"),
    ]

    for source, destination, description in file_mappings:
        if Path(source).exists():
            # Create destination directory if it doesn't exist
            Path(destination).parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(source, destination)
            logger.info(f"✅ Moved {description}: {source} → {destination}")
        else:
            logger.warning(f"⚠️ Source file not found: {source}")

def create_step_readmes():
    """Create README files for each BI framework step."""
    logger.info("📝 Creating README files for each BI framework step...")

    step_readmes = {
        "step1_scope_strategy/README.md": """# Step 1: Scope & Strategy

## Status: ✅ COMPLETED

This step defines the business requirements, stakeholder needs, and success metrics.

### Components
- Business requirements definition
- Stakeholder mapping
- Success metrics establishment
- Technical scope documentation

### Documentation
- See `docs/BI_FRAMEWORK_STRATEGIC_PLAN.md` for complete details
- Business requirements are documented in the main README.md

### Next Steps
This step is complete. Proceed to Step 2: Data Ingestion.
""",

        "step2_data_ingestion/README.md": """# Step 2: Data Ingestion

## Status: ✅ COMPLETED

This step handles data extraction from Chicago Open Data Portal via Socrata API.

### Components
- `socrata_client.py` - Socrata API client with error handling
- `config_manager.py` - Configuration management
- `pipeline.py` - Main ingestion pipeline
- `notebooks/` - Data exploration and quality assessment

### Usage
```bash
# Run data ingestion
python -m step2_data_ingestion.pipeline

# Explore data
jupyter notebook step2_data_ingestion/notebooks/
```

### Data Sources
- Business Licenses (r5kz-chrr)
- Building Permits (ydr8-5enu)
- CTA Boardings (6iii-9s97)

### Next Steps
Proceed to Step 3: Transform & Model.
""",

        "step3_transform_model/README.md": """# Step 3: Transform & Model

## Status: 🔄 PARTIALLY COMPLETED

This step transforms raw data into analysis-ready business metrics.

### Components
- `transformers.py` - Data transformations (existing)
- `aggregators.py` - Weekly aggregations (to be implemented)
- `category_mapper.py` - Business category mapping (to be implemented)
- `trend_calculator.py` - Trend metrics and baselines (to be implemented)
- `pipeline.py` - Main transformation pipeline (to be implemented)
- `notebooks/` - Transformation analysis notebooks

### Current Status
- ✅ Raw data extraction and storage
- ✅ Basic data flattening
- ❌ Weekly aggregations by community area
- ❌ Business category mapping
- ❌ Trend analysis (WoW, momentum indices)
- ❌ Baseline calculations (13-week rolling averages)

### Next Steps
1. Implement weekly aggregation functions
2. Add business category mapping
3. Calculate trend metrics and baselines
4. Test transformation pipeline
""",

        "step4_load_validate/README.md": """# Step 4: Load & Validate

## Status: ❌ NOT STARTED

This step implements data validation and quality monitoring.

### Components (To Be Implemented)
- `validators.py` - Data validation framework
- `quality_monitor.py` - Data quality monitoring
- `schema_validator.py` - Schema validation
- `pipeline.py` - Main validation pipeline
- `notebooks/` - Validation analysis notebooks

### Planned Implementation
- Great Expectations for data validation
- Automated data quality checks
- Schema validation
- Business rule validation

### Next Steps
1. Implement data validation framework
2. Add automated quality checks
3. Create monitoring alerts
4. Test error scenarios
""",

        "step5_visualize_report/README.md": """# Step 5: Visualize & Report

## Status: ❌ NOT STARTED

This step creates interactive dashboards and automated reports.

### Components (To Be Implemented)
- `dashboard_builder.py` - Dashboard creation
- `report_generator.py` - Report generation (moved from src/brief.py)
- `kpi_calculator.py` - Executive KPIs
- `pipeline.py` - Main visualization pipeline
- `notebooks/` - Visualization analysis notebooks

### Planned Implementation
- Looker Studio dashboard
- Automated report generation
- Executive KPI tracking
- Neighborhood-level drill-downs

### Next Steps
1. Design Looker Studio dashboard
2. Implement executive KPIs
3. Create neighborhood views
4. Test user experience
""",

        "step6_automate_scale/README.md": """# Step 6: Automate & Scale

## Status: ❌ NOT STARTED

This step implements automation, monitoring, and scaling capabilities.

### Components (To Be Implemented)
- `scheduler.py` - Job scheduling
- `monitor.py` - System monitoring
- `alerting.py` - Alert system
- `pipeline.py` - Main automation pipeline
- `scripts/` - Automation scripts

### Planned Implementation
- Scheduled data refresh
- Automated report generation
- Error handling and alerting
- Performance monitoring

### Next Steps
1. Implement scheduled automation
2. Add error handling and alerting
3. Set up performance monitoring
4. Test automation workflows
"""
    }

    for file_path, content in step_readmes.items():
        with open(file_path, 'w') as f:
            f.write(content)
        logger.info(f"✅ Created README: {file_path}")

def create_main_entry_point():
    """Create the main entry point that orchestrates all BI framework steps."""
    logger.info("🚀 Creating main entry point...")

    main_content = '''#!/usr/bin/env python3
"""
Chicago SMB Market Radar - Main Entry Point

This is the main entry point for the Chicago SMB Market Radar project,
orchestrating all BI 0→1 Framework steps.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add shared directory to path
sys.path.append(str(Path(__file__).parent / "shared"))

from logging_setup import setup_logger

logger = setup_logger()

def run_step(step_number: int):
    """Run a specific BI framework step."""
    step_modules = {
        1: "step1_scope_strategy",
        2: "step2_data_ingestion",
        3: "step3_transform_model",
        4: "step4_load_validate",
        5: "step5_visualize_report",
        6: "step6_automate_scale"
    }

    if step_number not in step_modules:
        logger.error(f"Invalid step number: {step_number}. Must be 1-6.")
        return False

    step_module = step_modules[step_number]
    logger.info(f"🔄 Running Step {step_number}: {step_module}")

    try:
        # Import and run the step's pipeline
        module = __import__(f"{step_module}.pipeline", fromlist=["main"])
        return module.main()
    except ImportError as e:
        logger.error(f"❌ Step {step_number} not implemented yet: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error running Step {step_number}: {e}")
        return False

def run_all_steps():
    """Run all BI framework steps in sequence."""
    logger.info("🚀 Running complete BI 0→1 Framework pipeline...")

    steps = [2, 3, 4, 5, 6]  # Skip step 1 (completed)
    success_count = 0

    for step in steps:
        if run_step(step):
            success_count += 1
        else:
            logger.error(f"❌ Step {step} failed. Stopping pipeline.")
            break

    logger.info(f"🏁 Pipeline completed: {success_count}/{len(steps)} steps successful")
    return success_count == len(steps)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Chicago SMB Market Radar - BI 0→1 Framework")
    parser.add_argument("--steps", type=str, help="Comma-separated list of steps to run (e.g., '2,3,4')")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    parser.add_argument("--step", type=int, help="Run a specific step (1-6)")

    args = parser.parse_args()

    if args.all:
        success = run_all_steps()
    elif args.steps:
        step_numbers = [int(s.strip()) for s in args.steps.split(",")]
        success = all(run_step(step) for step in step_numbers)
    elif args.step:
        success = run_step(args.step)
    else:
        parser.print_help()
        return 0

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
'''

    with open("main.py", "w") as f:
        f.write(main_content)

    # Make it executable
    os.chmod("main.py", 0o755)
    logger.info("✅ Created main entry point: main.py")

def update_makefile():
    """Update the Makefile to work with the new structure."""
    logger.info("🔧 Updating Makefile...")

    makefile_content = '''run:
	python main.py --all

run-step2:
	python main.py --step 2

run-step3:
	python main.py --step 3

run-step4:
	python main.py --step 4

run-step5:
	python main.py --step 5

run-step6:
	python main.py --step 6

docs-serve:
	@echo "🚀 Starting documentation server..."
	@echo "📚 Serving documentation at http://localhost:8000"
	@echo "📁 Documentation directory: docs/"
	@echo "🛑 Press Ctrl+C to stop the server"
	@echo ""
	@if command -v python3 >/dev/null 2>&1; then \\
		cd docs && python3 -m http.server 8000; \\
	elif command -v python >/dev/null 2>&1; then \\
		cd docs && python -m http.server 8000; \\
	else \\
		echo "❌ Python not found. Please install Python to serve documentation."; \\
		exit 1; \\
	fi

docs-build:
	@echo "📚 Building documentation..."
	@echo "✅ Documentation is already in Markdown format"
	@echo "📁 Documentation files:"
	@find docs/ -name "*.md" -type f | head -10
	@echo ""
	@echo "💡 To serve documentation locally, run: make docs-serve"

help:
	@echo "Chicago SMB Market Radar - Available Commands:"
	@echo ""
	@echo "📊 BI Framework Steps:"
	@echo "  run              Run all BI framework steps"
	@echo "  run-step2        Run Step 2: Data Ingestion"
	@echo "  run-step3        Run Step 3: Transform & Model"
	@echo "  run-step4        Run Step 4: Load & Validate"
	@echo "  run-step5        Run Step 5: Visualize & Report"
	@echo "  run-step6        Run Step 6: Automate & Scale"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs-serve       Serve documentation locally at http://localhost:8000"
	@echo "  docs-build       Build documentation (Markdown files)"
	@echo ""
	@echo "📋 Help:"
	@echo "  help             Show this help message"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make run                    # Run all steps"
	@echo "  make run-step2             # Run data ingestion only"
	@echo "  make docs-serve            # Serve docs locally"

setup-automation:
	@echo "🔧 Setting up automation..."
	@chmod +x step6_automate_scale/scripts/setup_automation.sh
	@./step6_automate_scale/scripts/setup_automation.sh

.PHONY: run run-step2 run-step3 run-step4 run-step5 run-step6 docs-serve docs-build help setup-automation
'''

    with open("Makefile", "w") as f:
        f.write(makefile_content)

    logger.info("✅ Updated Makefile")

def create_shared_utilities():
    """Create shared utility files."""
    logger.info("🔧 Creating shared utilities...")

    # Create constants.py
    constants_content = '''"""
Chicago SMB Market Radar - Project Constants

This module contains project-wide constants and configuration.
"""

# BI Framework Steps
BI_STEPS = {
    1: "Scope & Strategy",
    2: "Data Ingestion",
    3: "Transform & Model",
    4: "Load & Validate",
    5: "Visualize & Report",
    6: "Automate & Scale"
}

# Data Sources
DATA_SOURCES = {
    "business_licenses": "r5kz-chrr",
    "building_permits": "ydr8-5enu",
    "cta_boardings": "6iiy-9s97"
}

# Default Configuration
DEFAULT_DAYS_LOOKBACK = 90
DEFAULT_BASELINE_WEEKS = 13
DEFAULT_SHEET_ROWS = 1000
DEFAULT_SHEET_COLS = 26
'''

    with open("shared/constants.py", "w") as f:
        f.write(constants_content)

    logger.info("✅ Created shared/constants.py")

def main():
    """Main restructuring function."""
    logger.info("🚀 Starting Chicago SMB Market Radar restructuring...")

    try:
        # Step 1: Create directory structure
        create_directory_structure()

        # Step 2: Move existing files
        move_existing_files()

        # Step 3: Create step READMEs
        create_step_readmes()

        # Step 4: Create main entry point
        create_main_entry_point()

        # Step 5: Update Makefile
        update_makefile()

        # Step 6: Create shared utilities
        create_shared_utilities()

        logger.info("🎉 Restructuring completed successfully!")
        logger.info("")
        logger.info("📋 Next steps:")
        logger.info("1. Review the new structure")
        logger.info("2. Update any remaining import statements")
        logger.info("3. Test the new entry points")
        logger.info("4. Implement missing components in each step")
        logger.info("")
        logger.info("💡 Usage examples:")
        logger.info("  python main.py --all          # Run all steps")
        logger.info("  python main.py --step 2       # Run data ingestion")
        logger.info("  make run-step3                # Run transformations")

    except Exception as e:
        logger.error(f"❌ Restructuring failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
