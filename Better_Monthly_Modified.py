import openpyxl
import requests
from bs4 import BeautifulSoup
import re, math
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
import ftplib

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run monthly scraper for Better Music')
parser.add_argument('scraper', nargs='?', default='better_monthly', 
                    help='Scraper name from config')
args = parser.parse_args()

def upload_to_ftp(file_path, file_name):
    print(f"\n==== Uploading {file_name} to FTP ====")
    try:
        # Get FTP password from environment
        ftp_password = os.environ.get('FTP_PASSWORD')
        if not ftp_password:
            print("FTP_PASSWORD not found in environment variables")
            return False
            
        # Connect and upload
        session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', ftp_password)
        
        # Check if directory exists
        if 'competitor_pricing' not in session.nlst():
            print("competitor_pricing directory not found, creating it...")
            session.mkd('competitor_pricing')
        
        # Change to the directory
        session.cwd('competitor_pricing')
        
        # Upload the file
        with open(file_path, 'rb') as file:
            session.storbinary(f'STOR {file_name}', file)
            
        # Create timestamp file for verification
        with open('upload_timestamp.txt', 'w') as f:
            f.write(f"Upload of {file_name} completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        with open('upload_timestamp.txt', 'rb') as file:
            session.storbinary('STOR upload_timestamp.txt', file)
            
        session.quit()
        print(f"File {file_name} uploaded to FTP successfully")
        return True
    except Exception as e:
        print(f"Error uploading to FTP: {str(e)}")
        print(traceback.format_exc())
        return False

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
            msg['Subject'] = f"Better Music Monthly Scraper Success: {items_count} new items added"
            body = f"The Better Music monthly web scraper ran successfully and added {items_count} new items."
        else:
            msg['Subject'] = "Better Music Monthly Scraper Failed"
            body = f"The Better Music monthly web scraper encountered an error:\n\n{error_msg}"
        
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

# Setup Chrome options for headless operation in GitHub Actions
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

try:
    # Initialize WebDriver using webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Print Chrome and ChromeDriver version for debugging
    print(f"Chrome version: {driver.capabilities['browserVersion']}")
    print(f"ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]}")
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    session = HTMLSession()
    
    # Use local path instead of network path
    file_path = "Pricing Spreadsheets/Better.xlsx"
    file_name = "Better.xlsx"
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['Sheet']
    
    # Get existing URLs to avoid duplicates
    url_list = []
    for x in range(2, sheet.max_row+1):
        url = sheet['E'+str(x)].value
        if url:
            url_list.append(url)
    
    print(f"Found {len(url_list)} existing URLs in the spreadsheet")
    
    # Starting the scraping process
    url = 'https://www.bettermusic.com.au/brands'
    print(f"Accessing brands page: {url}")
    
    # Add retry logic for resilience
    max_retries = 3
    for retry in range(max_retries):
        try:
            r = driver.get(url)
            break
        except Exception as e:
            if retry == max_retries - 1:
                raise
            print(f"Retry {retry+1}/{max_retries} for {url}: {str(e)}")
            time.sleep(5)
    
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")
    
    item_number = 0
    items_scrapped = 0
    
    # Process each brand
    brand_elements = soup.find_all(class_='brands-grid__link')
    brand_count = len(brand_elements)
    print(f"Found {brand_count} brands to process")
    
    for brand_index, brand_element in enumerate(brand_elements):
        try:
            brand_url = brand_element['href']
            brand = brand_element.text.strip()
            
            print(f"\nProcessing brand {brand_index+1}/{brand_count}: {brand}")
            print(f"Brand URL: {brand_url}")
            
            # Add retry logic for brand page
            for retry in range(max_retries):
                try:
                    r = driver.get(brand_url)
                    break
                except Exception as e:
                    if retry == max_retries - 1:
                        raise
                    print(f"Retry {retry+1}/{max_retries} for brand {brand}: {str(e)}")
                    time.sleep(5)
            
            html = driver.page_source
            soup2 = BeautifulSoup(html, features="lxml")
            
            products = soup2.find_all(class_='item product product-item')
            print(f"Found {len(products)} products for brand {brand}")
            
            for product in products:
                try:
                    item_number += 1
                    
                    product_link = product.find(class_='product-item-link')
                    if not product_link:
                        print(f"No product link found for item {item_number}, skipping")
                        continue
                        
                    product_url = product_link['href']
                    
                    if product_url in url_list:
                        print(f'Item {str(item_number)} already in sheet, skipping')
                        continue
                    
                    print(f"Processing new product {item_number}: {product_url}")
                    
                    # Add retry logic for product page
                    for retry in range(max_retries):
                        try:
                            r = driver.get(product_url)
                            break
                        except Exception as e:
                            if retry == max_retries - 1:
                                raise
                            print(f"Retry {retry+1}/{max_retries} for product {product_url}: {str(e)}")
                            time.sleep(5)
                    
                    html = driver.page_source
                    soup3 = BeautifulSoup(html, features="lxml")
                    
                    # Extract title
                    try:
                        title_element = soup3.find(class_='page-title-wrapper')
                        if not title_element:
                            print(f"No title found for {product_url}, skipping")
                            continue
                            
                        title = title_element.text
                        title = title.replace('Ä','')
                        title = title.replace('ì', '')
                        title = title.strip()
                    except Exception as e:
                        print(f"Error extracting title: {str(e)}")
                        continue
                    
                    # Extract SKU and RRP
                    try:
                        sku_element = soup3.find(class_='musipos-msrp')
                        if not sku_element:
                            print(f"No SKU found for {product_url}, skipping")
                            continue
                            
                        sku_rrp = sku_element.text
                        sku_rrp = sku_rrp.split(' - RRP $')
                        sku = sku_rrp[0].strip()
                        
                        try:
                            rrp = sku_rrp[1].strip()
                        except IndexError:
                            print(f"No RRP found for {product_url}, continuing anyway")
                            rrp = "N/A"
                    except Exception as e:
                        print(f"Error extracting SKU/RRP: {str(e)}")
                        continue
                    
                    # Extract price
                    try:
                        price_container = soup3.find(class_='product-add-form')
                        if price_container:
                            price_element = price_container.find(class_='price')
                            if price_element:
                                price = price_element.text.strip()
                                price = price.replace('$', '')
                            else:
                                price = "N/A"
                        else:
                            price = "N/A"
                    except Exception as e:
                        print(f"Error extracting price: {str(e)}")
                        price = "N/A"
                    
                    # Extract image
                    try:
                        image_container = soup3.find(class_='gallery__item')
                        if image_container:
                            img_element = image_container.find('img')
                            if img_element and 'src' in img_element.attrs:
                                image = img_element['src']
                            else:
                                image = "N/A"
                        else:
                            image = "N/A"
                    except Exception as e:
                        print(f"Error extracting image: {str(e)}")
                        image = "N/A"
                    
                    # Extract description
                    try:
                        description_element = soup3.find(class_='data item content')
                        if description_element:
                            description = description_element.text.strip()
                        else:
                            description = "No description available."
                    except Exception as e:
                        print(f"Error extracting description: {str(e)}")
                        description = "No description available."
                    
                    # Check stock availability
                    try:
                        stock_element = soup3.find(class_='stock available')
                        stock_avaliable = 'y' if stock_element else 'n'
                    except Exception as e:
                        print(f"Error checking stock: {str(e)}")
                        stock_avaliable = 'n'
                    
                    # Get current date
                    today = datetime.now()
                    date = today.strftime('%m %d %Y')
                    
                    # Add to spreadsheet
                    sheet.append([sku, brand, title, price, product_url, image, description, date, stock_avaliable])
                    url_list.append(product_url)  # Add to our list to avoid duplicates
                    
                    items_scrapped += 1
                    print(f'Item {str(item_number)} scraped successfully')
                    
                    # Save periodically
                    if int(items_scrapped) % 20 == 0:
                        print(f'Saving Sheet... Please wait....')
                        try:
                            wb.save(file_path)
                            print("Sheet saved successfully")
                            
                            # Upload periodically
                            if int(items_scrapped) % 100 == 0:
                                upload_to_ftp(file_path, file_name)
                                
                        except Exception as e:
                            print(f"Error occurred while saving the Excel file: {str(e)}")
                            print(traceback.format_exc())
                    
                    # Add a pause to be gentle with the server
                    time.sleep(3)
                
                except Exception as product_error:
                    print(f"Error processing product {item_number}: {str(product_error)}")
                    print(traceback.format_exc())
                    # Continue with next product even if this one fails
        
        except Exception as brand_error:
            print(f"Error processing brand {brand_index+1}: {str(brand_error)}")
            print(traceback.format_exc())
            # Continue with next brand even if this one fails
    
    # Final save
    wb.save(file_path)
    upload_to_ftp(file_path, file_name)
    
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
    try:
        driver.quit()
    except:
        pass
