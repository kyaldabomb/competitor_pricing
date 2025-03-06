import ftplib
import os
import time
import sys
from scrapers_config import SCRAPERS

# Get scraper name from command line argument
if len(sys.argv) > 1:
    scraper_name = sys.argv[1]
    if scraper_name not in SCRAPERS:
        print(f"Error: Scraper '{scraper_name}' not found in config")
        sys.exit(1)
    scrapers_to_process = [scraper_name]
else:
    # Process all scrapers if none specified
    scrapers_to_process = SCRAPERS.keys()

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
        if os.path.exists(file_path):
            print(f"Uploading {file_name}...")
            with open(file_path, 'rb') as file:
                session.storbinary(f'STOR {file_name}', file)
            print(f"Upload of {file_name} complete")
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
