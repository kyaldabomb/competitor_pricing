import requests, pprint, openpyxl
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime, timedelta


url = 'https://billyhydemusic.com.au/brand/'

r = requests.get(url)

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Billy_Hyde.xlsx")
sheet = wb['Sheet']

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)

items_scrapped = 0

item_number = 0

for x in BeautifulSoup(r.content, 'html.parser', parse_only=SoupStrainer('a')):
    if x.has_attr('href'):
        if 'brand' in x['href']:
            #print(x)
            url = x['href']
            brand = x.find(class_='m__all_brand_label').text

            for pages in range(10):

                r = requests.get(f'{url}?p={str(pages+1)}&product_list_limit=36')
                soup2 = BeautifulSoup(r.content, 'html.parser')
                try:
                    for xx in soup2.find_all(class_='col-6 col-lg-3 p-2'):
                        item_number += 1

                        url = xx.find('a')['href']
                        item_number += 1
                        if url in url_list:
                            print(f'Item {str(item_number)} already in sheet.')
                            continue
                        items_scrapped += 1
                        sku = xx.find(class_='product-sku').text
                        price = xx.find(class_='price').text
                        price = price.replace('$', '')
                        price = price.replace(',', '')
                        title = xx.find(class_='product-name').text.strip()


                        today = datetime.now()

                        date = today.strftime('%m %d %Y')

                        image = 'Not Scraped'
                        description = 'Not Scraped'

                        sheet.append([sku, brand, title, price, url, image, description, date])
                        print(f'Item {str(item_number)} scraped successfully')

                        if int(items_scrapped) % 50 == 0:
                            print(f'Saving Sheet... Please wait....')

                            try:
                                wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Billy_Hyde.xlsx")
                            except:
                                print(f"Error occurred while saving the Excel file:")

                except:
                    continue

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Billy_Hyde.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")


                #print(title)


# for x in soup.find_all(class_='letter-row js-brand-row'):
#
#     url = x.find_all('a')['href']
#     brand = x.find(class_='m__all_brand_label').text
#
#     r = requests.get(url)
#     soup2 = BeautifulSoup(r.content, 'html.parser')

    # for xx in soup2.find_all(class_= 'col-6 col-lg-3 p-2'):
    #     url = xx.find('a')['href']
    #     sku = xx.find(class_='product-sku').text
    #     price = xx.find(class_='price').text
    #     price = price.replace('$', '')
    #     price = price.replace(',', '')
    #     title = xx.find(class_='product-name').text.strip()
    #
    #
    #
    #     print(title)


