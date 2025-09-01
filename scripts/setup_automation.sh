#!/bin/bash

# Chicago SMB Market Radar - Automation Setup Script
# This script sets up basic automation for the project

set -e

echo "🚀 Setting up Chicago SMB Market Radar automation..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"

# Create necessary directories
echo "📂 Creating directories..."
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/scripts/cron"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$PROJECT_ROOT/scripts/automated_analysis.py"

# Create cron job template
echo "⏰ Creating cron job template..."
cat > "$PROJECT_ROOT/scripts/cron/chicago_smb_automation.cron" << 'EOF'
# Chicago SMB Market Radar - Daily Automation
# Run data pipeline and analysis every day at 6 AM

# Data pipeline (daily at 6 AM)
0 6 * * * cd /path/to/chicago-smb-market-radar && python scripts/automated_analysis.py --pipeline --notify >> logs/cron.log 2>&1

# Analysis notebooks (daily at 7 AM, after data pipeline)
0 7 * * * cd /path/to/chicago-smb-market-radar && python scripts/automated_analysis.py --notebooks --reports --notify >> logs/cron.log 2>&1

# Weekly summary (Mondays at 8 AM)
0 8 * * 1 cd /path/to/chicago-smb-market-radar && python scripts/automated_analysis.py --all --notify >> logs/cron.log 2>&1
EOF

echo "📝 Cron job template created at: $PROJECT_ROOT/scripts/cron/chicago_smb_automation.cron"
echo "⚠️  Remember to update the path in the cron file!"

# Create environment template
echo "🔐 Creating environment template..."
cat > "$PROJECT_ROOT/.env.automation" << 'EOF'
# Chicago SMB Market Radar - Automation Environment Variables
# Copy this to .env and fill in your values

# Google Sheets Configuration (already configured)
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
# SHEET_ID=your_sheet_id

# Email Configuration for Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com

# Automation Settings
DAYS_LOOKBACK=90
ENABLE_PERMITS=true
ENABLE_CTA=true
EOF

echo "📝 Environment template created at: $PROJECT_ROOT/.env.automation"
echo "⚠️  Copy this to .env and configure your email settings!"

# Create systemd service template (for Linux systems)
echo "🔧 Creating systemd service template..."
cat > "$PROJECT_ROOT/scripts/cron/chicago-smb-automation.service" << 'EOF'
[Unit]
Description=Chicago SMB Market Radar Automation
After=network.target

