#!/bin/bash

# Local GitHub Actions Workflow Test Script
# This simulates the GitHub Actions environment locally

set -e  # Exit on any error

echo "🧪 Testing GitHub Actions workflow locally..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check Python version (matches GitHub Actions)
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version)
echo "Python version: $PYTHON_VERSION"
if [[ "$PYTHON_VERSION" == *"3.11"* ]]; then
    print_success "Python 3.11 detected (matches GitHub Actions)"
else
    print_warning "Python version differs from GitHub Actions (3.11)"
fi

# Step 2: Create temporary directory (simulates $RUNNER_TEMP)
TEMP_DIR=$(mktemp -d)
export RUNNER_TEMP="$TEMP_DIR"
print_status "Created temp directory: $RUNNER_TEMP"

# Step 3: Install dependencies
print_status "Installing Python dependencies..."
python3 -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
print_success "Dependencies installed"

# Step 4: Setup service account credentials
print_status "Setting up service account credentials..."

# Check if base64 credentials are provided
if [ -z "$GOOGLE_CREDENTIALS_B64" ]; then
    print_warning "GOOGLE_CREDENTIALS_B64 not set. Using local credentials file..."

    # Check if local credentials file exists
    LOCAL_CREDS="/Users/loki/api_keys/google_cloud/ravenswood-consulting-c3a2e60d67a9.json"
    if [ -f "$LOCAL_CREDS" ]; then
        cp "$LOCAL_CREDS" "$RUNNER_TEMP/sa.json"
        print_success "Using local credentials file"
    else
        print_error "No credentials found. Please set GOOGLE_CREDENTIALS_B64 or ensure local file exists"
        exit 1
    fi
else
    print_status "Using GOOGLE_CREDENTIALS_B64 environment variable..."

    # Check if the secret exists and is not empty
    if [ -z "$GOOGLE_CREDENTIALS_B64" ]; then
        print_error "GOOGLE_CREDENTIALS_B64 secret is not set or is empty"
        exit 1
    fi

    # Write credentials to secure temp location
    echo "$GOOGLE_CREDENTIALS_B64" | base64 -d > "$RUNNER_TEMP/sa.json"

    # Check if decoding was successful
    if [ $? -ne 0 ]; then
        print_error "Failed to decode base64 credentials"
        exit 1
    fi
fi

# Set restrictive permissions
chmod 600 "$RUNNER_TEMP/sa.json"

# Verify the file was created securely and contains valid JSON
if [ ! -f "$RUNNER_TEMP/sa.json" ]; then
    print_error "Credentials file was not created"
    exit 1
fi

# Validate JSON structure
if ! python3 -m json.tool "$RUNNER_TEMP/sa.json" > /dev/null 2>&1; then
    print_error "Credentials file does not contain valid JSON"
    exit 1
fi

print_success "Credentials file created successfully"
ls -la "$RUNNER_TEMP/sa.json"

# Step 5: Set environment variables (simulates GitHub Actions environment)
export GOOGLE_APPLICATION_CREDENTIALS="$RUNNER_TEMP/sa.json"
export DAYS_LOOKBACK="90"
export WEEKLY_BASELINE_WEEKS="13"
export ENABLE_PERMITS="true"
export ENABLE_CTA="true"

# Check if SHEET_ID is set
if [ -z "$SHEET_ID" ]; then
    print_warning "SHEET_ID not set. Pipeline may fail without it."
    print_status "Please set SHEET_ID environment variable if needed:"
    print_status "export SHEET_ID='your_google_sheet_id'"
fi

print_status "Environment variables set:"
echo "  GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"
echo "  DAYS_LOOKBACK: $DAYS_LOOKBACK"
echo "  WEEKLY_BASELINE_WEEKS: $WEEKLY_BASELINE_WEEKS"
echo "  ENABLE_PERMITS: $ENABLE_PERMITS"
echo "  ENABLE_CTA: $ENABLE_CTA"
echo "  SHEET_ID: ${SHEET_ID:-'(not set)'}"

# Step 6: Test credentials
print_status "Testing Google credentials..."
python3 -c "
import json
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

try:
    credentials, project = default()
    print('✓ Google credentials loaded successfully')
    print(f'✓ Project ID: {project}')

    # Load and verify the service account info
    with open('$RUNNER_TEMP/sa.json', 'r') as f:
        sa_info = json.load(f)
    print(f'✓ Service account: {sa_info.get(\"client_email\", \"unknown\")}')

except DefaultCredentialsError as e:
    print(f'✗ Failed to load credentials: {e}')
    exit(1)
except Exception as e:
    print(f'✗ Error testing credentials: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Google credentials test passed"
else
    print_error "Google credentials test failed"
    exit 1
fi

# Step 7: Run the pipeline (with option to skip)
echo ""
read -p "Do you want to run the full pipeline? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running the main pipeline..."
    python3 -m src.main

    if [ $? -eq 0 ]; then
        print_success "Pipeline completed successfully!"
    else
        print_error "Pipeline failed"
        exit 1
    fi
else
    print_status "Skipping pipeline execution (use -f flag to force run)"
fi

# Step 8: Cleanup
print_status "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"
print_success "Cleanup completed"

echo ""
print_success "🎉 Local workflow test completed successfully!"
echo "Your workflow should work correctly in GitHub Actions."
