import requests, math, openpyxl
from bs4 import BeautifulSoup
import pprint
from datetime import datetime, timedelta

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Jade.xlsx")
sheet = wb['Sheet']

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)


item_number = 0

items_scrapped = 0


for page in range(150):

    url = f'https://www.jademcaustralia.com.au/collections/all?page={page+1}'

    try:
        r = requests.get(url)
    except:
        continue

    soup = BeautifulSoup(r.content, 'html.parser')

    # pprint.pprint(soup)

    for x in soup.find_all(class_='indiv-product'):
        title = x.find(class_='grid__image')['title']
        post_url = x.find(class_='grid__image')['href']

        brand = title.split(' ')[0]

        item_number+=1


        url2 = f'https://www.jademcaustralia.com.au{post_url}'

        if url2 in url_list:
            print(f'Item {str(item_number)} already in sheet.')
            continue

        items_scrapped +=1

        r = requests.get(url2)

        soup2 = BeautifulSoup(r.content, 'html.parser')

        sku = soup2.find(class_='indiv-product-sku-text').text

        sku = f'{sku}JD'

        RRP = soup2.find(class_='product-page--pricing')
        RRP = RRP.find(class_='money').text.replace('$', '')

        print(RRP)


        description = soup2.find(class_='product-description-section-wrapper').text

        try:

            image_url = soup2.find(class_='product-single__photo')['data-zoom-img'].split('?')[0]

        except:
            continue

        today = datetime.now()

        date = today.strftime('%m %d %Y')

        sheet.append([sku, brand, title, RRP, url2, image_url, description, date])

        print(f'Item {str(item_number)} scraped successfully')

        if int(items_scrapped) % 30 == 0:
            print(f'Saving Sheet... Please wait....')
            wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Jade.xlsx")



wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Jade.xlsx")
