import ftplib
import os
import time
import traceback

def upload_to_ftp(file_path, file_name):
    """Upload a single file to FTP server"""
    print(f"Uploading {file_name} to FTP...")
    
    # Get password from environment variable
    password = os.environ.get('FTP_PASSWORD')
    if not password:
        print("Error: FTP_PASSWORD environment variable not set")
        return False
    
    try:
        # Connect to FTP
        session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', password)
        
        # Check if directory exists
        if 'competitor_pricing' not in session.nlst():
            print("competitor_pricing directory not found, creating it...")
            session.mkd('competitor_pricing')
        
        # Change to the directory
        session.cwd('competitor_pricing')
        
        # Upload the file
        with open(file_path, 'rb') as file:
            session.storbinary(f'STOR {file_name}', file)
        
        # Add timestamp for verification
        timestamp = str(time.time())
        with open('upload_timestamp.txt', 'w') as f:
            f.write(f"Upload of {file_name} completed at {time.ctime()}")
        
        with open('upload_timestamp.txt', 'rb') as file:
            session.storbinary('STOR upload_timestamp.txt', file)
        
        session.quit()
        print(f"Upload of {file_name} to FTP successful")
        return True
    
    except Exception as e:
        print(f"Error during FTP upload of {file_name}: {str(e)}")
        print(traceback.format_exc())
        return False
