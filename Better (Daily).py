import requests, pprint
from bs4 import BeautifulSoup
import re, math
from requests_html import HTMLSession
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os, time, openpyxl
from send2trash import send2trash
from datetime import datetime, timedelta

session = HTMLSession()

options = webdriver.ChromeOptions()
options.add_argument("start-minimized")
#options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("window-size=10,10")


#s=Service(ChromeDriverManager().install())
# s=ChromeDriverManager().install()
# driver = webdriver.Chrome(s, options=options)
#driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')

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

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Better.xlsx")
sheet = wb['Sheet']

url_list = []

#driver.minimize_window()

html = driver.page_source


soup = BeautifulSoup(html)
#time.sleep(10)

item_number = 0

items_scrapped = 0

for sheet_line in range(2, sheet.max_row+1):
    item_number += 1

    time_last_scrapped = sheet['H' + str(sheet_line)].value
    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')

    else:
        url = sheet['E' + str(sheet_line)].value
        brand = sheet['B' + str(sheet_line)].value
        items_scrapped += 1

        r = driver.get(url)
        html = driver.page_source
        soup3 = BeautifulSoup(html)
        try:

            title = soup3.find(class_='page-title-wrapper').text
            title = title.replace('Ä', '')
            title = title.replace('ì', '')
            title = title.strip()
        except:
            continue
        sku_rrp = soup3.find(class_='musipos-msrp').text
        sku_rrp = sku_rrp.split(' - RRP $')
        # print(sku_rrp)
        sku = sku_rrp[0]
        rrp = sku_rrp[1]

        price = soup3.find(class_='product-add-form')
        price = price.find(class_='price').text
        price = price.replace('$', '')

        image = soup3.find(class_='gallery__item')
        image = image.find('img')['src']

        description = soup3.find(class_='data item content').text
        #print(description)

        try:

            stock = soup3.find(class_='stock available').text

            stock_avaliable = 'y'
        except:
            stock_avaliable = 'n'

        today = datetime.now()

        date = today.strftime('%m %d %Y')  ###URL FOR FINAL PRODUCT, NEED TO ENTER AND SCRAPE FOR ALL INFO

        print(f'Item {str(item_number)} scraped successfully')

        sheet['B' + str(sheet_line)].value = brand
        sheet['C' + str(sheet_line)].value = title
        sheet['D' + str(sheet_line)].value = price
        sheet['F' + str(sheet_line)].value = image
        sheet['G' + str(sheet_line)].value = description
        sheet['H' + str(sheet_line)].value = date
        sheet['I' + str(sheet_line)].value = stock_avaliable


        items_scrapped += 1

        if int(items_scrapped) % 15 == 0:
            print(f'Saving Sheet... Please wait....')

            try:
                wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Better.xlsx")
            except:
                print(f"Error occurred while saving the Excel file:")

try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Better.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")
# for x in soup.find_all(class_='brands-grid__link'):
#     brand_url = x['href']
#     brand = x.text
#
#     r = driver.get(brand_url)
#     html = driver.page_source
#     soup2 = BeautifulSoup(html)
#
#     for xx in soup2.find_all(class_='item product product-item'):
#
#         item_number+= 1
#
#         product_url = xx.find(class_='product-item-link')['href']
#
#         if product_url in url_list:
#             print(f'Item {str(item_number)} already in sheet.')
#             continue
#         items_scrapped += 1
#
#         r = driver.get(product_url)
#         html = driver.page_source
#         soup3 = BeautifulSoup(html)
#
#         title = soup3.find(class_='page-title-wrapper').text
#         title = title.replace('Ä','')
#         title = title.replace('ì', '')
#         title = title.strip()
#         sku_rrp = soup3.find(class_='musipos-msrp').text
#         sku_rrp = sku_rrp.split(' - RRP $')
#         #print(sku_rrp)
#         sku = sku_rrp[0]
#         rrp = sku_rrp[1]
#
#         price = soup3.find(class_='product-add-form')
#         price = price.find(class_='price').text
#         price = price.replace('$', '')
#
#
#         image = soup3.find(class_='gallery__item')
#         image = image.find('img')['src']
#
#         description = soup3.find(class_='data item content').text
#         print(description)
#
#         today = datetime.now()
#
#         date = today.strftime('%m %d %Y')
#
#         sheet.append([sku, brand, title, price, product_url, image, description, date])
#         print(f'Item {str(item_number)} scraped successfully')
#
#         if int(items_scrapped) % 20 == 0:
#             print(f'Saving Sheet... Please wait....')
#             wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Better.xlsx")
#
# wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Better.xlsx")





