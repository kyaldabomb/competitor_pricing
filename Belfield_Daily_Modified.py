import openpyxl
from bs4 import BeautifulSoup
import requests, pprint
from requests_html import HTMLSession
import os, time
from pathlib import Path
from datetime import datetime, timedelta
import traceback
import ftplib


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

# Import the standardized email notification function
try:
    from email_notifications import send_email_notification
except ImportError:
    # Fallback to local definition if module not available
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    def send_email_notification(success, items_count=0, error_msg="", scraper_name="Belfield"):
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
                msg['Subject'] = f"{scraper_name} Scraper Success: {items_count} items processed"
                body = f"The {scraper_name} web scraper ran successfully and processed {items_count} items."
            else:
                msg['Subject'] = f"{scraper_name} Scraper Failed"
                body = f"The {scraper_name} web scraper encountered an error: {error_msg}"
            
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

# Initialize HTML session
session = HTMLSession()

# Use local path instead of network path
file_path = "Pricing Spreadsheets/Belfield.xlsx"
file_name = "Belfield.xlsx"
wb = openpyxl.load_workbook(file_path)
sheet = wb['Sheet']

item_number = 0
items_scrapped = 0

try:
    for sheet_line in range(2, sheet.max_row+1):
        further_break = ''
        item_number += 1
        
        # Get the URL to scrape
        url = sheet['E'+str(sheet_line)].value
        
        # Handle HTTP requests with retry logic
        max_retries = 3
        for retry in range(max_retries):
            try:
                r = requests.get(url, timeout=30)
                
                if r.status_code == 430:
                    print('Page limit reached, waitng 5 mins')
                    time.sleep(300)
                    continue
                elif r.status_code == 404:
                    sheet.delete_rows(sheet_line, 1)
                    sheet_line -= 1
                    further_break = 'true'
                    break
                else:
                    break
            except requests.RequestException as e:
                print(f"Request error on try {retry+1}/{max_retries}: {str(e)}")
                if retry == max_retries - 1:  # Last retry
                    raise
                time.sleep(10)  # Wait before retrying
        
        if further_break == 'true':
            continue
            
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(r.content, 'html.parser')
        
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
            print(f"Could not find title for item {item_number}, URL: {url}")
            continue
        
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
                    image = 'N/A'
        except:
            image = 'N/A'
        
        # Get description
        try:
            description = soup.find(class_='product-tabs__panel').text
            description = description.replace('\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')
        except:
            description = 'N/A'
        
        # Check stock availability at Bass Hill, Online Stock, or BM 3PL - VIC
        try:
            stock_avaliable = 'y'  # Default to not available
            
            # Look for the CNC results container that has store-specific stock info
            cnc_container = soup.find('div', id='cnc-results-container')
            
            if cnc_container:
                # Find all store outlets
                outlets = cnc_container.find_all('li')
                
                for outlet in outlets:
                    # Check if this is Bass Hill, Online Stock, or BM 3PL - VIC
                    store_details = outlet.find('div', class_='cnc-store-details')
                    if store_details:
                        store_text = store_details.get_text()
                        
                        # Check if it's Bass Hill, Online Stock, or BM 3PL - VIC
                        if 'Bass Hill' in store_text or 'Online Stock' in store_text or 'BM 3PL' in store_text:
                            # Check the availability status for this outlet
                            availability = outlet.find('p', class_='cnc-heading-availability')
                            if availability:
                                # If it has the 'available' class (not 'unavailable'), mark as in stock
                                if 'cnc-heading-available' in availability.get('class', []) and \
                                   'cnc-heading-unavailable' not in availability.get('class', []):
                                    stock_avaliable = 'y'
                                    break  # Found stock at one location, no need to check others
            else:
                # Fallback to the old method if CNC container not found
                unavailable = soup.find(class_='purchase-details__buttons purchase-details__spb--false product-is-unavailable')
                
                # Also check for the "IN STOCK" text that appears when item is available
                in_stock_elem = soup.find('p', class_='in-stock')
                if in_stock_elem and 'IN STOCK' in in_stock_elem.get_text().upper():
                    stock_avaliable = 'y'
                elif not unavailable:
                    stock_avaliable = 'y'
                else:
                    stock_avaliable = 'y'
                    
        except Exception as e:
            print(f"Error checking stock availability: {str(e)}")
            stock_avaliable = 'y'  # Default to available if error
        
        # Get current date
        today = datetime.now()
        date = today.strftime('%m %d %Y')
        
        # Update the Excel sheet
        sheet['A'+ str(sheet_line)].value = sku
        sheet['B'+ str(sheet_line)].value = brand
        sheet['C'+ str(sheet_line)].value = title
        sheet['D'+ str(sheet_line)].value = price
        sheet['F'+ str(sheet_line)].value = image
        sheet['G'+ str(sheet_line)].value = description
        sheet['H'+ str(sheet_line)].value = date
        sheet['I' + str(sheet_line)].value = stock_avaliable
        
        items_scrapped += 1
        print(f'Item {str(item_number)} scraped successfully')
        
        # Save periodically
        if int(items_scrapped) % 10 == 0:
            print(f'Saving Sheet... Please wait....')
            try:
                wb.save(file_path)
                upload_to_ftp(file_path, file_name)
            except Exception as e:
                print(f"Error occurred while saving the Excel file: {str(e)}")
    
    try:
        # Final save
        wb.save(file_path)
        upload_to_ftp(file_path, file_name)
        print(f"Scraping completed successfully. Added {items_scrapped} new items.")
    
        # Import the FTP helper and upload immediately
        try:
            from ftp_helper import upload_to_ftp
            upload_success = upload_to_ftp(file_path, file_name)
            if upload_success:
                print(f"Uploaded {file_name} to FTP immediately after completion")
            else:
                print(f"Failed to upload {file_name} to FTP, will try again at the end of workflow")
        except Exception as ftp_error:
            print(f"Error with immediate FTP upload: {str(ftp_error)}")
    
        # Send email notification with explicit scraper name
        send_email_notification(True, items_scrapped, scraper_name="Belfield Daily")
    except Exception as final_error:
        print(f"Error in final save and upload: {str(final_error)}")
        print(traceback.format_exc())
    
except Exception as e:
    error_message = str(e)
    full_traceback = traceback.format_exc()
    print(f"Error in scraping: {error_message}")
    print(f"Traceback:\n{full_traceback}")
    
    try:
        wb.save(file_path)
        upload_to_ftp(file_path, file_name)
        print("Saved progress before error")
    except:
        print("Could not save progress after error")
    
    send_email_notification(False, error_msg=f"{error_message}\n\nFull traceback:\n{full_traceback}", scraper_name="Belfield Daily")
