import ftplib
import os
import openpyxl
import sys
import argparse
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

# Create directory if it doesn't exist
os.makedirs('Pricing Spreadsheets', exist_ok=True)

print("Connecting to FTP for downloading files...")
print(f"FTP_PASSWORD environment variable exists: {'Yes' if 'FTP_PASSWORD' in os.environ else 'No'}")

# Get password from environment variable
password = os.environ.get('FTP_PASSWORD')
if not password:
    raise ValueError("FTP_PASSWORD environment variable not set")

try:
    # Connect to FTP
    session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', password)
    
    print("Connected to FTP. Checking for competitor_pricing directory...")
    # Check if directory exists
    if 'competitor_pricing' not in session.nlst():
        print("competitor_pricing directory not found, creating it...")
        session.mkd('competitor_pricing')
    
    # Change to the directory
    session.cwd('competitor_pricing')
    
    # List files to see what's available
    files = session.nlst()
    print(f"Files in directory: {files}")
    
    # Process each scraper
    for scraper_name in scrapers_to_process:
        scraper = SCRAPERS[scraper_name]
        file_name = scraper["file_name"]
        
        print(f"Processing {scraper['description']} ({file_name})...")
        
        # Download Excel file if it exists
        if file_name in files:
            print(f"Downloading {file_name}...")
            with open(f'Pricing Spreadsheets/{file_name}', 'wb') as f:
                session.retrbinary(f'RETR {file_name}', f.write)
            print("Download complete")
        else:
            print(f"{file_name} not found on server, creating a new file...")
            # Create a new Excel file since it's not on the server
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = 'Sheet'
            # Add header row
            headers = ['SKU', 'Brand', 'Title', 'Price', 'URL', 'Image', 'Description', 'Date', 'Stock Available']
            for col, header in enumerate(headers, 1):
                sheet.cell(row=1, column=col).value = header
            wb.save(f'Pricing Spreadsheets/{file_name}')
            print(f"Created new {file_name} file")

    session.quit()
    print("Files downloaded successfully")
except Exception as e:
    print(f"Error during FTP download: {str(e)}")
    import traceback
    print(traceback.format_exc())
    
    # Create empty files for any scrapers that were requested
    for scraper_name in scrapers_to_process:
        file_name = SCRAPERS[scraper_name]["file_name"]
        if not os.path.exists(f'Pricing Spreadsheets/{file_name}'):
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = 'Sheet'
            # Add header row
            headers = ['SKU', 'Brand', 'Title', 'Price', 'URL', 'Image', 'Description', 'Date', 'Stock Available']
            for col, header in enumerate(headers, 1):
                sheet.cell(row=1, column=col).value = header
            wb.save(f'Pricing Spreadsheets/{file_name}')
            print(f"Created empty {file_name} file due to FTP error")
