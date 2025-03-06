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
import argparse
from scrapers_config import SCRAPERS

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run monthly scraper for Belfield')
parser.add_argument('scraper', nargs='?', default='belfield_monthly', 
                    help='Scraper name from config')
args = parser.parse_args()

# Get scraper config
if args.scraper not in SCRAPERS:
    print(f"Error: Scraper '{args.scraper}' not found in config")
    sys.exit(1)

scraper_config = SCRAPERS[args.scraper]
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
        port = 587
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        
        if success:
            msg['Subject'] = f"{description} Success: {items_count} new items added"
            body = f"The {description} scraper ran successfully and added {items_count} new items."
        else:
            msg['Subject'] = f"{description} Failed"
            body = f"The {description} scraper encountered an error:\n\n{error_msg}"
        
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

# Get existing URLs to avoid duplicates
url_list = []
for x in range(2, sheet.max_row+1):
    url = sheet['E'+str(x)].value
    if url:
        url_list.append(url)

item_number = 0
items_scrapped = 0

try:
    # Initialize HTML session for JavaScript-rendered pages
    # If using requests_html
    from requests_html import HTMLSession
    session = HTMLSession()
    
    # MONTHLY SCRAPING CODE - search for new products
    # Example: Loop through pagination pages to find all products
    for t in range(1000):  # Adjust this range as needed
        time.sleep(0.3)  # Be gentle with the server
        print(f'Scraping page {t+1}...')
        
        # Make request to the page
        r = session.get(f'https://www.belfieldmusic.com.au/search?page={str(t+1)}&q=+&type=product', timeout=30)
        r.html.render(timeout=10)  # Render JavaScript
        
        # Find all product links
        found_items = False
        for x in r.html.absolute_links:
            if '/products/' in x:
                item_number += 1
                time.sleep(0.3)  # Polite delay
                
                url = x
                if url in url_list:
                    print(f'Item {str(item_number)} already in sheet.')
                    continue
                
                found_items = True
                items_scrapped += 1
                
                # Now scrape the product page
                while True:
                    try:
                        while True:
                            r = requests.get(url, timeout=30)
                            if r.status_code == 430:
                                print('Page limit reached, waiting 5 mins')
                                time.sleep(300)
                                continue
                            else:
                                break
                                
                        soup = BeautifulSoup(r.content, 'html.parser')
                        
                        # Extract product data
                        try:
                            sku = soup.find(class_='sku').text.strip()
                        except:
                            sku = 'N/A'
                            
                        try:
                            brand = soup.find(class_='vendor').text.strip()
                            if brand.lower() == 'orange':
                                sku = f'{sku}AUSTRALIS'
                        except:
                            brand = 'N/A'
                            
                        try:
                            title = soup.find(class_='product_name').text.strip()
                        except:
                            print(f"Could not find title for {url}, skipping")
                            break
                            
                        try:
                            price = soup.find(class_='price-ui').text.strip()
                            if int(price.count('$')) > 1:
                                price = price.split('$')
                                price = price[1]
                            price = price.replace('$', '')
                        except:
                            price = 'N/A'
                            
                        # Get image
                        try:
                            image = soup.find(class_='image__container')
                            for x in image:
                                try:
                                    image = x['data-src']
                                    break
                                except:
                                    pass
                            if image == soup.find(class_='image__container'):
                                image = 'N/A'
                        except:
                            image = 'N/A'
                            
                        # Get description
                        try:
                            description = soup.find(class_='product-tabs__panel').text
                            description = description.replace('\n', '\n\n')
                            description = description.replace('\n\n\n', '\n\n')
                        except:
                            description = 'N/A'
                            
                        # Check stock availability
                        try:
                            stock = soup.find(class_='purchase-details__buttons purchase-details__spb--false product-is-unavailable').text
                            stock_avaliable = 'n'
                        except:
                            stock_avaliable = 'y'
                            
                        # Get current date
                        today = datetime.now()
                        date = today.strftime('%m %d %Y')
                        
                        # Add to Excel sheet
                        sheet.append([sku, brand, title, price, url, image, description, date, stock_avaliable])
                        print(f'Item {str(item_number)} scraped successfully')
                        
                        break
                    except Exception as e:
                        print(f'Error, retrying: {str(e)}')
                        time.sleep(1)
                        continue
                
                # Save periodically
                if int(items_scrapped) % 5 == 0:
                    print(f'Saving Sheet... Please wait....')
                    try:
                        wb.save(file_path)
                    except Exception as e:
                        print(f"Error occurred while saving the Excel file: {str(e)}")
        
        # If no new items found on this page, we might be at the end
        if not found_items and t > 0:  # Skip this check for the first page
            print("No new items found on this page, might be at the end.")
            break
    
    # Final save
    wb.save(file_path)
    print(f"Monthly scraping completed successfully. Added {items_scrapped} new items.")
    send_email_notification(True, items_scrapped)
    
except Exception as e:
    error_message = str(e)
    full_traceback = traceback.format_exc()
    print(f"Error in scraping: {error_message}")
    print(f"Traceback:\n{full_traceback}")
    
    try:
        wb.save(file_path)
        print("Saved progress before error")
    except Exception as save_error:
        print(f"Could not save progress after error: {str(save_error)}")
    
    send_email_notification(False, error_msg=f"{error_message}\n\nFull traceback:\n{full_traceback}")
    sys.exit(1)  # Exit with error code
