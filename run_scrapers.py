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
parser.add_argument('--chunk', type=int, default=0,
                    help='Chunk number for long-running scrapers (0 = run all normally)')
args = parser.parse_args()

# Import scraper configuration
try:
    from scrapers_config import DAILY_SCRAPERS, MONTHLY_SCRAPERS, CHUNKED_SCRAPERS
except ImportError:
    # Backward compatibility if CHUNKED_SCRAPERS doesn't exist
    try:
        from scrapers_config import DAILY_SCRAPERS, MONTHLY_SCRAPERS
        CHUNKED_SCRAPERS = {}
    except ImportError:
        print("Error: scrapers_config.py not found. Please create this file with DAILY_SCRAPERS and MONTHLY_SCRAPERS dictionaries.")
        sys.exit(1)

scrapers = MONTHLY_SCRAPERS if args.type == 'monthly' else DAILY_SCRAPERS

# Run each scraper with timeout
MAX_SCRAPER_RUNTIME = 340 * 60  # 340 minutes (just under 6 hours) max per scraper
success_count = 0
failure_count = 0
skipped_count = 0

print(f"\n=== Starting {args.type} scrapers run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
if args.chunk > 0:
    print(f"Running CHUNK {args.chunk} for long-running scrapers")
print(f"Found {len(scrapers)} {args.type} scrapers to run")

for scraper_name, config in scrapers.items():
    script_name = config['script_name']
    
    # Check if this scraper needs chunking
    is_chunked = scraper_name in CHUNKED_SCRAPERS
    
    # Skip non-chunked scrapers when running a specific chunk
    if args.chunk > 0 and not is_chunked:
        print(f"\nSkipping {config['description']} (not a chunked scraper)")
        skipped_count += 1
        continue
    
    # Skip chunked scrapers when running normally (chunk 0) if they're marked for chunking only
    if args.chunk == 0 and is_chunked and CHUNKED_SCRAPERS.get(scraper_name, {}).get('chunk_only', False):
        print(f"\nSkipping {config['description']} (requires chunk mode)")
        skipped_count += 1
        continue
    
    print(f"\n=== Running {config['description']} ({scraper_name}) ===")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Build command
    cmd = ['python', script_name, scraper_name]
    
    # Add chunking parameters if this is a chunked scraper
    if is_chunked and args.chunk > 0:
        chunk_config = CHUNKED_SCRAPERS[scraper_name]
        pages_per_chunk = chunk_config.get('pages_per_chunk', 500)
        start_page = ((args.chunk - 1) * pages_per_chunk) + 1
        
        # Check if we've exceeded max pages for this scraper
        max_pages_total = chunk_config.get('max_pages_total', 1000)
        if start_page > max_pages_total:
            print(f"Chunk {args.chunk} exceeds max pages ({max_pages_total}) for {scraper_name}, skipping")
            skipped_count += 1
            continue
        
        cmd.extend(['--start-page', str(start_page), '--max-pages', str(pages_per_chunk)])
        print(f"Running pages {start_page} to {start_page + pages_per_chunk - 1}")
    
    try:
        # Create a process with timeout
        process = subprocess.Popen(
            cmd,
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
                print(f"\nWARNING: {scraper_name} exceeded maximum runtime of {MAX_SCRAPER_RUNTIME/60:.0f} minutes")
                
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
