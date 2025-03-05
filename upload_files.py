import ftplib
import os
import time

# Get password from environment variable
password = os.environ.get('FTP_PASSWORD')
if not password:
    raise ValueError("FTP_PASSWORD environment variable not set")

print("Connecting to FTP for uploading files...")
try:
    # Connect to FTP
    session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', password)
    
    # Check if directory exists
    if 'competitor_pricing' not in session.nlst():
        print("competitor_pricing directory not found, creating it...")
        session.mkd('competitor_pricing')
    
    # Change to the directory
    session.cwd('competitor_pricing')
    
    # Upload Excel files
    print("Uploading Sky_Music.xlsx...")
    with open('Pricing Spreadsheets/Sky_Music.xlsx', 'rb') as file:
        session.storbinary('STOR Sky_Music.xlsx', file)
    print("Upload complete")
    
    # Add timestamp file to verify upload
    timestamp = str(time.time())
    with open('upload_timestamp.txt', 'w') as f:
        f.write(f"Upload completed at {time.ctime()}")
    
    with open('upload_timestamp.txt', 'rb') as file:
        session.storbinary('STOR upload_timestamp.txt', file)
    
    session.quit()
    print("Files uploaded successfully")
except Exception as e:
    print(f"Error during FTP upload: {str(e)}")
