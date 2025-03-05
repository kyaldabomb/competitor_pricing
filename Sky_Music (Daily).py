import openpyxl
import requests, pprint
from bs4 import BeautifulSoup
import re, math
from requests_html import HTMLSession
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import Workbook
import os, time
from send2trash import send2trash
from datetime import datetime, timedelta


options = webdriver.ChromeOptions()
options.add_argument("start-minimized")
#options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("window-size=10,10")




#s=Service(ChromeDriverManager().install())
# s = Service(r'\\SERVER\Python\chromedriver.exe')
# driver = webdriver.Chrome(service=s, options=options)
#driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')
driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )





session = HTMLSession()
wb = openpyxl.load_workbook(fr"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sky_Music.xlsx")
sheet = wb['Sheet']





item_number = 0
items_scrapped = 0

for sheet_line in range(2, sheet.max_row+1):

    item_number += 1

    time_last_scrapped = sheet['H' + str(sheet_line)].value
    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')

    else:

        url = sheet['E'+str(sheet_line)].value

        try:

            r = driver.get(url)


        except:
            continue

        html = driver.page_source

        soup2 = BeautifulSoup(html, features="lxml")

        try:

            brand = soup2.find(class_='vendor').text.strip()

        except:
            continue
        print(brand)

        try:

            sku = soup2.find(class_='sku').text.strip()

        except:
            continue

        if brand == 'Ernie Ball':
            sku = sku.replace('P0', '')

        if brand.lower() == 'orange':
            sku = f'{sku}AUSTRALIS'

        title = soup2.find(class_='product_name').text.strip()

        price = soup2.find(class_='current_price').text.strip()
        price = price.replace('$', '')
        price = price.replace(',', '')

        # itemcounter += 1

        print(f'\nScraping Item {str(item_number)}\nSKU: {sku}\nPrice: {price}\n')

        image = 'Not yet scraped'
        description = 'Not yet scraped'

        try:

            image = soup2.find(class_='gallery-cell is-selected')
            image = image.find('a')['href']

        except:
            image = 'Not yet scraped'

        try:

          description = soup2.find(class_='station-tabs-content-inner').text

        except:
            description = 'N/A'

        stock_avaliable = 'n'

        for x in soup2.find_all(class_='location-stock-status'):
            # print(x)
            if 'In Stock' in x or "Low Stock" in x:
                stock_avaliable = 'y'

        # try:
        #     stock = soup2.find(class_='sold_out').text
        #     print(f'stock: {stock}')
        #     if stock == '':
        #         stock_avaliable = 'y'
        #     else:
        #
        #         stock_avaliable = 'n'
        #
        # except:
        #     stock_avaliable = 'y'

        today = datetime.now()

        date = today.strftime('%m %d %Y')

        sheet['A' + str(sheet_line)].value = sku
        sheet['B' + str(sheet_line)].value = brand
        sheet['C' + str(sheet_line)].value = title
        sheet['D' + str(sheet_line)].value = price
        sheet['F' + str(sheet_line)].value = image
        sheet['G' + str(sheet_line)].value = description
        sheet['H' + str(sheet_line)].value = date
        sheet['I' + str(sheet_line)].value = stock_avaliable

        items_scrapped +=1
        print(f'Item {str(item_number)} scraped successfully')

        time.sleep(8)

        if int(items_scrapped) % 20 == 0:
            print(f'Saving Sheet... Please wait....')

            try:
                wb.save(fr"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sky_Music.xlsx")
            except:
                print(f"Error occurred while saving the Excel file:")

try:
    wb.save(fr"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sky_Music.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")