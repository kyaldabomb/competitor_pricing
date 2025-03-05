import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import openpyxl
from send2trash import send2trash
from datetime import datetime, timedelta

import pprint, time, math, os

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Acoustic_Centre.xlsx")
sheet = wb['Sheet']

url_list = []
item_number = 0

items_scrapped = 0

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)

r = requests.get(fr'https://www.acousticcentre.com.au/search?page=1&q=+&type=product')

soup = BeautifulSoup(r.content, 'html.parser')

soup = soup.find(class_='dropdown_container mega-menu mega-menu-5')
for brands in soup.find_all(class_='dropdown_column'):
    for xx in brands.find_all('a'):
        if 'Brands' in xx.text:
            continue
        else:
            brand = xx.text
            post_url = xx['href']

            brand_url = f'https://www.acousticcentre.com.au{post_url}'

            r = requests.get(brand_url)

            soup2 = BeautifulSoup(r.content, 'html.parser')

            #pprint.pprint(soup2)

            for yy in soup2.find_all(class_='product-info__caption'):
                title = yy.find(class_='title').text
                post_url = yy['href']
                product_url = f'https://www.acousticcentre.com.au{post_url}'
                item_number+=1

                if product_url in url_list:
                    print(f'Item {str(item_number)} already in sheet.')
                    continue
                else:
                    pass
                r = requests.get(product_url)
                soup3 = BeautifulSoup(r.content, 'html.parser')

                try:
                    sku = soup3.find(class_='sku').text.strip()
                except:
                    continue
                image = soup3.find(class_='image__container')
                image = image.find('img')['data-src']
                price = soup3.find(class_='price-ui')
                price = price.find(class_='price').text
                price = price.replace('$', '')
                price = price.replace(',', '')

                try:
                    description = soup3.find(id='tabs-2').text.strip()

                except:
                    'Description not avaliable.'
                print(description)

                stock = soup3.find(class_='purchase-details').text
                stock = stock.replace('\n', '')
                stock = stock.strip()

                if 'cart' in stock:
                    stock_avaliability = 'y'
                else:
                    stock_avaliability = 'n'

                today = datetime.now()

                date = today.strftime('%m %d %Y')

                items_scrapped+=1
                sheet.append([sku, brand, title, price, product_url, image, description, date, stock_avaliability])
                print(f'Item {str(item_number)} scraped successfully')

                if int(items_scrapped) % 20 == 0:
                    print(f'Saving Sheet... Please wait....')

                    try:
                        wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Acoustic_Centre.xlsx")
                    except:
                        print(f"Error occurred while saving the Excel file:")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Acoustic_Centre.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")




