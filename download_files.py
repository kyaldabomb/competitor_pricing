import ftplib
import os

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
    
    # Download Excel files if they exist
    if 'Belfield.xlsx' in files:
        print("Downloading Belfield.xlsx...")
        with open('Pricing Spreadsheets/Belfield.xlsx', 'wb') as f:
            session.retrbinary('RETR Belfield.xlsx', f.write)
        print("Download complete")
    else:
        print("Belfield.xlsx not found on server, creating a new file...")
        # Create a new Excel file since it's not on the server
        import openpyxl
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = 'Sheet'
        # Add header row
        headers = ['SKU', 'Brand', 'Title', 'Price', 'URL', 'Image', 'Description', 'Date', 'Stock Available']
        for col, header in enumerate(headers, 1):
            sheet.cell(row=1, column=col).value = header
        wb.save('Pricing Spreadsheets/Belfield.xlsx')
        print("Created new Belfield.xlsx file")

    session.quit()
    print("Files downloaded successfully")
except Exception as e:
    print(f"Error during FTP download: {str(e)}")
    # Create new Excel file if download fails
    import openpyxl
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = 'Sheet'
    # Add header row
    headers = ['SKU', 'Brand', 'Title', 'Price', 'URL', 'Image', 'Description', 'Date', 'Stock Available']
    for col, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col).value = header
    wb.save('Pricing Spreadsheets/Belfield.xlsx')
    print("Created new Belfield.xlsx file due to FTP error")
