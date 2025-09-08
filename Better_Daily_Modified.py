import openpyxl
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os, time
from datetime import datetime
import traceback
import ftplib
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore
import queue
from dataclasses import dataclass
from typing import Optional, Dict, Any


# Configuration
MAX_WORKERS = 5  # Number of parallel workers (adjust based on system and target site limits)
MAX_SELENIUM_INSTANCES = 3  # Limit concurrent Selenium instances to avoid memory issues
RATE_LIMIT_DELAY = 0.5  # Delay between requests to avoid overwhelming the server

# Thread-safe locks
excel_lock = Lock()  # For Excel file operations
selenium_semaphore = Semaphore(MAX_SELENIUM_INSTANCES)  # Limit Selenium instances
request_lock = Lock()  # For rate limiting


@dataclass
class ProductData:
    """Data class to hold product information"""
    sheet_line: int
    url: str
    sku: str = 'N/A'
    brand: str = 'N/A'
    title: str = 'N/A'
    price: str = 'N/A'
    image: str = 'N/A'
    description: str = 'N/A'
    stock_available: str = 'n'
    date: str = ''
    success: bool = False
    error: Optional[str] = None


def upload_to_ftp(file_path, file_name):
    """Upload file to FTP server"""
    print(f"\n==== Uploading {file_name} to FTP ====")
    try:
        ftp_password = os.environ.get('FTP_PASSWORD')
        if not ftp_password:
            print("FTP_PASSWORD not found in environment variables")
            return False
            
        session = ftplib.FTP('ftp.drivehq.com', 'kyaldabomb', ftp_password)
        
        if 'competitor_pricing' not in session.nlst():
            print("competitor_pricing directory not found, creating it...")
            session.mkd('competitor_pricing')
        
        session.cwd('competitor_pricing')
        
        with open(file_path, 'rb') as file:
            session.storbinary(f'STOR {file_name}', file)
            
        with open('upload_timestamp.txt', 'w') as f:
            f.write(f"Upload of {file_name} completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        with open('upload_timestamp.txt', 'rb') as file:
            session.storbinary('STOR upload_timestamp.txt', file)
            
        session.quit()
        print(f"File {file_name} uploaded to FTP successfully")
        return True
    except Exception as e:
        print(f"Error uploading to FTP: {str(e)}")
        return False


def create_driver():
    """Create a new Selenium WebDriver instance"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def check_stock_with_selenium(url):
    """Check stock availability using Selenium"""
    with selenium_semaphore:  # Limit concurrent Selenium instances
        driver = None
        try:
            driver = create_driver()
            driver.get(url)
            time.sleep(2)
            
            # Try to click stock check button
            try:
                button = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#cnc-container button"))
                )
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.ID, "cnc-results"))
                )
            except:
                pass  # Button might not exist or already clicked
            
            # Parse the page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            cnc_container = soup.find('div', id='cnc-results-container')
            
            if cnc_container:
                outlets = cnc_container.find_all('li')
                
                for outlet in outlets:
                    store_details = outlet.find('div', class_='cnc-store-details')
                    if store_details:
                        store_name_elem = store_details.find('strong')
                        if store_name_elem:
                            store_name = store_name_elem.get_text().strip()
                            
                            # Check if it's one of our target stores
                            if any(target in store_name for target in ['Bass Hill', 'Online Stock', 'BM 3PL - VIC']):
                                availability = outlet.find('p', class_='cnc-heading-availability')
                                if availability:
                                    classes = availability.get('class', [])
                                    if 'cnc-heading-available' in classes and 'cnc-heading-unavailable' not in classes:
                                        return 'y'
                return 'n'
            else:
                # Check general stock indicator
                in_stock_elem = soup.find('p', class_='in-stock')
                if in_stock_elem and 'IN STOCK' in in_stock_elem.get_text().upper():
                    return 'y'
                return 'n'
                
        except Exception as e:
            print(f"  Selenium error: {str(e)[:100]}")
            return 'y'  # Default to available on error
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass


def scrape_product(sheet_line: int, url: str, item_number: int) -> ProductData:
    """Scrape a single product"""
    result = ProductData(sheet_line=sheet_line, url=url)
    
    try:
        print(f"[Worker] Processing item {item_number}: {url[:50]}...")
        
        # Rate limiting
        with request_lock:
            time.sleep(RATE_LIMIT_DELAY)
        
        # Get basic product info
        response = requests.get(url, timeout=30)
        
        if response.status_code == 404:
            result.error = "404 - Page not found"
            return result
        elif response.status_code == 430:
            result.error = "430 - Rate limited"
            time.sleep(60)  # Wait if rate limited
            return result
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract SKU
        try:
            result.sku = soup.find(class_='sku').text.strip()
        except:
            pass
        
        # Extract Brand
        try:
            result.brand = soup.find(class_='vendor').text.strip()
            if result.brand.lower() == 'orange':
                result.sku = f'{result.sku}AUSTRALIS'
        except:
            pass
        
        # Extract Title (required)
        try:
            result.title = soup.find(class_='product_name').text.strip()
        except:
            result.error = "Could not find title"
            return result
        
        # Extract Price
        try:
            price = soup.find(class_='price-ui').text.strip()
            if price.count('$') > 1:
                price = price.split('$')[1]
            result.price = price.replace('$', '')
        except:
            pass
        
        # Extract Image
        try:
            image_container = soup.find(class_='image__container')
            for elem in image_container:
                try:
                    result.image = elem['data-src']
                    break
                except:
                    pass
        except:
            pass
        
        # Extract Description
        try:
            desc = soup.find(class_='product-tabs__panel').text
            desc = desc.replace('\n', '\n\n')
            while '\n\n\n' in desc:
                desc = desc.replace('\n\n\n', '\n\n')
            result.description = desc
        except:
            pass
        
        # Check stock with Selenium
        result.stock_available = check_stock_with_selenium(url)
        
        # Set date
        result.date = datetime.now().strftime('%m %d %Y')
        result.success = True
        
        print(f"[Worker] ✓ Item {item_number} complete - Stock: {'Yes' if result.stock_available == 'y' else 'No'}")
        
    except Exception as e:
        result.error = str(e)[:200]
        print(f"[Worker] ✗ Item {item_number} failed: {result.error[:100]}")
    
    return result


def update_excel_row(sheet, result: ProductData):
    """Update Excel sheet with product data (thread-safe)"""
    with excel_lock:
        row = str(result.sheet_line)
        sheet['A' + row].value = result.sku
        sheet['B' + row].value = result.brand
        sheet['C' + row].value = result.title
        sheet['D' + row].value = result.price
        sheet['F' + row].value = result.image
        sheet['G' + row].value = result.description
        sheet['H' + row].value = result.date
        sheet['I' + row].value = result.stock_available


def send_email_notification(success, items_count=0, error_msg="", scraper_name="Belfield"):
    """Send email notification"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        sender = "kyal@scarlettmusic.com.au"
        receiver = "kyal@scarlettmusic.com.au"
        password = os.environ.get('EMAIL_PASSWORD')
        
        if not password:
            print("Email password not found")
            return
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        
        if success:
            msg['Subject'] = f"{scraper_name} Success: {items_count} items"
            body = f"The {scraper_name} scraper processed {items_count} items successfully."
        else:
            msg['Subject'] = f"{scraper_name} Failed"
            body = f"Error: {error_msg}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP("mail.scarlettmusic.com.au", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Email notification sent")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


