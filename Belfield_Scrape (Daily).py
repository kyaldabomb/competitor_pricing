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

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Belfield.xlsx")
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

            try:

                while True:

                    r = requests.get(url)

                    if r.status_code == 430:
                        print('Page limit reached, waitng 5 mins')
                        time.sleep(300)
                        continue

                    elif r.status_code == 404:
                        sheet.delete_rows(sheet_line, 1)
                        sheet_line-=1
                        further_break = 'true'
                        break


                    else:
                        break



                if further_break =='true':
                    break
                soup = BeautifulSoup(r.content, 'html.parser')

                try:
                    sku = soup.find(class_='sku').text.strip()
                except:
                    sku = 'N/A'

                brand = soup.find(class_='vendor').text.strip()
                if brand.lower() == 'orange':
                    sku = f'{sku}AUSTRALIS'

                title = soup.find(class_='product_name').text.strip()
                price = soup.find(class_='price-ui').text.strip()

                break

            except:
                print('Error, retrying')
                time.sleep(1)
                continue

        if further_break == 'true':
            continue

        if int(price.count('$')) > 1:
            price = price.split('$')
            price = price[1]

        price = price.replace('$', '')

        image = soup.find(class_='image__container')

        try:

            for x in image:
                try:
                    image = x['data-src']
                    break
                except:
                    image = 'N/A'
                    pass
        except:
            image = 'N/A'

        description = soup.find(class_='product-tabs__panel').text

        description = description.replace('\n', '\n\n')
        description = description.replace('\n\n\n', '\n\n')
        description = description.replace('\n\n\n', '\n\n')
        description = description.replace('\n\n\n', '\n\n')
        description = description.replace('\n\n\n', '\n\n')

        try:

            stock = soup.find(class_='purchase-details__buttons purchase-details__spb--false product-is-unavailable').text
            stock_avaliable = 'n'

        except:
            stock_avaliable = 'y'



        today = datetime.now()

        date = today.strftime('%m %d %Y')

        print(f'Item {str(item_number)} scraped successfully')

        sheet['A'+ str(sheet_line)].value = sku
        sheet['B'+ str(sheet_line)].value = brand
        sheet['C'+ str(sheet_line)].value = title
        sheet['D'+ str(sheet_line)].value = price
        sheet['F'+ str(sheet_line)].value = image
        sheet['G'+ str(sheet_line)].value = description
        sheet['H'+ str(sheet_line)].value = date
        sheet['I' + str(sheet_line)].value = stock_avaliable

        items_scrapped +=1

        if int(items_scrapped) % 50 == 0:
            print(f'Saving Sheet... Please wait....')

            try:
                wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Belfield.xlsx")
            except:
                print(f"Error occurred while saving the Excel file:")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Belfield.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")