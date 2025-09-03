# Installation & Setup

Get the Chicago SMB Market Radar up and running on your system.

## Prerequisites

- **Python 3.8+** (3.11 recommended)
- **Git** for version control
- **Google Account** for Sheets API access
- **4GB+ RAM** for data processing

## Quick Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/chicago-smb-market-radar.git
cd chicago-smb-market-radar
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Google Sheets Access

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Google Sheets API
4. Create service account credentials
5. Download credentials JSON file
6. Share your Google Sheet with the service account email

### 4. Set Up Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings:
# GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
# SHEET_ID=your_google_sheet_id
```

### 5. Verify Installation

```bash
# Test the installation
python -c "import pandas, great_expectations; print('✅ Installation successful!')"

# Run health check
make help
```

## What's Installed

Your installation includes:

- **Core Pipeline**: Data ingestion, transformation, and validation
- **Great Expectations**: Advanced data cleaning and validation
- **Jupyter Integration**: Analysis notebooks and exploration tools
- **Automation Framework**: Scheduled data processing
- **Documentation Site**: This documentation you're reading!

## Next Steps

1. **[Run Your First Analysis](first-run.md)** - Process your first dataset
2. **[Explore the Framework](../framework/)** - Understand the BI pipeline
3. **[Try Great Expectations](../guides/gx-integration-guide.md)** - Advanced data cleaning

## Troubleshooting

### Common Issues

**Python version conflicts:**
```bash
python3 --version  # Should be 3.8+
which python3
```

**Virtual environment not activating:**
```bash
# Recreate the environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

**Google Sheets authentication errors:**
- Verify service account email is shared on the Sheet
- Check credentials file path in `.env`
- Ensure Google Sheets API is enabled

**Module import errors:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

Need help? Check our [Technical Reference](../technical/) or open an issue on GitHub.