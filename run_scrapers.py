#!/usr/bin/env python3
import argparse
import subprocess
import sys
from scrapers_config import DAILY_SCRAPERS, MONTHLY_SCRAPERS

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run multiple scrapers')
parser.add_argument('--type', choices=['daily', 'monthly'], default='daily',
                    help='Type of scrapers to run (daily or monthly)')
args = parser.parse_args()

# Determine which scrapers to run
if args.type == 'monthly':
    scrapers = MONTHLY_SCRAPERS
else:
    scrapers = DAILY_SCRAPERS

# Run each scraper
success_count = 0
failure_count = 0

for scraper_name, config in scrapers.items():
    script_name = config['script_name']
    print(f"\n=== Running {config['description']} ===")
    
    try:
        result = subprocess.run(['python', script_name, scraper_name], 
                                capture_output=True, text=True, check=False)
        
        # Print output
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"ERROR: {config['description']} failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
            failure_count += 1
        else:
            print(f"SUCCESS: {config['description']} completed successfully")
            success_count += 1
    except Exception as e:
        print(f"ERROR: Failed to run {script_name}: {str(e)}")
        failure_count += 1

print(f"\n=== Summary: {success_count} succeeded, {failure_count} failed ===")

# Exit with non-zero code if any scrapers failed
if failure_count > 0:
    sys.exit(1)
