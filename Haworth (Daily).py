import requests
from bs4 import BeautifulSoup
import pprint, time, math, os

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import openpyxl
from send2trash import send2trash
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
from seleniumbase import Driver
from requests_html import HTMLSession



options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
# options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
#options.add_argument("window-size=10,10")
# s=Service(ChromeDriverManager().install())
# s=ChromeDriverManager().install()
# driver = webdriver.Chrome(s, options=options)
#driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')

# s=Service(r'\\SERVER\Python\chromedriver.exe')
# driver = webdriver.Chrome(service=s,options=options)

# stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#         )
# session = HTMLSession()
#
# driver = Driver(uc=True)

# s = Service(r'\\SERVER\Python\chromedriver.exe')
# driver = webdriver.Chrome(service=s, options=options)
driver = webdriver.Chrome(options=options)

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Haworth.xlsx")
sheet = wb['Sheet']

item_number = 0
items_scrapped = 0

for sheet_line in range(2, sheet.max_row+1):
    item_number += 1

    time_last_scrapped = sheet['H' + str(sheet_line)].value
    try:
        string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    except:
        string_datetime_conversion = datetime.strptime("01 01 2000", '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')
    else:
        try:
            items_scrapped+=1
            url = sheet['E'+str(sheet_line)].value
            brand = sheet['E' + str(sheet_line)].value
            r = driver.get(url)
            # while True:
            #     try:
            #
            #         r.html.render(timeout=10)
            #         break
            #     except:
            #         continue
            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')
            #pprint.pprint(soup)



            try:
                price = soup.find(class_='price')

            except:
                price = soup.find(class_='price sale')
            price = price.find('span').text
            price = price.replace('\t\t\t\t', '')
            price = price.replace('\t', '')
            price = price.replace('\n', '')
            price = price.replace('$', '')
            print(price)

            image = soup.find(class_='swiper-zoom-container')
            image = image.find('img')['src']

            description = soup.find(class_='page-content full-width')
            description = description.find(class_='standard container').text
            description = description.replace('\n\n\n', '\n\n')

            sku = soup.find(class_='sku').text
            sku = sku.replace('SKU: ', '')
            print(sku)

            stock = soup.find(class_='iia-container').text

            if 'available' in stock.lower():
                stock_avaliability = 'y'
            else:
                stock_avaliability = 'n'

            today = datetime.now()

            date = today.strftime('%m %d %Y')
            sheet['A' + str(sheet_line)].value = sku
            sheet['D' + str(sheet_line)].value = price
            sheet['F' + str(sheet_line)].value = image
            sheet['G' + str(sheet_line)].value = description
            sheet['H' + str(sheet_line)].value = date
            sheet['I' + str(sheet_line)].value = stock_avaliability

            print(f'Item {str(item_number)} scraped successfully')

            if int(items_scrapped) % 3 == 0:
                print(f'Saving Sheet... Please wait....')

                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Haworth.xlsx")

                except:
                    print(f"Error occurred while saving the Excel file:")

        except AttributeError:
            sheet.delete_rows(sheet_line, 1)
            sheet_line -= 1

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Haworth.xlsx")

except:
    print(f"Error occurred while saving the Excel file:")