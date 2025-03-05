import requests, pprint
from bs4 import BeautifulSoup
import re, math
from requests_html import HTMLSession
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os, time, openpyxl
from send2trash import send2trash
from datetime import datetime, timedelta
import random
from seleniumbase import Driver




session = HTMLSession()

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Derringer.xlsx")
sheet = wb['Sheet']



item_number = 0
items_scrapped = 0




# options = webdriver.ChromeOptions()
# options.add_argument("start-minimized")
# #options.add_argument("--headless")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument("window-size=10,10")
# options.add_argument('--disable-blink-features=AutomationControlled')
#
# # disable pop-up blocking
# options.add_argument('--disable-popup-blocking')
#
# # start the browser window in maximized mode
# options.add_argument('--start-maximized')
#
# # disable extensions
# options.add_argument('--disable-extensions')
#
# # disable sandbox mode
# options.add_argument('--no-sandbox')
#
# # disable shared memory usage
# options.add_argument('--disable-dev-shm-usage')
#
# options.add_argument('ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors=yes')

#PROXY ="202.110.67.141:9091"
#options.add_argument('--proxy-server=%s' % PROXY)


# Set navigator.webdriver to undefined
# create a driver instance
# s=ChromeDriverManager().install()
# driver = webdriver.Chrome(s, options=options)
# driver = webdriver.Chrome(executable_path=r'\\SERVER\Python\chromedriver.exe', options=options)
#
# # Change the property value of the navigator for webdriver to undefined
# driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#
# # Step 3: Rotate user agents
# user_agents = [
#     # Add your list of user agents here
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
# ]
#
# # select random user agent
# user_agent = random.choice(user_agents)
#
# # pass in selected user agent as an argument
# options.add_argument(f'user-agent={user_agent}')
#
# #s=Service(ChromeDriverManager().install())
#
# #driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')
#
# stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#         )

driver = Driver(uc=True)

for sheet_line in range(2, sheet.max_row+1):
    item_number += 1

    time_last_scrapped = sheet['H' + str(sheet_line)].value
    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')

    else:
        url = sheet['E' + str(sheet_line)].value
        brand = sheet['B' + str(sheet_line)].value
        items_scrapped += 1  ###URL FOR FINAL PRODUCT, NEED TO ENTER AND SCRAPE FOR ALL INFO

        ######### Cloudflare Bypass #####
        #handle = driver.current_window_handle
        driver.service.stop()
        time.sleep(6)
        while True:
            try:
                driver = Driver(uc=True)
                break

            except:
                time.sleep(4)
                print("trying chome again")
                continue
        #driver.switch_to.window(handle)
        try:

            r = driver.get(url)
            time.sleep(10)
            html = driver.page_source

        except Exception as e:
            sheet.delete_rows(sheet_line, 1)
            sheet_line -= 1
            print(e)
            continue

        driver.quit()
        soup = BeautifulSoup(html)

        try:

            title = soup.find(class_='page-title').text

        except:
            continue
        title = title.replace('\n', '').strip()

        # price = soup.find(class_='price-wrapper').text
        pre_price = soup.find(class_='product-info-main')
        try:
            price = pre_price.find(class_='special-price').text
        except:
            price = soup.find(class_='price-wrapper').text
        price = price.replace('\n', '')
        price = price.replace('Special Price', '')
        price = price.replace('$', '')
        price = price.replace(',', '')

        # pre_price = soup.find(class_= 'product-info-main')
        # price = pre_price.find(class_='price').text

        # pprint.pprint(price)

        sku = soup.find(class_='product attribute sku').text

        sku = sku.replace('SKU', '').strip()

        if brand.lower() == 'tanglewood':
            sku = sku.replace('TANG_', '')
            if sku == 'UT14E':
                sku = 'TUT14E'
                print('bing')
                print('bong')

        if brand.lower() == 'orange':
            sku = sku.replace('ORAN_', '')
            if sku == 'CRUSHACOUSTIC30':
                sku = '8900101'
            if sku == 'CRUSHACOUSTIC30BK':
                sku = '8900102'
            sku = f'{sku}AUSTRALIS'

        # image = soup.find(class_ = 'gallery-placeholder')
        image = soup.find(class_='gallery-placeholder__image')

        try:

            image = image['src']

        except:
            image = 'NA'

        print(f'sku: {sku}')

        description = soup.find(class_='product attribute description').text
        description = description.replace('Derringers', 'Scarlett')
        print(f'description: {description}')
        print(f'price: {price}')

        try:
            stock = soup.find(class_='amstockstatus-status-container stock available')
            stock_avaliable = 'y'

        except:
            stock_avaliable = 'n'

        today = datetime.now()

        date = today.strftime('%m %d %Y')

        print(f'Item {str(item_number)} scraped successfully')

        sheet['B' + str(sheet_line)].value = brand
        sheet['C' + str(sheet_line)].value = title
        sheet['D' + str(sheet_line)].value = price
        sheet['F' + str(sheet_line)].value = image
        sheet['G' + str(sheet_line)].value = description
        sheet['H' + str(sheet_line)].value = date
        sheet['I' + str(sheet_line)].value = stock_avaliable

        items_scrapped += 1

        if int(items_scrapped) % 15 == 0:
            print(f'Saving Sheet... Please wait....')
            wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Derringer.xlsx")

wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Derringer.xlsx")






