import ftplib
import os

print("Starting FTP connection test...")
print(f"FTP_PASSWORD environment variable exists: {'Yes' if 'FTP_PASSWORD' in os.environ else 'No'}")

try:
    # Get password from environment variable or use default for testing
    password = os.environ.get('FTP_PASSWORD')
    if not password:
        raise ValueError("FTP_PASSWORD environment variable not set")
    
    print("Connecting to FTP server...")
    session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', password)
    
    # List directories to verify connection
    print("Listing directories:")
    directories = session.nlst()
    for directory in directories:
        print(f"- {directory}")
    
    # Create competitor_pricing directory if it doesn't exist
    if 'competitor_pricing' not in directories:
        print("competitor_pricing directory not found, creating it...")
        session.mkd('competitor_pricing')
        print("Directory created successfully")
    else:
        print("Found competitor_pricing directory")
        session.cwd('competitor_pricing')
        files = session.nlst()
        print("Files in competitor_pricing:")
        for file in files:
            print(f"- {file}")
    
    # Close the connection
    session.quit()
    print("FTP connection test completed successfully")
    
except Exception as e:
    print(f"Error connecting to FTP: {str(e)}")
