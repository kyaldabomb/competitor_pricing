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

driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Haworth.xlsx")
sheet = wb['Sheet']

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)


item_number = 0
items_scrapped = 0


url = 'https://www.haworthguitars.com.au/pages/search-results'

r = driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
time.sleep(10)


for tt in range(360):
    try:
        element = driver.find_element(By.XPATH, '//*[@id="shopify-section-footer"]/section[1]/div/div/div/form/div/div[3]/div[2]/button')

        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        time.sleep(5)
    except:
        continue
#####^^^^^^^^

html = driver.page_source

soup = BeautifulSoup(html, 'html.parser')

for x in soup.find_all(class_='sq-page-item sparq-column-3'):
    title = x.find(class_='sparq-item-title').text
    brand = x.find(class_='vendor-title').text.strip()

    post_url = title.replace(' ', '-')
    post_url = post_url.replace("'", "")
    post_url = post_url.replace('"', '')
    post_url = post_url.replace("(", "")
    post_url = post_url.replace(")", "")
    post_url = post_url.replace(",", "")
    post_url = post_url.replace("/", "")
    post_url = post_url.replace("---", "-")
    post_url = post_url.replace("--", "-")

    url = f"https://www.haworthguitars.com.au/products/{post_url}"
    if url in url_list:
        continue

    sku = 'NOT SCRAPED'
    image = 'NOT SCRAPED'
    description = 'NOT SCRAPED'
    price = 'NOT SCRAPED'

    today = datetime.now()

    date = today.strftime('%m %d %Y')

    sheet.append([sku, brand, title, price, url, image, description, date])
    print(f'Item {str(item_number)} scraped successfully')

    if int(items_scrapped) % 3 == 0:
        print(f'Saving Sheet... Please wait....')
        try:
            wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Haworth.xlsx")

        except:
            print(f"Error occurred while saving the Excel file:")
try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Haworth.xlsx")

except:
    print(f"Error occurred while saving the Excel file:")





#view button xpath //*[@id="sparq-container"]/div/div/div[2]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div/div[5]/div/div[1]/div   class_='sparq-cart-btn'