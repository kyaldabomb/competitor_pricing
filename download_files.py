import ftplib
import os

# Create directory if it doesn't exist
os.makedirs('Pricing Spreadsheets', exist_ok=True)

# Connect to FTP
session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', os.environ['FTP_PASSWORD'])

# Download Excel files
with open('Pricing Spreadsheets/Sky_Music.xlsx', 'wb') as f:
    session.retrbinary('RETR competitor_pricing/Sky_Music.xlsx', f.write)

# Add other files as needed
# with open('Pricing Spreadsheets/Sounds_Easy.xlsx', 'wb') as f:
#     session.retrbinary('RETR competitor_pricing/Sounds_Easy.xlsx', f.write)

session.quit()
print("Files downloaded successfully")
