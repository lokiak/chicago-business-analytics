#!/usr/bin/env python3
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
    logger.info(f"🔄 Running Step {step_number}")

    if step_number == 2:
        # Step 2: Data Ingestion - use src/main.py
        logger.info("📊 Running data ingestion...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "src/main.py"], cwd=Path(__file__).parent)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"❌ Error running data ingestion: {e}")
            return False

    # For other steps, try to import their pipeline modules
    step_modules = {
        1: "step1_scope_strategy",
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
