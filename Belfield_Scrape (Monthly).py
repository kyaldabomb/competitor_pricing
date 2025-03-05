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

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)




item_number = 0

items_scrapped = 0

for t in range(1000):

    time.sleep(0.3)


    print(f'Scraping page {t+1}...')

    r = session.get(f'https://www.belfieldmusic.com.au/search?page={str(t+1)}&q=+&type=product')
    while True:
        try:

            r.html.render(timeout=10)
            break
        except:
            continue


    for x in r.html.absolute_links:
        #print(x)

        if '/products/' in x:
            item_number +=1
            #print(f'Scraping item {str(item_number)}')
            time.sleep(0.3)

            url = x

            if url in url_list:
                print(f'Item {str(item_number)} already in sheet.')
                continue
            items_scrapped +=1

            while True:

                try:

                    while True:

                        r = requests.get(url)

                        if r.status_code == 430:
                            print('Page limit reached, waitng 5 mins')
                            time.sleep(300)
                            continue

                        else:
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

            description = soup.find(class_ = 'product-tabs__panel').text

            description = description.replace('\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')
            description = description.replace('\n\n\n', '\n\n')

            try:

                stock = soup.find(
                    class_='purchase-details__buttons purchase-details__spb--false product-is-unavailable').text
                stock_avaliable = 'n'

            except:
                stock_avaliable = 'y'

            today = datetime.now()

            date = today.strftime('%m %d %Y')

            sheet.append([sku, brand, title, price, url, image, description, date, stock_avaliable])
            print(f'Item {str(item_number)} scraped successfully')



            if int(items_scrapped)%100 == 0:
                print(f'Saving Sheet... Please wait....')

                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Belfield.xlsx")

                except:
                    print(f"Error occurred while saving the Excel file")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Belfield.xlsx")

except:
    print(f"Error occurred while saving the Excel file")