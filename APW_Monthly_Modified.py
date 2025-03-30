import openpyxl
import requests
from bs4 import BeautifulSoup
import os
import time
import traceback
from datetime import datetime
import sys
import argparse

# Import helper functions
try:
    from ftp_helper import upload_to_ftp
    from email_notifications import send_email_notification
except ImportError:
    print("Error: ftp_helper.py or email_notifications.py not found.")
    print("Ensure these files are in the same directory or Python path.")
    sys.exit(1)

# --- Configuration and Argument Parsing ---

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run monthly scraper for Australian Piano Warehouse (APW)')
parser.add_argument('scraper', nargs='?', default='apw_monthly',
                    help='Scraper name (should be apw_monthly)')
args = parser.parse_args()
scraper_name = args.scraper

# Basic check if the scraper name matches
if scraper_name != "apw_monthly":
    print(f"Warning: Expected scraper name 'apw_monthly', but received '{scraper_name}'. Proceeding anyway.")

# Define file names and paths
file_name = "APW.xlsx"
file_path = f"Pricing Spreadsheets/{file_name}"
description = "Australian Piano Warehouse (Monthly)" # For notifications

# The main category URL to scrape for products
# Consider making this configurable or dynamically finding category pages if needed
# Increased per_page significantly - check if the site supports this value.
# High values might cause timeouts or get blocked. Test lower values (e.g., 100) if 500 fails.
category_url = "https://www.australianpianowarehouse.com.au/product-category/digital-pianos-keyboards/?per_page=100" # Reduced per_page for stability


# --- Main Script Logic ---

