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
    
    # Better Music brands page - try the main page and search instead
    # The brands page might have changed or be protected
    print("Trying alternative approach to find products...")
    url = 'https://www.bettermusic.com.au/catalogsearch/result/?q=&product_list_limit=36'
    print(f"Accessing search page: {url}")
    
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
    
    # Wait for the page to load properly
    time.sleep(10)
    html = driver.page_source
    
    # Debug the HTML to see what we're getting
    print("Parsing HTML response...")
    
    # Try different parsing approaches
    soup = BeautifulSoup(html, features="lxml")
    
    # Debug the page structure
    print("Page title:", soup.title.text if soup.title else "No title found")
    
    item_number = 0
    items_scrapped = 0
    
    # Loop through all brands - try multiple selectors to find brands
    print("Starting to process brands")
    brands_links = soup.find_all(class_='brands-grid__link')
    
    # If no brands found with the first selector, try alternatives
    if len(brands_links) == 0:
        print("Trying alternative brand selectors...")
        brands_links = soup.find_all('a', class_='brand-item')
        
        if len(brands_links) == 0:
            # Try a more general approach
            brand_container = soup.find('div', class_='brandContainer')
            if brand_container:
                brands_links = brand_container.find_all('a')
            else:
                # Try even more general approach - look for links with 'brand' in URL
                all_links = soup.find_all('a', href=True)
                brands_links = [link for link in all_links if 'brand' in link['href'].lower()]
                
    print(f"Found {len(brands_links)} brands to process")
    
    for x in brands_links:
        try:
            brand_url = x['href']
            brand = x.text.strip()
            print(f"\nProcessing brand: {brand} at {brand_url}")
            
            # Add retry logic for brand page access
            max_retries = 3
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
            
            # Find all products for this brand
            products = soup2.find_all(class_='item product product-item')
            print(f"Found {len(products)} products for brand {brand}")
            
            for xx in products:
                try:
                    item_number += 1
                    
                    # Get product URL
                    product_link = xx.find(class_='product-item-link')
                    if not product_link:
                        print(f"Could not find product link for item {item_number}, skipping")
                        continue
                        
                    product_url = product_link['href']
                    
                    # Skip if already in the spreadsheet
                    if product_url in url_list:
                        print(f'Item {str(item_number)} already in sheet, skipping')
                        continue
                    
                    print(f"Processing new product: {product_url}")
                    
                    # Add retry logic for product page access
                    max_retries = 3
                    for retry in range(max_retries):
                        try:
                            r = driver.get(product_url)
                            break
                        except Exception as e:
                            if retry == max_retries - 1:
                                raise
                            print(f"Retry {retry+1}/{max_retries} for product {item_number}: {str(e)}")
                            time.sleep(5)
                    
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
                    
                    # Extract SKU and RRP
                    try:
                        sku_rrp = soup3.find(class_='musipos-msrp').text
                    except:
                        print(f"Could not find SKU for {product_url}, skipping")
                        continue
                        
                    sku_rrp = sku_rrp.split(' - RRP $')
                    sku = sku_rrp[0]
                    
                    try:
                        rrp = sku_rrp[1]
                    except:
                        print(f"Could not parse RRP from {sku_rrp}, skipping")
                        continue
                    
                    # Extract price
                    try:
                        price_container = soup3.find(class_='product-add-form')
                        price = price_container.find(class_='price').text
                        price = price.replace('$', '')
                        price = price.replace(',', '')
                    except:
                        price = "N/A"
                        print(f"Could not find price for {product_url}")
                    
                    # Extract image
                    try:
                        image_container = soup3.find(class_='gallery__item')
                        image = image_container.find('img')['src']
                    except:
                        image = "N/A"
                        print(f"Could not find image for {product_url}")
                    
                    # Extract description
                    try:
                        description = soup3.find(class_='data item content').text
                    except:
                        description = "No description available."
                        print(f"Could not find description for {product_url}")
                    
                    # Check stock availability
                    try:
                        stock = soup3.find(class_='stock available').text
                        stock_avaliable = 'y'
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
        
        except Exception as brand_error:
            print(f"Error processing brand {brand}: {str(brand_error)}")
            print(traceback.format_exc())
                # End of product processing
            
        # After processing all products on this page, check if there's a next page
        try:
            # Find the next page link and navigate to it
            next_page_link = soup.find('a', class_='action next')
            if next_page_link and 'href' in next_page_link.attrs:
                next_page_url = next_page_link['href']
                print(f"Moving to next page: {next_page_url}")
                
                # Add retry logic for next page access
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        r = driver.get(next_page_url)
                        break
                    except Exception as e:
                        if retry == max_retries - 1:
                            raise
                        print(f"Retry {retry+1}/{max_retries} for page {page_num+1}: {str(e)}")
                        time.sleep(5)
                
                # Wait for page to load
                time.sleep(5)
                html = driver.page_source
                soup = BeautifulSoup(html, features="lxml")
                
                # Find products on the new page
                products = soup.find_all(class_='item product product-item')
                if len(products) == 0:
                    products = soup.find_all(class_='product-item-info')
                if len(products) == 0:
                    products = soup.find_all('li', class_='product')
                
                page_num += 1
            else:
                print("No next page found, ending pagination")
                break
        except Exception as page_error:
            print(f"Error moving to next page: {str(page_error)}")
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
