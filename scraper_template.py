import openpyxl
from bs4 import BeautifulSoup
import requests
import os
import time
import traceback
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from scrapers_config import SCRAPERS

# Get scraper name from command line argument
if len(sys.argv) > 1:
    scraper_name = sys.argv[1]
    if scraper_name not in SCRAPERS:
        print(f"Error: Scraper '{scraper_name}' not found in config")
        sys.exit(1)
else:
    print("Error: No scraper name provided")
    sys.exit(1)

# Get scraper config
scraper_config = SCRAPERS[scraper_name]
file_name = scraper_config["file_name"]
description = scraper_config["description"]

# Email notification function
def send_email_notification(success, items_count=0, error_msg=""):
    print("Sending email notification...")
    try:
        # Email settings
        sender = "kyal@scarlettmusic.com.au"
        receiver = "kyal@scarlettmusic.com.au"
        password = os.environ.get('EMAIL_PASSWORD')
        if not password:
            print("Email password not found in environment variables")
            return
            
        host = "mail.scarlettmusic.com.au"
        port = 587  # Try different ports if this doesn't work: 25, 465
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        
        if success:
            msg['Subject'] = f"{description} Scraper Success: {items_count} items scraped"
            body = f"The {description} web scraper ran successfully and processed {items_count} items."
        else:
            msg['Subject'] = f"{description} Scraper Failed"
            body = f"The {description} web scraper encountered an error:\n\n{error_msg}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        print(traceback.format_exc())

# Use local path instead of network path
file_path = f"Pricing Spreadsheets/{file_name}"
wb = openpyxl.load_workbook(file_path)
sheet = wb['Sheet']

item_number = 0
items_scrapped = 0

# YOUR SCRAPER CODE GOES HERE
# ...
