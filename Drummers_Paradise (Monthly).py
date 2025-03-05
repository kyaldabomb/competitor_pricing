import requests, pprint, math, time
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from openpyxl import Workbook
import os, time
import openpyxl
from pathlib import Path
from datetime import datetime, timedelta

session = HTMLSession()

url = 'https://drumfactory.com.au/'

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Drummers_Paradise.xlsx")
sheet = wb['Sheet']

url_list = []

item_number = 0

items_scrapped = 0

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)

while True:
    r = requests.get(url)

    if r.status_code == 200:
        break
    else:
        print('Page limit reached, trying again in 5 minutes')
        time.sleep(250)

soup = BeautifulSoup(r.content, 'html.parser')

soup = soup.find(class_='top top--nav is-mobile-responsive')
soup = soup.find(class_='top__links')

collection_url_list = []

for link in soup.find_all('a'):
    url = link['href']
    if 'collection' not in url:
        continue
    collection_url_list.append(fr"https://drumfactory.com.au{link['href']}")

for mainlink in collection_url_list:
    while True:
        r = requests.get(mainlink)

        if r.status_code == 200:
            break
        else:
            print('Page limit reached, trying again in 5 minutes')
            time.sleep(250)
    category = mainlink.split()
    soup = BeautifulSoup(r.content, 'html.parser')
    number_of_products = soup.find(id='product_count').text.strip().split(' ')[5]
    number_of_pages = math.ceil(float(number_of_products)/30)
    print(number_of_pages)

    for pages in range(int(number_of_pages)):

        try:
            url = fr'{mainlink}?page={str(int(pages)+1)}'
            r = requests.get(fr'{mainlink}?page={str(int(pages)+1)}')
        except:
            continue

        while True:

            if r.status_code == 200:
                break
            else:
                print('Page limit reached, trying again in 5 minutes')
                time.sleep(250)
                r = requests.get(fr'{mainlink}?page={str(int(pages) + 1)}')

        soup = BeautifulSoup(r.content, 'html.parser')

        for product in soup.find_all(class_='card__content'):
            item_number +=1

            try:
                link = product('a')[0]
            except:
                continue

            url = f"https://drumfactory.com.au{link['href']}"

            if url in url_list:
                print(f'Item {str(item_number)} already in sheet.')
                continue
            items_scrapped +=1

            while True:
                r2 = session.get(url)

                if r2.status_code == 200:
                    while True:
                        try:

                            r2.html.render(timeout=10)
                            break
                        except:
                            continue
                    break
                else:
                    print('Page limit reached, trying again in 5 minutes')
                    time.sleep(250)
            soup2 = BeautifulSoup(r2.content, 'html.parser')

            pre_title = soup2.find(class_='column is-full product-page__title').text

            pre_title = pre_title.split('Product Code:')
            title = pre_title[0].replace('\n','').strip()

            brand = title.split(' ')[0]
            try:
                sku = pre_title[1].replace('\n','').strip()
            except:
                continue
            image = soup2.find(class_='column is-full')
            image = image.find('img')['data-flickity-lazyload']
            image = image.split('?')[0]
            image = f'https:{image}'
            description = soup2.find(class_='tabs__content is-open').text
            price = soup2.find(id='price_display').text
            price = price.replace('\n', '').strip()
            price = price.replace('$', '')
            price = price.replace(',', '')
            print(price)


            stock = soup2.find(id='stock_level').text
            if int(stock) > 0:
                current_stock = 'y'
            else:
                current_stock = 'n'


            today = datetime.now()

            date = today.strftime('%m %d %Y')

            sheet.append([sku, brand, title, price, url, image, description, date, current_stock])
            print(f'Item {str(item_number)} scraped successfully')


            if int(items_scrapped)%100 == 0:
                print(f'Saving Sheet... Please wait....')
                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Drummers_Paradise.xlsx")
                except:
                    print(f"Error occurred while saving the Excel file:")
try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Drummers_Paradise.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")