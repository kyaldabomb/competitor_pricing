import openpyxl
import requests, pprint
from bs4 import BeautifulSoup
import re, math, json
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import os, time, traceback
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import argparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run monthly scraper for Sky Music')
parser.add_argument('scraper', nargs='?', default='sky_music_monthly', 
                    help='Scraper name from config')
args = parser.parse_args()

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
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        
        if success:
            msg['Subject'] = f"Sky Music Monthly Scraper Success: {items_count} new items added"
            body = f"The Sky Music monthly web scraper ran successfully and added {items_count} new items."
        else:
            msg['Subject'] = "Sky Music Monthly Scraper Failed"
            body = f"The Sky Music monthly web scraper encountered an error:\n\n{error_msg}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        print(traceback.format_exc())

# Load the Excel file upfront to avoid issues later
file_path = "Pricing Spreadsheets/Sky_Music.xlsx"
try:
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['Sheet']
    
    # Get existing URLs to avoid duplicates
    url_list = []
    for x in range(2, sheet.max_row+1):
        url = sheet['E'+str(x)].value
        if url:
            url_list.append(url)
    
    print(f"Found {len(url_list)} existing URLs in the spreadsheet")
except Exception as e:
    print(f"Error loading Excel file: {str(e)}")
    send_email_notification(False, error_msg=f"Error loading Excel file: {str(e)}")
    sys.exit(1)

# Setup Chrome options for headless operation in GitHub Actions
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = None
try:
    # Initialize WebDriver using webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    # Initialize HTML session for other requests
    session = HTMLSession()
    
    itemcounter = 0
    items_scrapped = 0
    max_pages = 30  # Limit the number of pages we'll check
    
    # Loop through search result pages to find products
    for page in range(max_pages):
        url = f'https://skymusic.com.au/search?page={page+1}&type=product&q=%20'
        print(f"Processing page {page+1} of {max_pages}")
        
        # Add retry logic for resilience
        max_retries = 3
        for retry in range(max_retries):
            try:
                driver.get(url)
                time.sleep(3)  # Wait for the page to load
                break
            except Exception as e:
                if retry == max_retries - 1:
                    raise
                print(f"Retry {retry+1}/{max_retries} for page {page+1}: {str(e)}")
                time.sleep(5)
        
        html = driver.page_source
        soup = BeautifulSoup(html, features="lxml")
        
        # Find all product items on the page
        products = soup.find_all(class_='boost-sd__product-item boost-sd__product-item--noBorder boost-sd__product-item-grid-view-layout')
        
        if not products:
            print(f"No products found on page {page+1}, might be at the end")
            if page > 0:  # Skip this check for the first page
                break
        
        # Count how many new items we found on this page
        new_items_on_page = 0
        
        for x in products:
            itemcounter += 1
            
            try:
                # Extract product data from JSON string
                product_data_str = x['data-product']
                # Clean up the string
                product_data_str = product_data_str.replace('"', '"')
                product_data_str = product_data_str.replace('\n', '')
                product_data_json = json.loads(product_data_str)
                
                # Get product URL
                url2 = f'https://skymusic.com.au{x.find("a")["href"]}'
                
                # Skip if already in the spreadsheet
                if url2 in url_list:
                    print(f'Item {str(itemcounter)} already in sheet, skipping')
                    continue
                
                # Process new product
                new_items_on_page += 1
                items_scrapped += 1
                
                # Extract basic data from search page
                price = product_data_json['priceMin']
                title = product_data_json['images'][0]['alt'] if product_data_json.get('images') and len(product_data_json['images']) > 0 else "No Title"
                image = product_data_json['images'][0]['src'] if product_data_json.get('images') and len(product_data_json['images']) > 0 else "No Image"
                
                # Check stock status
                stock_available = 'n'  # Default to not available
                try:
                    stock = product_data_json.get('variants', '{}')
                    if isinstance(stock, str):
                        stock = stock.replace('\n', '')
                        stock = json.loads(stock)
                    
                    if isinstance(stock, list) and len(stock) > 0 and stock[0].get('available'):
                        stock_available = 'y'
                except Exception as stock_error:
                    print(f"Error parsing stock data: {str(stock_error)}")
                
                # Visit product page to get more details with retry logic
                brand = "Unknown"
                sku = "Unknown"
                description = "Not yet scraped"
                
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        driver.get(url2)
                        time.sleep(2)  # Wait for the page to load
                        product_html = driver.page_source
                        soup2 = BeautifulSoup(product_html, features="lxml")
                        
                        # Extract brand
                        try:
                            brand_elem = soup2.find(class_='vendor')
                            if brand_elem:
                                brand = brand_elem.text.strip()
                        except Exception as e:
                            print(f"Could not find brand for {url2}: {str(e)}")
                            
                        # Extract SKU
                        try:
                            sku_elem = soup2.find(class_='sku')
                            if sku_elem:
                                sku = sku_elem.text.strip()
                        except Exception as e:
                            print(f"Could not find SKU for {url2}: {str(e)}")
                        
                        # Special handling for certain brands
                        if brand == 'Ernie Ball':
                            sku = sku.replace('P0', '')
                        
                        if brand.lower() == 'orange':
                            sku = f'{sku}AUSTRALIS'
                        
                        # Extract description
                        try:
                            desc_elem = soup2.find(class_='station-tabs-content-inner')
                            if desc_elem:
                                description = desc_elem.text
                        except Exception as e:
                            print(f"Could not find description for {url2}: {str(e)}")
                        
                        break
                    except Exception as e:
                        if retry == max_retries - 1:
                            print(f"Failed to process product page after {max_retries} attempts: {str(e)}")
                        print(f"Retry {retry+1}/{max_retries} for product {url2}: {str(e)}")
                        time.sleep(5)
                
                print(f'\nScraping Item {str(itemcounter)}\nSKU: {sku}\nPrice: {price}\n')
                
                # Get current date
                today = datetime.now()
                date = today.strftime('%m %d %Y')
                
                # Add to spreadsheet
                sheet.append([sku, brand, title, price, url2, image, description, date, stock_available])
                url_list.append(url2)  # Add to our list to avoid duplicates
                
                print(f'Item {str(itemcounter)} scraped successfully')
                
                # Save periodically
                if int(items_scrapped) % 5 == 0:
                    print(f'Saving Sheet... Please wait....')
                    try:
                        wb.save(file_path)
                        print("Sheet saved successfully")
                    except Exception as e:
                        print(f"Error occurred while saving the Excel file: {str(e)}")
                
                # Add a pause to be gentle with the server
                time.sleep(2)
                
            except Exception as product_error:
                print(f"Error processing product {itemcounter}: {str(product_error)}")
                print(traceback.format_exc())
                # Continue with next product even if this one fails
        
        # If we didn't find any new items on this page, we might want to exit early
        if new_items_on_page == 0 and page > 0:  # Skip this check for the first page
            print(f"No new items found on page {page+1}, exiting early")
            break
        
        # Save after each page
        try:
            wb.save(file_path)
            print(f"Saved after page {page+1}")
        except Exception as e:
            print(f"Error saving after page {page+1}: {str(e)}")
    
    # Final save
    print("Scraping complete. Saving final results...")
    wb.save(file_path)
    print(f"Scraping completed successfully. Added {items_scrapped} new items.")
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
finally:
    # Always close the driver
    if driver:
        try:
            driver.quit()
        except:
            pass
