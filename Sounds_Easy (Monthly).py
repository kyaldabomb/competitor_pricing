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

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)

item_number = 0

items_scrapped = 0

for t in range(1000):

    time.sleep(0.3)

    print(f'Scraping page {t+1}...')

    r = session.get(f'https://www.soundseasy.com.au/search?page={str(t+1)}&q=+&type=product')

    r.html.render(timeout=100)

    for x in r.html.absolute_links:

        if '/products/' in x:

            item_number+=1
            time.sleep(0.3)
            url = x
            if url in url_list:
                print(f'Item {str(item_number)} already in sheet.')

                continue

            while True:

                r = requests.get(url)

                if r.status_code == 430:
                    print('Page limit reached, waitng 5 mins')
                    time.sleep(300)
                    continue

                else:
                    break
            items_scrapped+=1

            soup = BeautifulSoup(r.content, 'html.parser')

            try:

                title = soup.find(class_ = 'product_name').text

            except:
                continue
            if 'open box' in title.lower():
                continue

            brand = soup.find(itemprop='brand').text

            try:
                sku = soup.find(itemprop='sku').text
            except:
                sku = 'N/A'

            try:
                price = soup.find(class_ = 'current_price').text
                price = price.replace('$', '').strip()
            except:
                price = 'N/A'

            image = soup.find(class_ = 'image__container')

            for x in image:
                try:
                    image = x['src']
                except:
                    pass

            try:

                description = soup.find(itemprop='description').text
                while '\n\n\n' in description:
                    description = description.replace('\n\n\n', '\n\n')
            except:
                description = 'Description not avaliable.'

            try:
                stock = soup.find(
                    class_='purchase-details__buttons purchase-details__spb--true product-is-unavailable').text
                if 'sold' in stock.lower():
                    stock_avaliable = 'n'
                else:

                    stock_avaliable = 'y'

            except:
                stock_avaliable = 'y'

            today = datetime.now()

            date = today.strftime('%m %d %Y')

            sheet.append([sku, brand, title, price, url, image, description, date, stock_avaliable])
            print(f'Item {str(item_number)} scraped successfully')

            if int(items_scrapped)%3 == 0:
                print(f'Saving Sheet... Please wait....')
                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sounds_Easy.xlsx")
                except:
                    print(f"Error occurred while saving the Excel file:")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Sounds_Easy.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")




