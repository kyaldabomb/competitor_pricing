# Skip if already in the spreadsheet (check after fixing URL)
                    if product_url in url_list:
                        print(f'Item {str(item_number)} already in sheet, skipping')
                        continueimport openpyxl
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
            msg['Subject'] = f"Better Monthly Scraper Success: {items_count} new items added"
            body = f"The Better Music monthly web scraper ran successfully and added {items_count} new items."
        else:
            msg['Subject'] = "Better Monthly Scraper Failed"
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
    # Base URL for the website
    base_url = 'https://www.bettermusic.com.au'
    
    # Initialize WebDriver using webdriver-manager
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Print Chrome and ChromeDriver version for debugging
        print(f"Chrome version: {driver.capabilities['browserVersion']}")
        print(f"ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]}")
    except Exception as driver_error:
        print(f"Error initializing Chrome driver: {str(driver_error)}")
        print(traceback.format_exc())
        raise
    
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
    
    # Try a simpler approach directly using the direct URLs 
    item_number = 0
    items_scrapped = 0
    
    # List of specific category pages to try
    category_urls = [
        "https://www.bettermusic.com.au/guitars",
        "https://www.bettermusic.com.au/guitar-amps",
        "https://www.bettermusic.com.au/bass",
        "https://www.bettermusic.com.au/keyboards",
        "https://www.bettermusic.com.au/drums",
        "https://www.bettermusic.com.au/recording",
        "https://www.bettermusic.com.au/pa-live-sound",
        "https://www.bettermusic.com.au/accessories"
    ]
    
    # Process each category
    for category_url in category_urls:
        print(f"\nProcessing category: {category_url}")
        
        page_num = 1
        max_pages_per_category = 5  # Limit pages per category
        
        while page_num <= max_pages_per_category:
            # Construct page URL (add page parameter if not the first page)
            if page_num == 1:
                current_url = category_url
            else:
                current_url = f"{category_url}?p={page_num}"
                
            print(f"Processing page {page_num}: {current_url}")
            
            try:
                # Add retry logic for page access
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        driver.get(current_url)
                        break
                    except Exception as e:
                        if retry == max_retries - 1:
                            raise
                        print(f"Retry {retry+1}/{max_retries} for page {page_num}: {str(e)}")
                        time.sleep(5)
                
                # Wait for page to load
                time.sleep(5)
                html = driver.page_source
                soup2 = BeautifulSoup(html, features="lxml")
            
            # Find all products on the page
            products = soup2.find_all(class_='item product product-item')
            
            if not products:
                products = soup2.find_all(class_='product-item-info')
            
            if not products:
                print(f"No products found on page {page_num}, ending pagination")
                break
                
            print(f"Found {len(products)} products on page {page_num}")
            
            for product in products:
                try:
                    item_number += 1
                    
                    # Find the product link
                    product_link = product.find('a', class_='product-item-link')
                    if not product_link:
                        product_link = product.find('a', class_='product-item-photo')
                        
                    if not product_link or 'href' not in product_link.attrs:
                        print(f"Could not find product URL for item {item_number}, skipping")
                        continue
                        
                    product_url = product_link['href']
                    
                    # Fix URL format (handle protocol-relative URLs)
                    if product_url.startswith('//'):
                        product_url = 'https:' + product_url
                    elif not product_url.startswith('http'):
                        if product_url.startswith('/'):
                            product_url = base_url + product_url
                        else:
                            product_url = base_url + '/' + product_url
                            
                    print(f"Processing new product: {product_url}")
                    
                    # Add retry logic for product page access
                    max_retries = 3
                    for retry in range(max_retries):
                        try:
                            driver.get(product_url)
                            break
                        except Exception as e:
                            if retry == max_retries - 1:
                                raise
                            print(f"Retry {retry+1}/{max_retries} for product {item_number}: {str(e)}")
                            time.sleep(5)
                    
                    # Wait for product page to load
                    time.sleep(2)
                    html = driver.page_source
                    soup3 = BeautifulSoup(html, features="lxml")
                    
                    # Extract title
                    try:
                        title = soup3.find(class_='page-title-wrapper').text
                        title = title.replace('Ä','')
                        title = title.replace('ì', '')
                        title = title.strip()
                    except:
                        print(f"Could not find title for {product_url}, skipping")
                        continue
                    
                    # Extract brand - try to find it on the product page
                    try:
                        brand_element = soup3.find(class_='product-brand')
                        if brand_element:
                            brand = brand_element.text.strip()
                        else:
                            # Try to find in breadcrumbs
                            breadcrumbs = soup3.find(class_='breadcrumbs')
                            if breadcrumbs:
                                brand_links = breadcrumbs.find_all('a')
                                if len(brand_links) >= 2:
                                    brand = brand_links[1].text.strip()
                                else:
                                    brand = "Better Music"  # Default fallback
                            else:
                                brand = "Better Music"  # Default fallback
                    except:
                        brand = "Better Music"  # Default fallback
                    
                    # Extract SKU and RRP
                    try:
                        sku_element = soup3.find(class_='musipos-msrp')
                        if sku_element:
                            sku_text = sku_element.text
                            if ' - RRP $' in sku_text:
                                sku_rrp = sku_text.split(' - RRP $')
                                sku = sku_rrp[0].strip()
                                rrp = sku_rrp[1].strip()
                            else:
                                sku = sku_text.strip()
                                rrp = "N/A"
                        else:
                            # Try alternative approach to find SKU
                            sku_element = soup3.find(class_='product attribute sku')
                            if sku_element:
                                sku_value = sku_element.find(class_='value')
                                if sku_value:
                                    sku = sku_value.text.strip()
                                else:
                                    sku = "Unknown"
                            else:
                                sku = "Unknown"
                                
                            rrp = "N/A"
                    except Exception as sku_error:
                        print(f"Error extracting SKU: {str(sku_error)}")
                        sku = "Unknown"
                        rrp = "N/A"
                    
                    # Extract price
                    try:
                        price_container = soup3.find(class_='product-add-form')
                        if price_container:
                            price_element = price_container.find(class_='price')
                            if price_element:
                                price = price_element.text.replace('$', '').replace(',', '').strip()
                            else:
                                price = "N/A"
                        else:
                            # Try alternative price selectors
                            price_element = soup3.find(class_='price-box price-final_price')
                            if price_element:
                                price_span = price_element.find(class_='price')
                                if price_span:
                                    price = price_span.text.replace('$', '').replace(',', '').strip()
                                else:
                                    price = "N/A"
                            else:
                                price = "N/A"
                    except:
                        price = "N/A"
                    
                    # Extract image
                    try:
                        image_container = soup3.find(class_='gallery__item')
                        if image_container:
                            image_tag = image_container.find('img')
                            if image_tag and 'src' in image_tag.attrs:
                                image = image_tag['src']
                            else:
                                image = "N/A"
                        else:
                            # Try alternative image selectors
                            image_tag = soup3.find('img', class_='product-image-photo')
                            if image_tag and 'src' in image_tag.attrs:
                                image = image_tag['src']
                            else:
                                image = "N/A"
                    except:
                        image = "N/A"
                    
                    # Extract description
                    try:
                        description_container = soup3.find(class_='data item content')
                        if description_container:
                            description = description_container.text.strip()
                        else:
                            # Try alternative description selectors
                            description_container = soup3.find(class_='product attribute description')
                            if description_container:
                                description = description_container.text.strip()
                            else:
                                description = "No description available."
                    except:
                        description = "No description available."
                    
                    # Check stock availability
                    try:
                        stock_element = soup3.find(class_='stock available')
                        if stock_element:
                            stock_avaliable = 'y'
                        else:
                            stock_avaliable = 'n'
                    except:
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
                            upload_to_ftp(file_path, file_name)
                            print("Sheet saved successfully")
                        except Exception as e:
                            print(f"Error occurred while saving the Excel file: {str(e)}")
                    
                    # Add a pause to be gentle with the server
                    time.sleep(3)
                    
                except Exception as product_error:
                    print(f"Error processing product {item_number}: {str(product_error)}")
                    print(traceback.format_exc())
                    # Continue with next product even if this one fails
            
                # Check if we have a next page
                next_page = soup2.find('a', class_='next')
                
                if not next_page or 'href' not in next_page.attrs:
                    print(f"No next page found for category {category_url}")
                    break
                    
                page_num += 1
                
            except Exception as page_error:
                print(f"Error processing page {page_num}: {str(page_error)}")
                print(traceback.format_exc())
                break
    
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
