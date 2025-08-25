#!/bin/bash

# Chicago SMB Market Radar - Run Script
echo "🚀 Starting Chicago SMB Market Radar..."

# Activate local virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if activation was successful
if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activated"
    echo "🐍 Python version: $(python --version)"
    echo "📁 Running from: $(pwd)"
    echo "🔧 Using local .env file"
    echo ""

    # Run the main script
    echo "🚀 Executing main.py..."
    python -m src.main
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
