import openpyxl
from bs4 import BeautifulSoup
import requests, pprint
from requests_html import HTMLSession
from send2trash import send2trash
from openpyxl import Workbook
import os, time
from pathlib import Path
from datetime import datetime, timedelta





session = HTMLSession()

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Drummers_Paradise.xlsx")
sheet = wb['Sheet']

item_number = 0

items_scrapped = 0

for sheet_line in range(2, sheet.max_row+1):

    further_break = ''

    item_number +=1

    time_last_scrapped = sheet['H' + str(sheet_line)].value
    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')

    else:
        url = sheet['E'+str(sheet_line)].value

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
        title = pre_title[0].replace('\n', '').strip()

        brand = title.split(' ')[0]
        sku = pre_title[1].replace('\n', '').strip()
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

        if int(items_scrapped) % 100 == 0:
            print(f'Saving Sheet... Please wait....')

            try:
                wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Drummers_Paradise.xlsx")
            except:
                print(f"Error occurred while saving the Excel file:")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Drummers_Paradise.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")