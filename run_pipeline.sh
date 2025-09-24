#!/bin/bash
# run_pipeline.sh - Simple bash pipeline script

echo "🚀 Job Application Data Processing Pipeline"
echo "=========================================="

# Change to the correct directory
cd "/Users/mac/Desktop/Job Tracker/Tracker/job-app-tracker"

# Step 1: Extract data from Gmail
echo "🔄 Step 1: Extracting job application data from Gmail..."
python job-app-tracker/main.py
if [ $? -ne 0 ]; then
    echo "❌ Step 1 failed. Stopping pipeline."
    exit 1
fi
echo "✅ Step 1 completed"

# Step 2: Clean duplicates
echo "🔄 Step 2: Cleaning duplicate records..."
python job-app-tracker/clean_duplicates.py
if [ $? -ne 0 ]; then
    echo "❌ Step 2 failed. Stopping pipeline."
    exit 1
fi
echo "✅ Step 2 completed"

# Step 3: Export to CSV
echo "🔄 Step 3: Exporting cleaned data to CSV..."
python job-app-tracker/print_table.py --output data/job_applications.csv
if [ $? -ne 0 ]; then
    echo "❌ Step 3 failed. Stopping pipeline."
    exit 1
fi
echo "✅ Step 3 completed"

# Step 4: Generate statistics
echo "🔄 Step 4: Generating statistics report..."
python job-app-tracker/generate_stats.py
if [ $? -ne 0 ]; then
    echo "❌ Step 4 failed. Stopping pipeline."
    exit 1
fi
echo "✅ Step 4 completed"

# Step 5: Create status distribution visualization
echo "🔄 Step 5: Creating status distribution visualization..."
python job-app-tracker/create_visualizations.py
if [ $? -ne 0 ]; then
    echo "❌ Step 5 failed. Stopping pipeline."
    exit 1
fi
echo "✅ Step 5 completed"

echo ""
echo "🎉 Pipeline completed successfully!"
echo "📁 Generated files:"
echo "  - data/job_applications.json (cleaned data)"
echo "  - data/job_applications.csv (CSV export)"
echo "  - data/processed_ids.json (processed email IDs)"
echo "  - visualizations/status_distribution.html (status distribution chart)"
