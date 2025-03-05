import ftplib
import os

# Connect to FTP
session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', os.environ['FTP_PASSWORD'])

# Upload Excel files
with open('Pricing Spreadsheets/Sky_Music.xlsx', 'rb') as file:
    session.storbinary('STOR competitor_pricing/Sky_Music.xlsx', file)

# Add other files as needed
# with open('Pricing Spreadsheets/Sounds_Easy.xlsx', 'rb') as file:
#     session.storbinary('STOR competitor_pricing/Sounds_Easy.xlsx', file)

session.quit()
print("Files uploaded successfully")
