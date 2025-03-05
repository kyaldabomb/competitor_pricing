import requests, pprint, openpyxl
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\APW.xlsx")
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

            url = sheet['E'+str(sheet_line)].value
            r = requests.get(url)

            soup = BeautifulSoup(r.content, 'html.parser')
            #pprint.pprint(soup)

            try:
                title = soup.find(class_='product_title entry-title wd-entities-title').text

                price = soup.find('p', class_='price').text
                price = price.replace('$', '')
                price = price.replace(',', '')
                price = price.replace('\n', '')
                image = 'NOT SCRAPED'

                image = soup.find(class_='attachment-woocommerce_single size-woocommerce_single wp-post-image')['src']


                #description = soup.find(class_='col-12 poduct-tabs-inner').text
                description = soup.find(class_='wc-tab-inner').text.strip()
                sku= soup.find(class_='sku').text
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

                sheet['C' + str(sheet_line)].value = title
                sheet['D' + str(sheet_line)].value = price
                sheet['F' + str(sheet_line)].value = image
                sheet['G' + str(sheet_line)].value = description
                sheet['H' + str(sheet_line)].value = date
                sheet['I' + str(sheet_line)].value = stock_avaliability
            except:
                pass

            items_scrapped += 1
            print(f'Item {str(items_scrapped)} scraped successfully')

            if int(items_scrapped) % 50 == 0:
                print(f'Saving Sheet... Please wait....')

                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\APW.xlsx")
                except:
                    print(f"Error occurred while saving the Excel file:")


            # sheet.delete_rows(sheet_line, 1)
            # counter += 1

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\APW.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")