def main():
    """Main function with parallel processing"""
    file_path = "Pricing Spreadsheets/Belfield.xlsx"
    file_name = "Belfield.xlsx"
    
    print(f"Starting Belfield Parallel Scraper")
    print(f"Workers: {MAX_WORKERS}, Max Selenium: {MAX_SELENIUM_INSTANCES}")
    print("=" * 60)
    
    try:
        # Load workbook
        wb = openpyxl.load_workbook(file_path)
        sheet = wb['Sheet']
        
        # Prepare work items
        work_items = []
        for sheet_line in range(2, sheet.max_row + 1):
            url = sheet['E' + str(sheet_line)].value
            if url:
                work_items.append((sheet_line, url, len(work_items) + 1))
        
        print(f"Found {len(work_items)} items to process")
        
        # Process items in parallel
        items_processed = 0
        items_to_delete = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(scrape_product, item[0], item[1], item[2]): item 
                for item in work_items
            }
            
            # Process completed tasks
            for future in as_completed(future_to_item):
                result = future.result()
                
                if result.error == "404 - Page not found":
                    items_to_delete.append(result.sheet_line)
                elif result.success:
                    update_excel_row(sheet, result)
                    items_processed += 1
                    
                    # Save periodically
                    if items_processed % 10 == 0:
                        with excel_lock:
                            print(f"\n>>> Saving progress ({items_processed} items)...")
                            wb.save(file_path)
                            upload_to_ftp(file_path, file_name)
        
        # Delete 404 rows
        if items_to_delete:
            with excel_lock:
                for row in sorted(items_to_delete, reverse=True):
                    sheet.delete_rows(row, 1)
        
        # Final save
        wb.save(file_path)
        upload_to_ftp(file_path, file_name)
        
        print(f"\n{'=' * 60}")
        print(f"Scraping completed! Processed {items_processed} items successfully")
        
        send_email_notification(True, items_processed, scraper_name="Belfield Daily (Parallel)")
        
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Critical error: {error_msg}")
        
        try:
            wb.save(file_path)
            upload_to_ftp(file_path, file_name)
        except:
            pass
        
        send_email_notification(False, error_msg=error_msg, scraper_name="Belfield Daily (Parallel)")


if __name__ == "__main__":
    main()
