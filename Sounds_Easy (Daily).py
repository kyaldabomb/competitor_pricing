from bs4 import BeautifulSoup
import requests, pprint
from requests_html import HTMLSession
from send2trash import send2trash
import openpyxl
import os, time
from datetime import datetime, timedelta


session = HTMLSession()


wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sounds_Easy.xlsx")
sheet = wb['Sheet']

item_number = 0

items_scrapped = 0

for sheet_line in range(2, sheet.max_row+1):

    item_number += 1

    time_last_scrapped = sheet['H' + str(sheet_line)].value

    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 2 days ago, skipping...')

    else:
        url = sheet['E' + str(sheet_line)].value

        while True:

            r = requests.get(url)

            if r.status_code == 430:
                print('Page limit reached, waitng 5 mins')
                time.sleep(300)
                continue

            else:
                break
        items_scrapped += 1

        soup = BeautifulSoup(r.content, 'html.parser')

        try:

            title = soup.find(class_='product_name').text

        except:
            continue
        if 'open box' in title.lower():
            continue

        try:

            brand = soup.find(class_='vendor').text
            brand = brand.replace('\n', '\n')
            brand = brand.strip()



        except:
            brand = 'N/A'

        try:
            sku = soup.find(class_='sku').text
            sku = sku.strip()
        except:
            sku = 'N/A'

        try:
            price = soup.find(class_='price price--sale').text
            price = price.replace('$', '').strip()
        except:
            price = 'N/A'

        print(f'Price: {price}')

        image = soup.find(class_='image__container')

        try:

            for x in image:
                try:
                    image = x['src']
                except:
                    pass

        except:
            image = 'N/A'

        try:

            description = soup.find(itemprop='description').text
            while '\n\n\n' in description:
                description = description.replace('\n\n\n', '\n\n')
        except:
            description = 'Description not avaliable.'

        try:
            stock = soup.find(class_='purchase-details__buttons purchase-details__spb--true product-is-unavailable').text
            if 'sold' in stock.lower():
                stock_avaliable = 'n'
            else:

                stock_avaliable = 'y'

        except:
            stock_avaliable = 'y'
        today = datetime.now()

        date = today.strftime('%m %d %Y')

        print(f'Item {str(item_number)} scraped successfully')

        sheet['A' + str(sheet_line)].value = sku
        sheet['B' + str(sheet_line)].value = brand
        sheet['C' + str(sheet_line)].value = title
        sheet['D' + str(sheet_line)].value = price
        try:
            sheet['F' + str(sheet_line)].value = image
        except:
            sheet['F' + str(sheet_line)].value = 'N/A'

        sheet['G' + str(sheet_line)].value = description
        sheet['H' + str(sheet_line)].value = date
        sheet['I' + str(sheet_line)].value = stock_avaliable

        if int(items_scrapped) % 50 == 0:
            print(f'Saving Sheet... Please wait....')

            try:
             wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sounds_Easy.xlsx")
            except:
                print(f"Error occurred while saving the Excel file:")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sounds_Easy.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")







