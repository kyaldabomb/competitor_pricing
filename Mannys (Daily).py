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
from requests_html import HTMLSession
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import openpyxl
from send2trash import send2trash
from datetime import datetime, timedelta


# options = webdriver.ChromeOptions()
# options.add_argument("start-maximized")
# # options.add_argument("--headless")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# #options.add_argument("window-size=10,10")
# s=Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=s, options=options)
# #driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')
#
# stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#         )

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Mannys.xlsx")
sheet = wb['Sheet']

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
# options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
# options.add_argument("window-size=10,10")
# s=Service(ChromeDriverManager().install())
# s=ChromeDriverManager().install()
# driver = webdriver.Chrome(s, options=options)
# driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')

s = Service(r'\\SERVER\Python\chromedriver.exe')
# driver = webdriver.Chrome(service=s, options=options)
driver = webdriver.Chrome(options=options)


stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

item_number = 0
items_scrapped = 0

for sheet_line in range(2, sheet.max_row+1):
    item_number += 1

    time_last_scrapped = sheet['H' + str(sheet_line)].value
    string_datetime_conversion = datetime.strptime(time_last_scrapped, '%m %d %Y')
    if string_datetime_conversion + timedelta(days=7) > datetime.today():
        print(f'Item {str(item_number)} scrapped less than 7 days ago, skipping...')
    else:
        try:
            items_scrapped+=1
            url = sheet['E'+str(sheet_line)].value
            brand = sheet['E' + str(sheet_line)].value
            r = driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            pprint.pprint(soup)


            price = soup.find(class_='item-price').text
            price = price.replace('\n', '')
            price = price.replace('$', '')
            description = soup.find(class_='productInfo-content').text

            try:

                image = f"https://www.mannys.com.au/{soup.find(class_='product-detail-img')['src']}"

            except:
                image = "N/A"

            stock = soup.find(class_='stock-display').text

            try:
                stock = soup.find(class_='online-stock-status in-stock').text
                stock_avaliable = 'y'

            except:

                try:
                    stock = soup.find(class_='online-stock-statusin-stock').text
                    stock_avaliable = 'y'

                except:

                    stock_avaliable = 'n'


            today = datetime.now()

            date = today.strftime('%m %d %Y')
            sheet['D' + str(sheet_line)].value = price
            sheet['F' + str(sheet_line)].value = image
            sheet['G' + str(sheet_line)].value = description
            sheet['H' + str(sheet_line)].value = date
            sheet['I' + str(sheet_line)].value = stock_avaliable
            print(f'Item {str(item_number)} scraped successfully')

            if int(items_scrapped) % 3 == 0:
                print(f'Saving Sheet... Please wait....')

                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Mannys.xlsx")
                except:
                    print(f"Error occurred while saving the Excel file:")
        except AttributeError:
            sheet.delete_rows(sheet_line, 1)
            sheet_line -= 1
