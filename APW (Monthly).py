import requests, pprint, openpyxl
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

url = rf"https://www.australianpianowarehouse.com.au/product-category/digital-pianos-keyboards/?per_page=500"

r = requests.get(url)

soup = BeautifulSoup(r.content, 'html.parser')

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\APW.xlsx")
sheet = wb['Sheet']

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)

item_number = 0
items_scrapped = 0

for x in soup.find_all(class_='product-wrapper'):
    item_number+=1
    url = x.find(class_='product-element-top wd-quick-shop')('a')[0]['href']

    if url in url_list:
        print(f'Item {str(item_number)} already in sheet.')
        continue
    items_scrapped += 1

    title = x.find(class_='wd-entities-title').text
    price = x.find(class_='price').text
    price = price.replace('$', '')
    price = price.replace(',', '')
    brand = title.split(' ')[0]
    image = 'NOT SCRAPED'
    description = 'NOT SCRAPED'

    r = requests.get(url)

    soup2 = BeautifulSoup(r.content, 'html.parser')

    sku = soup2.find(class_='sku').text
    sku = sku.replace('\n', '')
    sku = sku.replace('\t', '')

    try:

        stock = soup.find(class_='stock-feeds-stock').text

        if 'in stock' in stock.lower():

            stock_avaliability = 'y'

        else:
            stock_avaliability = 'n'


    except:
        stock_avaliability = 'n'

    today = datetime.now()

    date = today.strftime('%m %d %Y')

    sheet.append([sku, brand, title, price, url, image, description, date, stock_avaliability])
    print(f'Item {str(items_scrapped)} scraped successfully')

    if int(items_scrapped) % 50 == 0:
        print(f'Saving Sheet... Please wait....')

        try:
            wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\APW.xlsx")
        except:
            print(f"Error occurred while saving the Excel file:")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\APW.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")
