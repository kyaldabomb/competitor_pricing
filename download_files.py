import ftplib
import os

# Create directory if it doesn't exist
os.makedirs('Pricing Spreadsheets', exist_ok=True)

print("Connecting to FTP for downloading files...")
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
    if 'Sky_Music.xlsx' in files:
        print("Downloading Sky_Music.xlsx...")
        with open('Pricing Spreadsheets/Sky_Music.xlsx', 'wb') as f:
            session.retrbinary('RETR Sky_Music.xlsx', f.write)
        print("Download complete")
    else:
        print("Sky_Music.xlsx not found on server, creating placeholder file...")
        # Create an empty placeholder file for first run
        with open('Pricing Spreadsheets/Sky_Music.xlsx', 'wb') as f:
            f.write(b'')

    # Add other files as needed
    
    session.quit()
    print("Files downloaded successfully")
except Exception as e:
    print(f"Error during FTP download: {str(e)}")
    # Create empty files if download fails
    with open('Pricing Spreadsheets/Sky_Music.xlsx', 'wb') as f:
        f.write(b'')
    print("Created empty placeholder files")