# r = requests.get(url)
#
# soup = BeautifulSoup(r.content, 'html.parser')
#
# brand_links = soup.find(class_='brand-links')
#
# for x in brand_links.find_all('li'):
#
#
#     brand = x.text
#     brand_url = x.find('a')['href']
#     url = f'{pre_url}{brand_url}'
#
#     if brand.lower() == 'orange':
#         r = driver.get(url)
#         html = driver.page_source
#         soup = BeautifulSoup(html, 'html.parser')
#
#         number_of_products_showing = soup.find(class_='page-end').text
#         number_of_brand_products_total = soup.find(class_= 'total').text
#         number_of_pages = math.ceil(float(number_of_brand_products_total)/float(number_of_products_showing))
#         #pprint.pprint(soup)
#
#         for _ in range(int(number_of_pages)+3):
#             try:
#                 element = driver.find_element(By.XPATH, "(//button[@class='btn cv-refresh'])[1]")
#
#                 actions = ActionChains(driver)
#                 actions.move_to_element(element).perform()
#                 time.sleep(1)
#             except:
#                 time.sleep(1)
#
#             driver.execute_script("arguments[0].click();", element)
#
#             html = driver.page_source
#
#             #pprint.pprint(html)
#
#         soup = BeautifulSoup(html, 'html.parser')
#
#         all_products = soup.find(id='product-grid')
#
#         for t in all_products.find_all(class_='product'):
#             item_number +=1
#
#
#             url = t.find('a')['href']
#             url = f'{pre_url}{url}'
#
#             if url in url_list:
#                 print(f'Item {str(item_number)} already in sheet.')
#                 continue
#
#             items_scrapped += 1
#             sku = t.find(class_='widget-productlist-code').text
#             #print(sku)
#             if 'OBX' in sku:
#                 continue
#
#             sku = sku.replace('ORA-', '')
#             if sku == 'CRUSH35RT':
#                 sku = '8900042AUSTRALIS'
#             if sku == 'CRUSH12':
#                 sku = '8900036AUSTRALIS'
#             if sku == 'CRUSH20':
#                 sku = '2900038AUSTRALIS'
#             if sku == 'CRUSH20RT':
#                 sku = '8900040AUSTRALIS'
#             if sku == 'CRUSHBASS25':
#                 sku = '8900044AUSTRALIS'
#             if sku == 'ROCKER15':
#                 sku = '8900030AUSTRALIS'
#             if sku == 'CRUSHBASS50':
#                 sku = '8900045AUSTRALIS'
#             if sku == 'RK15T':
#                 sku = '8900028AUSTRALIS'
#             if sku == 'PEDALBABY':
#                 sku = '8900074AUSTRALIS'
#             if sku == 'SUPERCR100CM':
#                 sku = '8900128AUSTRALIS'
#             if sku == 'PPC112':
#                 sku = '8900054AUSTRALIS'
#             if sku == 'SUPERCR100':
#                 sku = '8900126AUSTRALIS'
#             if sku == 'CRUSH20RTBK':
#                 sku = '8900041AUSTRALIS'
#             if sku == 'MT20':
#                 sku = '8900023AUSTRALIS'
#             if sku == 'CRUSH35RTBK':
#                 sku = '8900043AUSTRALIS'
#             if sku == 'OR15':
#                 sku = '8900019AUSTRALIS'
#             if sku == 'CRUSHMINI':
#                 sku = '8900035AUSTRALIS'
#             if sku == 'DUALTERROR':
#                 sku = '8900027AUSTRALIS'
#             if sku == 'PPC108':
#                 sku = '8900053AUSTRALIS'
#             if sku == 'OBC112':
#                 sku = '8900058AUSTRALIS'
#             if sku == 'CRUSH12BK':
#                 sku = '8900037AUSTRALIS'
#             if sku == 'MDHEAD':
#                 sku = '8900024AUSTRALIS'
#             if sku == 'CRUSH20BK':
#                 sku = '8900039AUSTRALIS'
#             if sku == 'DA15H':
#                 sku = '8900025AUSTRALIS'
#             if sku == 'PPC212OB':
#                 sku = '8900056AUSTRALIS'
#             if sku == 'FURCOAT':
#                 sku = '8900060AUSTRALIS'
#             if sku == 'SUPERCR100BK':
#                 sku = '8900127AUSTRALIS'
#             if sku == '8900101':
#                 sku = '8900101AUSTRALIS'
#             if sku == 'CRUSHBASSGH':
#                 sku = '8900130AUSTRALIS'
#             if sku == 'AMPDETONATOR':
#                 sku = '8900063AUSTRALIS'
#             if sku == '8900154':
#                 sku = '8900154AUSTRALIS'
#             if sku == 'ACOUSTPEDAL':
#                 sku = 'AUSTRALIS'
#             if sku == 'TERRORSTAMP':
#                 sku = '8900107AUSTRALIS'
#             if sku == '8900155':
#                 sku = '8900155AUSTRALIS'
#             if sku == '8900156':
#                 sku = '8900156AUSTRALIS'
#             if sku == 'SUPERCR100CB':
#                 sku = '8900129AUSTRALIS'
#             if sku == 'GETAWAY':
#                 sku = '8900061AUSTRALIS'
#             if sku == 'FS2':
#                 sku = '8900082AUSTRALIS'
#             if sku == 'TREMLORD30B':
#                 sku = '8900076AUSTRALIS'
#             if sku == 'TREMLORD30':
#                 sku = '8900075AUSTRALIS'
#             if sku == 'FS1MINI':
#                 sku = '8900110AUSTRALIS'
#             if sku == 'CRUSHBASS100':
#                 sku = '8900046AUSTRALIS'
#             if sku == 'OMECTELEPORT':
#                 sku = '8900064AUSTRALIS'
#             if sku == '8900098':
#                 sku = '8900098AUSTRALIS'
#             if sku == 'GUITARBUTLER':
#                 sku = '8900143AUSTRALIS'
#             if sku == 'LITTLEBASST':
#                 sku = '8900105AUSTRALIS'
#             if sku == 'TH30H':
#                 sku = '8900020AUSTRALIS'
#             if sku == 'TERRORBASS':
#                 sku = '8900047AUSTRALIS'
#             if sku == 'KONGPRESSOR':
#                 sku = '8900059AUSTRALIS'
#             if sku == 'ROCKER32':
#                 sku = '8900031AUSTRALIS'
#             if sku == 'FS1':
#                 sku = '8900081AUSTRALIS'
#             if sku == 'OB1500':
#                 sku = '8900051AUSTRALIS'
#             if sku == '4STROKE300':
#                 sku = '8900048AUSTRALIS'
#             if sku == '4STROKE500':
#                 sku = '8900049AUSTRALIS'
#             if sku == '8900102':
#                 sku = '8900102AUSTRALIS'
#             if sku == 'CRPRO412':
#                 sku = '8900057AUSTRALIS'
#
#
#             title = t.find(class_='widget-productlist-title').text
#
#             price = t.find(class_='widget-productlist-price').text
#             price = price.replace('\n', '')
#             price = price.replace('$', '')
#             #print(price)
#
#             image = 'NOT SCRAPED'
#             description = 'NOT SCRAPED'
#
#             today = datetime.now()
#
#             date = today.strftime('%m %d %Y')
#
#             sheet.append([sku, brand, title, price, url, image, description, date])
#             print(f'Item {str(item_number)} scraped successfully')
#
#             if int(items_scrapped)%3 == 0:
#                 print(f'Saving Sheet... Please wait....')
#                 wb.save("C:\Python\Pricing Spreadsheets\Mannys.xlsx")
#
#             ##GOING THROUGH ALL THE ORANGE SKUS MANUALLY, CHANGING SKU NAME TO ACTUAL SKU NAME
#
#         #print(number_of_brand_products)
#
#
#
try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Mannys.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")
