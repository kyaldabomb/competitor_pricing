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

#DJ CITY SCRAPE

# options = webdriver.ChromeOptions()
# options.add_argument("start-maximized")
#
# # options.add_argument("--headless")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# #options.add_argument("window-size=10,10")
# #s=Service(ChromeDriverManager().install())
# s=ChromeDriverManager().install()
# driver = webdriver.Chrome(s, options=options)
# #driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
# options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
#options.add_argument("window-size=10,10")
# s=Service(ChromeDriverManager(version='114.0.5735.90').install())
# s=ChromeDriverManager(version='114.0.5735.90').install()
# driver = webdriver.Chrome(s, options=options)

# s=Service(r'\\SERVER\Python\chromedriver.exe')
# driver = webdriver.Chrome(service=s,options=options)
driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )


wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\DJ_City.xlsx")
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

            try:

                r2 = driver.get(f'{url}?prod_products%5Bpage%5D={str(pages + 1)}')

            except:
                continue
            html = driver.page_source
            soup3 = BeautifulSoup(html, 'html.parser')
            title = soup3.find(class_='product_title entry-title').text
            price = soup3.find(class_='price').text
            price = price.replace("\n", "")
            price = price.replace("$", "")
            description = soup3.find(class_='woocommerce-product-details__short-description').text
            sku = soup3.find(class_='sku').text

            today = datetime.now()

            date = today.strftime('%m %d %Y')

            image = soup3.find(class_='lozad')['src']

            try:

                stock = soup3.find(class_='stock in-stock').text

                if 'accepting' in stock.lower():
                    stock_avaliable = 'n'

                else:
                    stock_avaliable = 'y'

            except:
                stock_avaliable = 'n'

            sheet['C' + str(sheet_line)].value = title
            sheet['D' + str(sheet_line)].value = price
            sheet['F' + str(sheet_line)].value = image
            sheet['G' + str(sheet_line)].value = description
            sheet['H' + str(sheet_line)].value = date
            sheet['I' + str(sheet_line)].value = stock_avaliable

            items_scrapped += 1

            print(f'Item {str(item_number)} scraped successfully')

            if int(items_scrapped) % 50 == 0:
                print(f'Saving Sheet... Please wait....')

                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\DJ_City.xlsx")
                except:
                    print(f"Error occurred while saving the Excel file: {str(e)}")


        except:
            sheet.delete_rows(sheet_line,1)
            counter+=1

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\DJ_City.xlsx")
except:
    print(f"Error occurred while saving the Excel file: {str(e)}")