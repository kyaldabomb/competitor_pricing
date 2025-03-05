import requests, math, openpyxl
from bs4 import BeautifulSoup
import pprint
from datetime import datetime, timedelta


wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Pro_Music.xlsx")
sheet = wb['Sheet']

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)


item_number = 0

items_scrapped = 0

url = 'https://www.promusicaustralia.com.au'

r = requests.get(url)

soup = BeautifulSoup(r.content, 'html.parser')

for x in soup.find_all(class_='list-group-item'):

    brand = x.text
    post_url = x['href']

    url2 = f'{url}{post_url}'

    #print(url2)

    try:

        r = requests.get(url2)

    except:
        continue

    soup2 = BeautifulSoup(r.content, 'html.parser')

    try:
        num_products = soup2.find(class_='btn-text').text
    except:
        continue
    num_products = num_products.replace('\n', '').split(' ')[0]
    num_pages = math.ceil(float(num_products)/48)

    for pages in range(num_pages):
        #print(pages+1)

        url3 = f'{url2}/?pgnum={pages}'

        r = requests.get(url3)

        soup3 = BeautifulSoup(r.content, 'html.parser')

        for products in soup3.find_all(class_='thumbnail-image'):

            item_number+= 1

            product_url = products['href']

            if product_url in url_list:
                print(f'Item {str(item_number)} already in sheet.')
                continue
            items_scrapped += 1
            title = products.find('img')['alt']
            img = products.find('img')['src']
            img = img.replace('assets', 'full')
            image_url = f'https://www.promusicaustralia.com.au{img}'


            r = requests.get(product_url)

            soup4 = BeautifulSoup(r.content, 'html.parser')

            RRP = soup4.find(class_='productprice productpricetext').text.replace('\n', '')

            RRP = RRP.replace('$', '')
            RRP = RRP.replace(',', '')
            sku = soup4.find(class_='sku').text.split(' ')[1]

            description = soup4.find(class_='productdetails').text.replace('\n\n', '\n')

            today = datetime.now()

            date = today.strftime('%m %d %Y')

            sheet.append([sku, brand, title, RRP, product_url, image_url, description, date])
            print(f'Item {str(item_number)} scraped successfully')

            if int(items_scrapped) % 30 == 0:
                print(f'Saving Sheet... Please wait....')
                wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Pro_Music.xlsx")

wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Pro_Music.xlsx")