wb = None # Initialize for robust error handling
try:
    print(f"Starting {description} scraper...")
    print(f"Target Category URL: {category_url}")
    print(f"Loading workbook: {file_path}")

    # Check if the file exists before trying to load
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}. Please ensure the file was downloaded correctly.")
        # The download_files.py should create a blank one if missing from FTP.
        # If it still fails here, there might be a workflow issue.
        sys.exit(1)

    wb = openpyxl.load_workbook(file_path)
    sheet = wb['Sheet']

    # --- Read Existing URLs ---
    print("Reading existing URLs from the spreadsheet...")
    url_list = set() # Use a set for faster lookups
    for row in range(2, sheet.max_row + 1):
        url_value = sheet['E' + str(row)].value
        if url_value and isinstance(url_value, str) and url_value.startswith('http'):
            url_list.add(url_value.strip())
    print(f"Found {len(url_list)} existing URLs.")

    # --- Fetch Category Page ---
    print(f"Fetching category page: {category_url}")
    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            response = requests.get(category_url, timeout=60) # Increased timeout for potentially large page
            response.raise_for_status()
            print("Category page fetched successfully.")
            break # Success
        except requests.exceptions.RequestException as req_err:
            print(f"Category page request attempt {attempt + 1}/{max_retries} failed: {req_err}")
            if attempt == max_retries - 1:
                print("Max retries reached for category page. Exiting.")
                raise # Re-raise the last exception
            time.sleep(5 * (attempt + 1))

    if response is None:
        sys.exit(1) # Exit if category page fetch failed

    soup = BeautifulSoup(response.content, 'html.parser')

    # --- Process Products on Page ---
    item_number = 0
    items_added = 0
    products_on_page = soup.find_all(class_='product-wrapper')
    total_products_found = len(products_on_page)
    print(f"Found {total_products_found} product wrappers on the page.")

    for product_element in products_on_page:
        item_number += 1
        current_item_info = f"Product {item_number}/{total_products_found}"

        try:
            # Extract Product URL from category page item
            product_url_tag = product_element.find(class_='product-element-top') # More reliable parent?
            product_url = None
            if product_url_tag:
                 link_tag = product_url_tag.find('a')
                 if link_tag and 'href' in link_tag.attrs:
                     product_url = link_tag['href']

            if not product_url:
                print(f"{current_item_info}: Could not find product URL in wrapper. Skipping.")
                continue

            product_url = product_url.strip()

            # Check if URL already exists
            if product_url in url_list:
                # print(f'{current_item_info}: URL {product_url} already in sheet. Skipping.') # Reduce log noise
                continue

            print(f"\n{current_item_info}: NEW product found. URL: {product_url}")

            # Extract initial info from category page item (can be less reliable)
            title_tag = product_element.find(class_='wd-entities-title')
            title = title_tag.text.strip() if title_tag else "N/A"

            price_tag = product_element.find(class_='price')
            price = "N/A"
            if price_tag:
                 # Simplified price cleaning, may need refinement for ranges etc.
                 price_text = price_tag.text.strip()
                 cleaned_price = price_text.replace('$', '').replace(',', '').split()[0]
                 try:
                     float(cleaned_price)
                     price = cleaned_price
                 except ValueError:
                     print(f"{current_item_info}: Price text '{price_text}' could not be cleaned to number.")
                     price = "N/A"

            # Attempt brand extraction (less reliable method)
            brand = title.split(' ')[0] if title != "N/A" else "N/A"
            print(f"{current_item_info}: Title='{title}', Price='{price}', Brand (Guess)='{brand}'")

            # --- Fetch Individual Product Page for Details ---
            print(f"{current_item_info}: Fetching individual product page...")
            product_response = None
            for attempt in range(max_retries):
                try:
                    product_response = requests.get(product_url, timeout=30)
                    product_response.raise_for_status()
                    break # Success
                except requests.exceptions.RequestException as req_err:
                    print(f"{current_item_info}: Product page request attempt {attempt + 1}/{max_retries} failed: {req_err}")
                    if attempt == max_retries - 1:
                        print(f"{current_item_info}: Max retries reached for product page. Skipping item.")
                        raise # Re-raise to be caught by outer item loop try/except
                    time.sleep(5 * (attempt + 1))

            if product_response is None:
                continue # Skip item if fetching its page failed

            soup2 = BeautifulSoup(product_response.content, 'html.parser')

            # Extract details from product page (more reliable)
            sku_tag = soup2.find(class_='sku')
            sku = sku_tag.text.strip() if sku_tag else "N/A"

            # Extract image (similar to daily script)
            image_tag = soup2.find(class_='attachment-woocommerce_single size-woocommerce_single wp-post-image')
            image = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "N/A"

            # Extract description (similar to daily script)
            desc_tag = soup2.find(class_='wc-tab-inner')
            description_text = desc_tag.text.strip() if desc_tag else "N/A"

            # Extract stock status (similar to daily script - IMPORTANT: Use soup2!)
            stock_availability = 'n' # Default
            stock_tag = soup2.find(class_='stock-feeds-stock')
            if stock_tag:
                stock_text = stock_tag.text.lower()
                if 'in stock' in stock_text:
                    stock_availability = 'y'
            else:
                 # Optional: Add fallback checks like the daily script if needed
                 print(f"{current_item_info}: Could not find specific stock tag on product page. Defaulting stock to 'n'.")

            print(f"{current_item_info}: Details: SKU='{sku}', Stock='{stock_availability}'")

            # --- Append to Spreadsheet ---
            today = datetime.now()
            date_str = today.strftime('%m %d %Y')

            # Ensure data types match expectations (e.g., price as string or number)
            # Column Order: SKU, Brand, Title, Price, URL, Image, Description, Last Updated, In Stock
            new_row_data = [sku, brand, title, price, product_url, image, description_text, date_str, stock_availability]
            sheet.append(new_row_data)

            # Add the newly added URL to our set to prevent duplicates within this run
            url_list.add(product_url)
            items_added += 1
            print(f'{current_item_info}: Added successfully to sheet. Total items added so far: {items_added}')

            # --- Periodic Save and Upload ---
            if items_added > 0 and items_added % 25 == 0: # Save more frequently for monthly adds
                print(f'\nSaving sheet after {items_added} new items...')
                try:
                    wb.save(file_path)
                    print("Sheet saved locally.")
                    if not upload_to_ftp(file_path, file_name):
                         print("Periodic FTP upload failed. Continuing script.")
                except Exception as save_err:
                    print(f"Error occurred during periodic save/upload: {save_err}")
                    print(traceback.format_exc())

            # Add a delay
            time.sleep(3) # Slightly longer delay as we hit product pages

        except Exception as item_error:
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"Error processing {current_item_info} for URL {product_url}: {item_error}")
            print(traceback.format_exc())
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # Continue to the next product wrapper
            continue

    # --- Final Save and Upload ---
    print("\nFinished processing products from category page.")
    if items_added > 0:
        print(f"Attempting final save for {file_name}...")
        wb.save(file_path)
        print("Final local save successful.")

        if upload_to_ftp(file_path, file_name):
            print("Final FTP upload successful.")
        else:
            print("Final FTP upload failed.")
    else:
        print("No new items were added, skipping final save and upload.")

    # --- Success Notification ---
    print(f"\n{description} scraper completed successfully.")
    print(f"Products found on page: {total_products_found}")
    print(f"New items added to spreadsheet: {items_added}")
    send_email_notification(True, items_added, scraper_name=description)

except Exception as e:
    # --- Error Handling and Notification ---
    error_message = str(e)
    full_traceback = traceback.format_exc()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"An unexpected error occurred in the {description} scraper:")
    print(error_message)
    print(f"Traceback:\n{full_traceback}")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # Attempt to save progress
    if wb and items_added > 0: # Only save if workbook loaded and items were added
        try:
            print("Attempting to save progress before exiting due to error...")
            wb.save(file_path)
            print("Progress saved locally.")
            # upload_to_ftp(file_path, file_name) # Optionally upload partial file
        except Exception as save_error:
            print(f"Could not save progress after error: {save_error}")

    # Send failure email
    send_email_notification(False, items_added, error_msg=f"{error_message}\n\nFull traceback:\n{full_traceback}", scraper_name=description)
    sys.exit(1) # Indicate failure

finally:
    print(f"{description} script finished.")
