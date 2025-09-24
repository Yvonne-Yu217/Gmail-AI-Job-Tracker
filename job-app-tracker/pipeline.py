#!/usr/bin/env python3
# pipeline.py - Complete job application data processing pipeline

import os
import sys
import subprocess
import time
from datetime import datetime

def reset_data():
    """Reset existing data files"""
    print("\n" + "="*60)
    print("STEP 0: Reset existing data")
    print("="*60)
    
    data_files = [
        "data/job_applications.json",
        "data/processed_ids.json",
        "data/job_applications.csv",
        "visualizations/status_distribution.html"
    ]
    
    removed_count = 0
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing {file_path}: {e}")
        else:
            print(f"Not found: {file_path}")
    
    print(f"Reset completed. Removed {removed_count} files.")
    return True

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    print()  # Add blank line for better readability
    
    try:
        # Change to the correct directory
        os.chdir("/Users/mac/Desktop/Job Tracker/Tracker/job-app-tracker")
        
        # Run the command with real-time output
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                output_lines.append(output.strip())
        
        # Wait for process to complete
        return_code = process.poll()
        
        if return_code == 0:
            print(f"\n{description} completed successfully")
        else:
            print(f"\n{description} failed with return code {return_code}")
            return False
            
    except Exception as e:
        print(f"Error running {description}: {e}")
        return False
    
    return True

def main():
    """Main pipeline execution"""
    start_time = datetime.now()
    
    print("Job Application Data Processing Pipeline")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Reset data first
    if not reset_data():
        print("Failed to reset data. Stopping pipeline.")
        return False
    
    # Pipeline steps
    steps = [
        {
            "command": "python job-app-tracker/main.py",
            "description": "STEP 1: Extract job application data from Gmail"
        },
        {
            "command": "python job-app-tracker/clean_duplicates.py",
            "description": "STEP 2: Clean duplicate records"
        },
        {
            "command": "python job-app-tracker/print_table.py --output data/job_applications.csv",
            "description": "STEP 3: Export cleaned data to CSV"
        },
        {
            "command": "python job-app-tracker/generate_stats.py",
            "description": "STEP 4: Generate statistics report"
        },
        {
            "command": "python job-app-tracker/create_visualizations.py",
            "description": "STEP 5: Create status distribution visualization"
        }
    ]
    
    # Execute each step
    success_count = 0
    for i, step in enumerate(steps, 1):
        step_start_time = datetime.now()
        
        if run_command(step["command"], step["description"]):
            step_end_time = datetime.now()
            step_duration = step_end_time - step_start_time
            success_count += 1
            
            print(f"\n{'='*60}")
            print(f"STEP {i} SUMMARY")
            print(f"{'='*60}")
            print(f"Status: SUCCESS")
            print(f"Duration: {step_duration}")
            print(f"Completed at: {step_end_time.strftime('%H:%M:%S')}")
            
            time.sleep(1)  # Brief pause between steps
        else:
            step_end_time = datetime.now()
            step_duration = step_end_time - step_start_time
            
            print(f"\n{'='*60}")
            print(f"STEP {i} SUMMARY")
            print(f"{'='*60}")
            print(f"Status: FAILED")
            print(f"Duration: {step_duration}")
            print(f"Failed at: {step_end_time.strftime('%H:%M:%S')}")
            print(f"\nPipeline stopped due to step {i} failure.")
            break
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("Pipeline Summary")
    print(f"{'='*60}")
    print(f"Completed steps: {success_count}/{len(steps)}")
    print(f"Total duration: {duration}")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == len(steps):
        print("\nPipeline completed successfully!")
        print("\nGenerated files:")
        print("  - data/job_applications.json (cleaned data)")
        print("  - data/job_applications.csv (CSV export)")
        print("  - data/processed_ids.json (processed email IDs)")
        print("  - visualizations/status_distribution.html (status distribution chart)")
    else:
        print(f"\nPipeline partially completed ({success_count}/{len(steps)} steps)")
    
    return success_count == len(steps)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nPipeline failed with error: {e}")
        sys.exit(1)
