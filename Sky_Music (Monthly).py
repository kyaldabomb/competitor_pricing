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
import os, time, json
from send2trash import send2trash
from datetime import datetime, timedelta


options = webdriver.ChromeOptions()
options.add_argument("start-minimized")
#options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("window-size=10,10")




#s=Service(ChromeDriverManager().install())
# s=Service(r'\\SERVER\Python\chromedriver.exe')
# driver = webdriver.Chrome(service=s,options=options)
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
wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sky_Music.xlsx")
sheet = wb['Sheet']


url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)

itemcounter = 0
items_scrapped = 0



for page in range(1000):
    url = f'https://skymusic.com.au/search?page={page+1}&type=product&q=%20'

    try:

      r = driver.get(url)
    except:
        continue

    html = driver.page_source

    soup = BeautifulSoup(html, features="lxml")

    for x in soup.find_all(class_='boost-sd__product-item boost-sd__product-item--noBorder boost-sd__product-item-grid-view-layout'):
        itemcounter +=1

        product_data_str = x['data-product']
        # Clean up the string (remove extra quotes and escape characters)
        product_data_str = product_data_str.replace('"', '"')
        product_data_str = product_data_str.replace('\n', '')
        product_data_json = json.loads(product_data_str)
        price = product_data_json['priceMin']
        title = product_data_json['images'][0]['alt']
        image = product_data_json['images'][0]['src']
        stock = product_data_json['variants'].replace('\n', '')
        stock = json.loads(stock)
        stock = stock[0]['available']

        if stock is True:
            stock_avaliable = 'y'
        else:
            stock_avaliable = 'n'

        # print(stock)
        # pprint.pprint(product_data_json)

        url2 = f'https://skymusic.com.au{x.find("a")["href"]}'
        if url2 in url_list:
            print(f'Item {str(itemcounter)} already in sheet.')
            continue
        items_scrapped+=1

        try:

          r = driver.get(url2)


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

        # itemcounter += 1

        print(f'\nScraping Item {str(itemcounter)}\nSKU: {sku}\nPrice: {price}\n')

        description = 'Not yet scraped'

        today = datetime.now()

        date = today.strftime('%m %d %Y')

        sheet.append([sku, brand, title, price, url2, image, description, date, stock_avaliable])
        print(f'Item {str(itemcounter)} scraped successfully')

        if int(items_scrapped) % 3 == 0:
            print(f'Saving Sheet... Please wait....')
            try:
                wb.save(fr"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sky_Music.xlsx")
            except:
                print(f"Error occurred while saving the Excel file:")
try:
    wb.save(fr"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sky_Music.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")