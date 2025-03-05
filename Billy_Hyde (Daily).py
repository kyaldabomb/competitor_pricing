import requests, pprint, openpyxl
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime, timedelta



wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Billy_Hyde.xlsx")
sheet = wb['Sheet']

items_scrapped = 0

item_number = 0
counter = 0

for sheet_line in range(2, sheet.max_row+1):

    sheet_line-=counter

    further_break = ''

    item_number +=1

    time_last_scrapped = sheet['H' + str(sheet_line)].value
    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')

    else:
        try:
            url = sheet['E'+str(sheet_line)].value

            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')

            sku = soup.find(class_='product_sku pb-md-3').text
            sku = sku.replace('\n', '')
            sku = sku.replace('SKU: ', '')

            price = soup.find(class_='price').text
            price = price.replace('$', '')
            price = price.replace(',', '')
            title = soup.find(class_='page-title').text.strip()
            brand = soup.find(class_='m-brand-tooltip')
            brand = brand.find('img')['title']
            #print(brand)
            image = 'Not Scraped'
            description = 'Not Scraped'

            stock_avaliability = 'n'

            try:
                stock = soup.find(class_='stock yes d-block d-md-inline')
                stock_avaliability = 'y'

            except:
                pass

            try:
                stock = soup.find(class_='stock yes')
                stock_avaliability = 'y'

            except:
                pass

            today = datetime.now()

            date = today.strftime('%m %d %Y')

            sheet['A' + str(sheet_line)].value = sku
            sheet['B' + str(sheet_line)].value = brand
            sheet['C' + str(sheet_line)].value = title
            sheet['D' + str(sheet_line)].value = price
            sheet['F' + str(sheet_line)].value = image
            sheet['G' + str(sheet_line)].value = description
            sheet['H' + str(sheet_line)].value = date
            sheet['I' + str(sheet_line)].value = stock_avaliability


            items_scrapped += 1

            print(f'Item {str(item_number)} scraped successfully')


            if int(items_scrapped) % 50 == 0:
                print(f'Saving Sheet... Please wait....')
                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Billy_Hyde.xlsx")
                except:
                    print(f"Error occurred while saving the Excel file:")
        except:
            sheet.delete_rows(sheet_line,1)
            counter+=1

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


