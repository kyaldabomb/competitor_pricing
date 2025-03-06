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

try:
    # Load workbook at the start
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['Sheet']
    
    # Get existing URLs to avoid duplicates
    url_list = []
    for x in range(2, sheet.max_row+1):
        url = sheet['E'+str(x)].value
        if url:
            url_list.append(url)
    
    print(f"Found {len(url_list)} existing URLs in the spreadsheet")
    
    # Initialize HTML session for JavaScript-rendered pages
    from requests_html import HTMLSession
    session = HTMLSession()
    
    item_number = 0
    items_scrapped = 0
    
    # MONTHLY SCRAPING CODE - search for new products
    # Limit the pages to check (30 instead of 1000)
    max_pages = 30
    
    for t in range(max_pages):
        time.sleep(1)  # Increased pause to be gentler with the server
        print(f'Scraping page {t+1} of max {max_pages}...')
        
        # Make request to the page with proper error handling
        try:
            r = session.get(f'https://www.belfieldmusic.com.au/search?page={str(t+1)}&q=+&type=product', timeout=30)
            r.html.render(timeout=30, sleep=2)  # Increase timeout and add sleep
        except Exception as e:
            print(f"Error loading page {t+1}: {str(e)}")
            # Try one more time
            try:
                time.sleep(10)
                r = session.get(f'https://www.belfieldmusic.com.au/search?page={str(t+1)}&q=+&type=product', timeout=30)
                r.html.render(timeout=30, sleep=2)
            except Exception as retry_e:
                print(f"Failed to load page {t+1} after retry: {str(retry_e)}")
                continue  # Skip this page and move to next
        
        # Check if we got valid content
        if not r.html or not r.html.absolute_links:
            print(f"No valid content on page {t+1}, skipping")
            continue
        
        # Find all product links
        found_items = False
        new_items_on_page = 0
        all_links = list(r.html.absolute_links)
        
        # Process only product links (much faster than processing one by one)
        product_links = [x for x in all_links if '/products/' in x]
        print(f"Found {len(product_links)} products on page {t+1}")
        
        for url in product_links:
            item_number += 1
            
            # Skip if already in sheet
            if url in url_list:
                print(f'Item {str(item_number)} already in sheet.')
                continue
            
            found_items = True
            new_items_on_page += 1
            items_scrapped += 1
            
            # Now scrape the product page
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    r = requests.get(url, timeout=30)
                    if r.status_code == 430:
                        print('Page limit reached, waiting 30 seconds')
                        time.sleep(30)
                        retry_count += 1
                        continue
                    elif r.status_code != 200:
                        print(f"Got status code {r.status_code}, retrying")
                        time.sleep(5)
                        retry_count += 1
                        continue
                    else:
                        break
                except Exception as e:
                    print(f"Request error: {str(e)}")
                    time.sleep(5)
                    retry_count += 1
                    
            if retry_count == max_retries:
                print(f"Failed to fetch {url} after {max_retries} attempts, skipping")
                continue
                
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Extract product data
            sku = 'N/A'
            brand = 'N/A'
            title = 'N/A'
            price = 'N/A'
            image = 'N/A'
            description = 'N/A'
            stock_avaliable = 'n'  # Default to not available
            
            try:
                sku_elem = soup.find(class_='sku')
                if sku_elem:
                    sku = sku_elem.text.strip()
            except:
                pass
                
            try:
                brand_elem = soup.find(class_='vendor')
                if brand_elem:
                    brand = brand_elem.text.strip()
                    if brand.lower() == 'orange':
                        sku = f'{sku}AUSTRALIS'
            except:
                pass
                
            try:
                title_elem = soup.find(class_='product_name')
                if title_elem:
                    title = title_elem.text.strip()
                else:
                    print(f"Could not find title for {url}, skipping")
                    continue
            except:
                print(f"Could not find title for {url}, skipping")
                continue
                
            try:
                price_elem = soup.find(class_='price-ui')
                if price_elem:
                    price = price_elem.text.strip()
                    if price.count('$') > 1:
                        price = price.split('$')[1]
                    price = price.replace('$', '')
            except:
                pass
                
            # Get image
            try:
                image_container = soup.find(class_='image__container')
                if image_container:
                    for img in image_container.find_all('img'):
                        if 'data-src' in img.attrs:
                            image = img['data-src']
                            break
                        elif 'src' in img.attrs:
                            image = img['src']
                            break
            except:
                pass
                
            # Get description
            try:
                description_elem = soup.find(class_='product-tabs__panel')
                if description_elem:
                    description = description_elem.text
                    description = description.replace('\n', '\n\n')
                    description = description.replace('\n\n\n', '\n\n')
            except:
                pass
                
            # Check stock availability
            try:
                # Try to find the "Out of Stock" or "Sold Out" message
                unavailable = soup.find(class_='purchase-details__buttons purchase-details__spb--false product-is-unavailable')
                if unavailable:
                    stock_avaliable = 'n'
                else:
                    # If no "Out of Stock" message, check for "Add to Cart" button
                    add_to_cart = soup.find('button', {'name': 'add'})
                    if add_to_cart and 'disabled' not in add_to_cart.attrs:
                        stock_avaliable = 'y'
            except:
                # Default to 'n' if we can't determine stock status
                stock_avaliable = 'n'
                
            # Get current date
            today = datetime.now()
            date = today.strftime('%m %d %Y')
            
            # Add to Excel sheet
            sheet.append([sku, brand, title, price, url, image, description, date, stock_avaliable])
            url_list.append(url)  # Add to our list to avoid duplicates in this run
            
            print(f'Item {str(item_number)} scraped successfully')
            
            # Save periodically
            if int(items_scrapped) % 5 == 0:
                print(f'Saving Sheet... Please wait....')
                try:
                    wb.save(file_path)
                    print("Periodic save successful")
                except Exception as e:
                    print(f"Error occurred while saving the Excel file: {str(e)}")
            
            # Add a pause to be gentle with the server
            time.sleep(1)
        
        # Save after each page
        print(f'Saving after page {t+1}...')
        wb.save(file_path)
        
        # If no new items found on this page, we might be at the end
        if new_items_on_page == 0 and t > 0:  # Skip this check for the first page
            print("No new items found on this page, might be at the end.")
            break
            
        # Exit early if we've processed enough items to avoid timeout
        if items_scrapped >= 100:
            print(f"Reached {items_scrapped} items, exiting early to avoid timeout")
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
    
    # Make sure wb is defined before trying to save
    if 'wb' in locals():
        try:
            wb.save(file_path)
            print("Saved progress before error")
        except Exception as save_error:
            print(f"Could not save progress after error: {str(save_error)}")
    
    send_email_notification(False, error_msg=f"{error_message}\n\nFull traceback:\n{full_traceback}")
    sys.exit(1)  # Exit with error code
