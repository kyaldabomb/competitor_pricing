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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scrapers_config import SCRAPERS

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run monthly scraper for Belfield')
parser.add_argument('scraper', nargs='?', default='belfield_monthly', 
                    help='Scraper name from config')
parser.add_argument('--start-page', type=int, default=1,
                    help='Starting page number')
parser.add_argument('--max-pages', type=int, default=1000,
                    help='Maximum number of pages to process')
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

# Setup Chrome driver for Selenium
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

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

print(f"Found {len(url_list)} existing URLs in spreadsheet")

item_number = 0
items_scrapped = 0
driver = None

try:
    # Initialize Selenium driver
    print("Setting up Chrome driver...")
    driver = setup_driver()
    
    # Test connection to website
    print("Testing connection to Belfield website...")
    driver.get('https://www.belfieldmusic.com.au')
    time.sleep(2)
    print("Successfully connected to website")
    
    # MONTHLY SCRAPING CODE - search for new products
    consecutive_empty_pages = 0
    max_empty_pages = 3  # Stop after 3 consecutive pages with no new products
    
    # Use page range from arguments
    start_page = args.start_page
    end_page = min(start_page + args.max_pages - 1, 1000)
    
    print(f"Scraping pages {start_page} to {end_page}")
    
    for page_num in range(start_page, end_page + 1):  # Use the specified range
        try:
            time.sleep(1)  # Be gentle with the server
            print(f'Scraping page {page_num}...')
            
            # Navigate to search page
            url = f'https://www.belfieldmusic.com.au/search?page={page_num}&q=+&type=product'
            driver.get(url)
            
            # Wait for page to load and check for products
            try:
                # Wait for either products or "no results" message
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "a[href*='/products/']") or
                             d.find_elements(By.CSS_SELECTOR, ".no-results, .empty-search")
                )
            except TimeoutException:
                print(f"Timeout on page {page_num}, checking what we have...")
            
            # Find all product links on the page
            product_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
            product_links = list(set([elem.get_attribute('href') for elem in product_elements if elem.get_attribute('href')]))
            
            print(f"Found {len(product_links)} product links on page {page_num}")
            
            # Filter out already scraped URLs
            new_product_links = [url for url in product_links if url not in url_list]
            print(f"Found {len(new_product_links)} new products to scrape")
            
            if len(new_product_links) == 0:
                consecutive_empty_pages += 1
                print(f"No new products on this page (consecutive empty: {consecutive_empty_pages})")
                
                # Check if we've hit the end of results
                if consecutive_empty_pages >= max_empty_pages:
                    print(f"No new products found on {max_empty_pages} consecutive pages. Ending search.")
                    break
                    
                # Check for "no more results" indicators
                no_results = driver.find_elements(By.CSS_SELECTOR, ".no-results, .empty-search, .end-of-results")
                if no_results:
                    print("Reached end of search results")
                    break
                    
                continue
            else:
                consecutive_empty_pages = 0  # Reset counter when we find new products
            
            # Scrape each new product
            for product_url in new_product_links:
                item_number += 1
                time.sleep(0.5)  # Polite delay between requests
                
                # Now scrape the product page using requests for speed
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        r = requests.get(product_url, timeout=30, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        
                        if r.status_code == 430:
                            print('Rate limit reached, waiting 5 mins')
                            time.sleep(300)
                            continue
                        elif r.status_code != 200:
                            print(f"Status code {r.status_code} for {product_url}")
                            if retry < max_retries - 1:
                                time.sleep(2)
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
                            print(f"Could not find title for {product_url}, skipping")
                            break
                            
                        try:
                            price = soup.find(class_='price-ui').text.strip()
                            if int(price.count('$')) > 1:
                                price = price.split('$')
                                price = price[1]
                            price = price.replace('$', '').replace(',', '')
                        except:
                            price = 'N/A'
                            
                        # Get image
                        try:
                            image = soup.find(class_='image__container')
                            image_url = 'N/A'
                            if image:
                                # Look for data-src or src attributes
                                for img_elem in image.find_all(['img', 'div']):
                                    if img_elem.get('data-src'):
                                        image_url = img_elem['data-src']
                                        break
                                    elif img_elem.get('src'):
                                        image_url = img_elem['src']
                                        break
                            image = image_url
                        except:
                            image = 'N/A'
                            
                        # Get description
                        try:
                            desc_elem = soup.find(class_='product-tabs__panel')
                            if desc_elem:
                                description = desc_elem.get_text(separator='\n', strip=True)
                                # Clean up the description
                                description = description.replace('\n\n\n', '\n\n')
                            else:
                                description = 'N/A'
                        except:
                            description = 'N/A'
                            
                        # Check stock availability
                        try:
                            unavailable = soup.find(class_='product-is-unavailable')
                            out_of_stock = soup.find(string=lambda text: 'out of stock' in text.lower() if text else False)
                            stock_available = 'n' if (unavailable or out_of_stock) else 'y'
                        except:
                            stock_available = 'y'
                            
                        # Get current date
                        today = datetime.now()
                        date = today.strftime('%m %d %Y')
                        
                        # Add to Excel sheet
                        sheet.append([sku, brand, title, price, product_url, image, description, date, stock_available])
                        url_list.append(product_url)  # Add to our tracking list
                        items_scrapped += 1
                        print(f'Item {item_number} scraped successfully: {title[:50]}...')
                        
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        if retry < max_retries - 1:
                            print(f'Error scraping product (attempt {retry + 1}/{max_retries}): {str(e)}')
                            time.sleep(2)
                        else:
                            print(f'Failed to scrape product after {max_retries} attempts: {product_url}')
                            print(f'Error: {str(e)}')
                
                # Save periodically
                if items_scrapped > 0 and items_scrapped % 10 == 0:
                    print(f'Saving progress... ({items_scrapped} items scraped so far)')
                    try:
                        wb.save(file_path)
                        print('Progress saved successfully')
                    except Exception as e:
                        print(f"Error saving Excel file: {str(e)}")
                        
        except Exception as page_error:
            print(f"Error on page {page_num}: {str(page_error)}")
            consecutive_empty_pages += 1
            if consecutive_empty_pages >= max_empty_pages:
                print("Too many consecutive errors, stopping scraper")
                break
    
    # Close the browser
    if driver:
        driver.quit()
        driver = None
    
    # Final save and upload
    try:
        wb.save(file_path)
        print(f"Scraping completed successfully. Added {items_scrapped} new items.")
        
        # Import the FTP helper and upload immediately
        try:
            if FTP_AVAILABLE:
                upload_success = upload_to_ftp(file_path, file_name)
                if upload_success:
                    print(f"Uploaded {file_name} to FTP immediately after completion")
                else:
                    print(f"Failed to upload {file_name} to FTP, will try again at the end of workflow")
            else:
                print("FTP not available, file saved locally only")
        except Exception as ftp_error:
            print(f"Error with immediate FTP upload: {str(ftp_error)}")
        
        # Send email notification (only once!)
        send_email_notification(True, items_scrapped)
        
    except Exception as final_error:
        print(f"Error in final save and upload: {str(final_error)}")
        print(traceback.format_exc())
    
except Exception as e:
    error_message = str(e)
    full_traceback = traceback.format_exc()
    print(f"Error in scraping: {error_message}")
    print(f"Traceback:\n{full_traceback}")
    
    # Clean up driver if it exists
    if driver:
        try:
            driver.quit()
        except:
            pass
    
    # Try to save any progress
    try:
        wb.save(file_path)
        print(f"Saved progress before error ({items_scrapped} items scraped)")
    except Exception as save_error:
        print(f"Could not save progress after error: {str(save_error)}")
    
    send_email_notification(False, error_msg=f"{error_message}\n\nFull traceback:\n{full_traceback}")
    sys.exit(1)  # Exit with error code
