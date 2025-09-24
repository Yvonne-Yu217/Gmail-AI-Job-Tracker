#!/bin/bash
# setup.sh - Quick setup script for Job Application Tracker

echo "Job Application Tracker Setup"
echo "=============================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data visualizations

# Check for configuration files
echo "Checking configuration..."
if [ ! -f "config/gmail_credentials.json" ]; then
    echo "⚠️  Missing: config/gmail_credentials.json"
    echo "   Please download from Google Cloud Console"
fi

if [ ! -f "config/.env" ]; then
    echo "⚠️  Missing: config/.env"
    echo "   Please copy config/.env.example to config/.env and add your OpenAI API key"
fi

echo ""
echo "Setup complete! Next steps:"
echo "1. Add your Gmail credentials to config/gmail_credentials.json"
echo "2. Copy config/.env.example to config/.env and add your OpenAI API key"
echo "3. Run: python job-app-tracker/pipeline.py"
