import ftplib
import os
import openpyxl
import sys
import argparse
import time  # Add missing import
import traceback  # Add for better error reporting
from scrapers_config import SCRAPERS, DAILY_SCRAPERS, MONTHLY_SCRAPERS

# Parse command line arguments
parser = argparse.ArgumentParser(description='Download files from FTP')
parser.add_argument('scraper', nargs='?', help='Specific scraper to process')
parser.add_argument('--type', choices=['daily', 'monthly'], default='daily',
                    help='Type of scrapers to process (daily or monthly)')
args = parser.parse_args()

# Determine which scrapers to process
if args.scraper:
    if args.scraper not in SCRAPERS:
        print(f"Error: Scraper '{args.scraper}' not found in config")
        sys.exit(1)
    scrapers_to_process = [args.scraper]
else:
    # Process all scrapers of the specified type
    if args.type == 'monthly':
        scrapers_to_process = MONTHLY_SCRAPERS.keys()
    else:  # default to daily
        scrapers_to_process = DAILY_SCRAPERS.keys()

print("Connecting to FTP for uploading files...")
print(f"FTP_PASSWORD environment variable exists: {'Yes' if 'FTP_PASSWORD' in os.environ else 'No'}")

# Get password from environment variable
password = os.environ.get('FTP_PASSWORD')
if not password:
    raise ValueError("FTP_PASSWORD environment variable not set")

try:
    # Connect to FTP
    session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', password)
    
    # Check if directory exists
    if 'competitor_pricing' not in session.nlst():
        print("competitor_pricing directory not found, creating it...")
        session.mkd('competitor_pricing')
    
    # Change to the directory
    session.cwd('competitor_pricing')
    
    # Process each scraper
    for scraper_name in scrapers_to_process:
      scraper = SCRAPERS[scraper_name]
      file_name = scraper["file_name"]
      file_path = f'Pricing Spreadsheets/{file_name}'
    
    # Check if file exists locally before uploading
    print(f"Checking if {file_path} exists locally...")
    if os.path.exists(file_path):
        print(f"Uploading {file_name}...")
        try:
            with open(file_path, 'rb') as file:
                session.storbinary(f'STOR {file_name}', file)
            print(f"Upload of {file_name} complete")
        except Exception as upload_error:
            print(f"Error uploading {file_name}: {str(upload_error)}")
            print(traceback.format_exc())
    else:
        print(f"Warning: {file_path} not found locally, skipping upload")
    
    # Add timestamp file to verify upload
    timestamp = str(time.time())
    with open('upload_timestamp.txt', 'w') as f:
        f.write(f"Upload completed at {time.ctime()}")
    
    with open('upload_timestamp.txt', 'rb') as file:
        session.storbinary('STOR upload_timestamp.txt', file)
    
    session.quit()
    print("Files uploaded successfully")
except Exception as e:
    import traceback
    print(f"Error during FTP upload: {str(e)}")
    print(traceback.format_exc())