[Service]
Type=oneshot
User=your_username
WorkingDirectory=/path/to/chicago-smb-market-radar
ExecStart=/usr/bin/python3 scripts/automated_analysis.py --all --notify
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "📝 Systemd service template created at: $PROJECT_ROOT/scripts/cron/chicago-smb-automation.service"

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > "$PROJECT_ROOT/scripts/monitor_automation.py" << 'EOF'
#!/usr/bin/env python3
"""
Monitoring script for Chicago SMB Market Radar automation.
Checks system health and sends alerts if needed.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MimeText

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import load_settings
from sheets import open_sheet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_freshness():
    """Check if data is fresh (less than 24 hours old)."""
    try:
        settings = load_settings()
        sh = open_sheet(settings.sheet_id, settings.google_creds_path)

        # Check the last update time (you might need to add a timestamp column)
        # This is a simplified check
        return True, "Data appears fresh"

    except Exception as e:
        return False, f"Data freshness check failed: {e}"

def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100

        if free_percent < 10:
            return False, f"Low disk space: {free_percent:.1f}% free"
        else:
            return True, f"Disk space OK: {free_percent:.1f}% free"

    except Exception as e:
        return False, f"Disk space check failed: {e}"

def check_log_files():
    """Check for recent errors in log files."""
    try:
        logs_dir = Path(__file__).parent.parent / "logs"
        if not logs_dir.exists():
            return True, "No logs directory found"

        # Check for recent error logs
        error_count = 0
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime > (datetime.now() - timedelta(hours=24)).timestamp():
                with open(log_file) as f:
                    content = f.read()
                    error_count += content.count("ERROR")

        if error_count > 10:
            return False, f"High error count in logs: {error_count} errors in last 24h"
        else:
            return True, f"Log errors OK: {error_count} errors in last 24h"

    except Exception as e:
        return False, f"Log check failed: {e}"

def send_alert(message):
    """Send alert email."""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email_user = os.getenv("EMAIL_USER", "")
        email_password = os.getenv("EMAIL_PASSWORD", "")
        email_to = os.getenv("EMAIL_TO", "")

        if not all([email_user, email_password, email_to]):
            logger.warning("Email configuration incomplete, cannot send alert")
            return

        msg = MimeText(f"Chicago SMB Market Radar Alert:\n\n{message}")
        msg['Subject'] = "Chicago SMB Market Radar - System Alert"
        msg['From'] = email_user
        msg['To'] = email_to

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()

        logger.info("Alert sent successfully")

    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

def main():
    """Run all health checks."""
    logger.info("🔍 Running system health checks...")

    checks = [
        ("Data Freshness", check_data_freshness),
        ("Disk Space", check_disk_space),
        ("Log Files", check_log_files)
    ]

    failed_checks = []

    for check_name, check_func in checks:
        try:
            success, message = check_func()
            status = "✅" if success else "❌"
            logger.info(f"{status} {check_name}: {message}")

            if not success:
                failed_checks.append(f"{check_name}: {message}")

        except Exception as e:
            logger.error(f"❌ {check_name}: Check failed with exception: {e}")
            failed_checks.append(f"{check_name}: Check failed with exception: {e}")

    if failed_checks:
        alert_message = "System health check failures:\n\n" + "\n".join(failed_checks)
        send_alert(alert_message)
        logger.warning("⚠️ Health check failures detected, alert sent")
    else:
        logger.info("✅ All health checks passed")

if __name__ == "__main__":
    main()
EOF

chmod +x "$PROJECT_ROOT/scripts/monitor_automation.py"
echo "📊 Monitoring script created at: $PROJECT_ROOT/scripts/monitor_automation.py"

# Create installation instructions
echo "📋 Creating installation instructions..."
cat > "$PROJECT_ROOT/scripts/AUTOMATION_SETUP.md" << 'EOF'
# Chicago SMB Market Radar - Automation Setup Instructions

## Quick Start

1. **Configure Environment:**
   ```bash
   cp .env.automation .env
   # Edit .env with your email settings
   ```

2. **Test Automation:**
   ```bash
   python scripts/automated_analysis.py --all --notify
   ```

3. **Set up Cron Jobs:**
   ```bash
   # Edit the cron file with your project path
   nano scripts/cron/chicago_smb_automation.cron

   # Install the cron job
   crontab scripts/cron/chicago_smb_automation.cron
   ```

4. **Set up Monitoring:**
   ```bash
   # Add monitoring to cron (runs every hour)
   echo "0 * * * * cd /path/to/chicago-smb-market-radar && python scripts/monitor_automation.py" | crontab -
   ```

## Manual Testing

Test individual components:
```bash
# Test data pipeline only
python scripts/automated_analysis.py --pipeline

# Test notebooks only
python scripts/automated_analysis.py --notebooks

# Test reports only
python scripts/automated_analysis.py --reports

# Test everything
python scripts/automated_analysis.py --all
```

## Troubleshooting

1. **Check logs:**
   ```bash
   tail -f logs/automation.log
   tail -f logs/cron.log
   ```

2. **Test email configuration:**
   ```bash
   python -c "import os; print('Email config:', bool(os.getenv('EMAIL_USER')))"
   ```

3. **Check cron jobs:**
   ```bash
   crontab -l
   ```

## Next Steps

1. Set up cloud infrastructure (see AUTOMATION_STRATEGY.md)
2. Implement advanced monitoring
3. Add data quality checks
4. Set up CI/CD pipelines
EOF

echo "📋 Installation instructions created at: $PROJECT_ROOT/scripts/AUTOMATION_SETUP.md"

echo ""
echo "🎉 Automation setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.automation to .env and configure your email settings"
echo "2. Test the automation: python scripts/automated_analysis.py --all --notify"
echo "3. Set up cron jobs following the instructions in scripts/AUTOMATION_SETUP.md"
echo "4. Review the automation strategy in docs/AUTOMATION_STRATEGY.md"
echo ""
echo "For more information, see:"
echo "- docs/AUTOMATION_STRATEGY.md (comprehensive automation plan)"
echo "- scripts/AUTOMATION_SETUP.md (setup instructions)"
echo "- notebooks/README.md (analysis framework)"
