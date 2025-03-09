#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
import signal
from datetime import datetime

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run multiple scrapers')
parser.add_argument('--type', choices=['daily', 'monthly'], default='daily',
                    help='Type of scrapers to run (daily or monthly)')
args = parser.parse_args()

# Import scraper configuration
try:
    from scrapers_config import DAILY_SCRAPERS, MONTHLY_SCRAPERS
    scrapers = MONTHLY_SCRAPERS if args.type == 'monthly' else DAILY_SCRAPERS
except ImportError:
    print("Error: scrapers_config.py not found. Please create this file with DAILY_SCRAPERS and MONTHLY_SCRAPERS dictionaries.")
    sys.exit(1)

# Run each scraper with timeout
MAX_SCRAPER_RUNTIME = 720 * 60  # 15 minutes max per scraper
success_count = 0
failure_count = 0
skipped_count = 0

print(f"\n=== Starting {args.type} scrapers run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
print(f"Found {len(scrapers)} {args.type} scrapers to run")

for scraper_name, config in scrapers.items():
    script_name = config['script_name']
    print(f"\n=== Running {config['description']} ({scraper_name}) ===")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Create a process with timeout
        process = subprocess.Popen(
            ['python', script_name, scraper_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor the process with timeout
        start_time = time.time()
        output_lines = []
        error_lines = []
        
        while process.poll() is None:
            # Read output without blocking
            if process.stdout:
                for line in process.stdout:
                    print(line, end='')
                    output_lines.append(line)
                    
            # Read errors without blocking
            if process.stderr:
                for line in process.stderr:
                    print(f"ERROR: {line}", end='')
                    error_lines.append(line)
            
            # Check for timeout
            if time.time() - start_time > MAX_SCRAPER_RUNTIME:
                print(f"\nWARNING: {scraper_name} exceeded maximum runtime of {MAX_SCRAPER_RUNTIME} seconds")
                
                # On Unix systems (Linux/macOS)
                if hasattr(signal, 'SIGKILL'):
                    process.send_signal(signal.SIGKILL)
                else:
                    # On Windows
                    process.terminate()
                    
                time.sleep(3)  # Give process time to clean up
                if process.poll() is None:
                    process.kill()  # Force kill if still running
                    
                failure_count += 1
                print(f"ERROR: {scraper_name} was terminated due to timeout")
                break
                
            # Small sleep to prevent CPU hogging
            time.sleep(0.5)
        
        # Process completed normally
        if process.returncode == 0:
            print(f"SUCCESS: {config['description']} completed successfully")
            success_count += 1
        else:
            print(f"ERROR: {config['description']} failed with exit code {process.returncode}")
            # Print any remaining stderr
            for line in process.stderr:
                print(f"ERROR: {line}", end='')
            failure_count += 1
            
    except Exception as e:
        print(f"ERROR: Failed to run {script_name}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        failure_count += 1

print(f"\n=== Summary: {success_count} succeeded, {failure_count} failed, {skipped_count} skipped ===")
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Exit with non-zero code if any scrapers failed
if failure_count > 0:
    sys.exit(1)
