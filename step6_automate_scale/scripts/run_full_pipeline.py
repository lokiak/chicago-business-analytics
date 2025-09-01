#!/usr/bin/env python3
"""
Automated Analysis Script for Chicago SMB Market Radar

This script demonstrates how to automate the analysis workflow using
Jupyter notebooks and provides a foundation for full automation.

Usage:
    python scripts/automated_analysis.py [--notebooks] [--reports] [--all]
"""

import argparse
import sys
import os
from pathlib import Path
import subprocess
import logging
from datetime import datetime
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import load_settings
from sheets import open_sheet
from brief import render_markdown_brief

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_notebook(notebook_path: Path) -> bool:
    """
    Execute a Jupyter notebook and return success status.

    Args:
        notebook_path: Path to the notebook file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Executing notebook: {notebook_path}")

        # Use nbconvert to execute the notebook
        cmd = [
            'jupyter', 'nbconvert',
            '--to', 'notebook',
            '--execute',
            '--inplace',
            str(notebook_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"✅ Successfully executed {notebook_path}")
            return True
        else:
            logger.error(f"❌ Failed to execute {notebook_path}")
            logger.error(f"Error: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Exception executing {notebook_path}: {e}")
        return False

def run_data_pipeline() -> bool:
    """
    Run the main data pipeline.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("🔄 Starting data pipeline...")

        # Import and run main function
        from main import main
        main()

        logger.info("✅ Data pipeline completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Data pipeline failed: {e}")
        return False

def run_analysis_notebooks() -> bool:
    """
    Run all analysis notebooks in sequence.

    Returns:
        bool: True if all successful, False otherwise
    """
    notebooks_dir = Path(__file__).parent.parent / "notebooks"
    notebooks = [
        "01_data_exploration.ipynb",
        "02_business_analysis.ipynb"
    ]

    success_count = 0
    total_count = len(notebooks)

    for notebook in notebooks:
        notebook_path = notebooks_dir / notebook
        if notebook_path.exists():
            if run_notebook(notebook_path):
                success_count += 1
        else:
            logger.warning(f"⚠️ Notebook not found: {notebook_path}")

    logger.info(f"📊 Notebook execution: {success_count}/{total_count} successful")
    return success_count == total_count

def generate_reports() -> bool:
    """
    Generate automated reports.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("📄 Generating reports...")

        # Generate markdown brief
        reports_dir = Path(__file__).parent.parent / "reports"
        latest_week = datetime.utcnow()

        # Create empty dataframes for brief (since we're not doing weekly aggregation yet)
        import pandas as pd
        top_level = pd.DataFrame(columns=["community_area_name", "new_licenses"])
        top_momentum = pd.DataFrame(columns=["community_area_name", "new_licenses"])

        md_path = render_markdown_brief(reports_dir, latest_week, top_level, top_momentum)
        logger.info(f"✅ Report generated: {md_path}")

        return True

    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return False

def send_notification(success: bool, details: str = "") -> None:
    """
    Send email notification about automation results.

    Args:
        success: Whether the automation was successful
        details: Additional details to include
    """
    try:
        # Email configuration (you'll need to set these in your environment)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email_user = os.getenv("EMAIL_USER", "")
        email_password = os.getenv("EMAIL_PASSWORD", "")
        email_to = os.getenv("EMAIL_TO", "")

        if not all([email_user, email_password, email_to]):
            logger.warning("⚠️ Email configuration incomplete, skipping notification")
            return

        # Create message
        msg = MimeMultipart()
        msg['From'] = email_user
        msg['To'] = email_to
        msg['Subject'] = f"Chicago SMB Market Radar - Automation {'Success' if success else 'Failure'}"

        # Create body
        status = "✅ SUCCESS" if success else "❌ FAILURE"
        body = f"""
Chicago SMB Market Radar - Automated Analysis Report

Status: {status}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Details:
{details}

This is an automated message from the Chicago SMB Market Radar system.
        """

        msg.attach(MimeText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, email_to, text)
        server.quit()

        logger.info("✅ Notification sent successfully")

    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}")

def main():
    """Main automation function."""
    parser = argparse.ArgumentParser(description="Automated Analysis for Chicago SMB Market Radar")
    parser.add_argument("--notebooks", action="store_true", help="Run analysis notebooks")
    parser.add_argument("--reports", action="store_true", help="Generate reports")
    parser.add_argument("--pipeline", action="store_true", help="Run data pipeline")
    parser.add_argument("--all", action="store_true", help="Run all automation steps")
    parser.add_argument("--notify", action="store_true", help="Send email notifications")

    args = parser.parse_args()

    # Create logs directory
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    logger.info("🚀 Starting Chicago SMB Market Radar automation")
    logger.info(f"Arguments: {vars(args)}")

    success = True
    details = []

    try:
        # Run data pipeline
        if args.pipeline or args.all:
            if run_data_pipeline():
                details.append("✅ Data pipeline: Success")
            else:
                details.append("❌ Data pipeline: Failed")
                success = False

        # Run analysis notebooks
        if args.notebooks or args.all:
            if run_analysis_notebooks():
                details.append("✅ Analysis notebooks: Success")
            else:
                details.append("❌ Analysis notebooks: Failed")
                success = False

        # Generate reports
        if args.reports or args.all:
            if generate_reports():
                details.append("✅ Report generation: Success")
            else:
                details.append("❌ Report generation: Failed")
                success = False

        # Send notification if requested
        if args.notify:
            send_notification(success, "\n".join(details))

        logger.info(f"🏁 Automation completed: {'Success' if success else 'Failure'}")

    except Exception as e:
        logger.error(f"❌ Automation failed with exception: {e}")
        success = False

        if args.notify:
            send_notification(success, f"Exception: {e}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
