import openpyxl
import requests
from bs4 import BeautifulSoup
import pprint, time, math, os, traceback, sys, argparse
from datetime import datetime, timedelta

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run daily scraper for Mannys')
parser.add_argument('scraper', nargs='?', default='mannys_daily', 
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
            msg['Subject'] = f"Mannys Daily Scraper Success: {items_count} items updated"
            body = f"The Mannys daily web scraper ran successfully and updated {items_count} items."
        else:
            msg['Subject'] = "Mannys Daily Scraper Failed"
            body = f"The Mannys daily web scraper encountered an error:\n\n{error_msg}"
        
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
    # Use local path instead of network path
    file_path = "Pricing Spreadsheets/Mannys.xlsx"
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['Sheet']
    
    item_number = 0
    items_scrapped = 0
    driver = None
    
    # Function to create a fresh WebDriver
    def create_webdriver():
        print("Creating fresh WebDriver instance...")
        driver_instance = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        stealth(driver_instance,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        # Set page load timeout to prevent hanging
        driver_instance.set_page_load_timeout(60)
        print(f"New WebDriver created - Chrome version: {driver_instance.capabilities['browserVersion']}")
        return driver_instance
    
    # Create initial WebDriver
    driver = create_webdriver()
    restart_counter = 0
    
    print(f"Starting to process {sheet.max_row-1} items")
    
    for sheet_line in range(2, sheet.max_row+1):
        try:
            item_number += 1
            restart_counter += 1
            
            # Restart WebDriver every 50 items to prevent resource exhaustion
            if restart_counter >= 50:
                print("Restarting WebDriver to prevent resource exhaustion...")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(5)  # Give system time to clean up resources
                driver = create_webdriver()
                restart_counter = 0
                
            # Check if we need to scrape this item (based on last scrape date)
            time_last_scrapped = sheet['H' + str(sheet_line)].value
            if time_last_scrapped:
                try:
                    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
                    if string_datetime_conversion + timedelta(days=7) > datetime.today():
                        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')
                        continue
                except Exception as date_error:
                    print(f"Error parsing date {time_last_scrapped}: {str(date_error)}")
            
            # Get the URL and fetch the page
            url = sheet['E'+str(sheet_line)].value
            if not url:
                print(f"No URL for item {item_number}, skipping")
                continue
                
            print(f"Processing item {item_number}: {url}")
            
            # Add retry logic for resilience
            max_retries = 3
            success = False
            
            for retry in range(max_retries):
                try:
                    print(f"Attempt {retry+1} for {url}")
                    # Set a lower timeout for page load
                    driver.set_page_load_timeout(60)
                    r = driver.get(url)
                    # Add a small delay to let JS execute
                    time.sleep(3)
                    success = True
                    break
                except Exception as e:
                    print(f"Retry {retry+1}/{max_retries} for {url}: {str(e)}")
                    time.sleep(5 * (retry + 1))  # Exponential backoff
                    # If we're on the last retry, try restarting the driver
                    if retry == max_retries - 1:
                        try:
                            print("Restarting WebDriver after failed attempts...")
                            driver.quit()
                        except:
                            pass
                        time.sleep(5)
                        driver = create_webdriver()
                        restart_counter = 0
                        
                        # One last attempt with fresh driver
                        try:
                            driver.set_page_load_timeout(60)
                            r = driver.get(url)
                            time.sleep(3)
                            success = True
                        except Exception as final_e:
                            print(f"Final attempt failed: {str(final_e)}")
            
            # Skip this item if all attempts failed
            if not success:
                print(f"Skipping item {item_number} after all attempts failed")
                continue
                
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract price
            price = "N/A"
            
            # Try selling-price class
            try:
                price_element = soup.find(class_='selling-price')
                if price_element and price_element.text:
                    price = price_element.text.strip()
                    price = price.replace('$', '')
                    price = price.replace('\n', '')
                    price = price.replace(',', '')
            except Exception as e:
                print(f"Error with selling-price: {str(e)}")
            
            # If that failed, try item-price class
            if price == "N/A":
                try:
                    price_element = soup.find(class_='item-price')
                    if price_element and price_element.text:
                        price = price_element.text.strip()
                        price = price.replace('$', '')
                        price = price.replace('\n', '')
                        price = price.replace(',', '')
                except Exception as e:
                    print(f"Error with item-price: {str(e)}")
            
            # Extract description
            description = "N/A"
            try:
                description_div = soup.find('div', class_='text-cutoff-wrap')
                if description_div:
                    description = description_div.text.strip()
            except:
                try:
                    description = soup.find(class_='productInfo-content').text
                except:
                    print(f"Could not find description for {url}")
            
            # Extract image
            image = "N/A"
            try:
                image_element = soup.find(class_='product-detail-img')
                if image_element and 'src' in image_element.attrs:
                    image = f"https://www.mannys.com.au/{image_element['src']}"
            except Exception as e:
                print(f"Error getting image: {str(e)}")
            
            # Check stock availability
            stock_avaliable = 'n'
            try:
                stock_elements = soup.find_all(class_=lambda c: c and 'stock' in c.lower())
                for elem in stock_elements:
                    if elem.text and ('In Stock' in elem.text or 'Low Stock' in elem.text):
                        stock_avaliable = 'y'
                        break
            except Exception as e:
                print(f"Error checking stock: {str(e)}")
            
            # Get current date
            today = datetime.now()
            date = today.strftime('%m %d %Y')
            
            # Update the Excel sheet
            sheet['D' + str(sheet_line)].value = price
            sheet['F' + str(sheet_line)].value = image
            sheet['G' + str(sheet_line)].value = description
            sheet['H' + str(sheet_line)].value = date
            sheet['I' + str(sheet_line)].value = stock_avaliable
            
            items_scrapped += 1
            print(f'Item {str(item_number)} scraped successfully')
            
            # Add a longer pause between requests to avoid overloading the server
            # Randomize slightly to appear more like human behavior
            sleep_time = 5 + (item_number % 3)
            print(f"Waiting {sleep_time} seconds before next request...")
            time.sleep(sleep_time)
            
            # Save periodically
            if int(items_scrapped) % 10 == 0:
                print(f'Saving Sheet... Please wait....')
                try:
                    wb.save(file_path)
                    print("Sheet saved successfully")
                except Exception as e:
                    print(f"Error occurred while saving the Excel file: {str(e)}")
        
        except Exception as item_error:
            print(f"Error processing item {item_number}: {str(item_error)}")
            print(traceback.format_exc())
            # Continue with next item even if this one fails
    
    # Final save
    wb.save(file_path)
    print(f"Scraping completed successfully. Updated {items_scrapped} items.")
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
        if driver:
            driver.quit()
    except:
        pass
