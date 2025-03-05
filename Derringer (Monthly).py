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
from seleniumbase import Driver



# session = HTMLSession()

wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Derringer.xlsx")
sheet = wb['Sheet']

url_list = []

item_number = 0
items_scrapped = 0

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)


# options = webdriver.ChromeOptions()
# options.add_argument("start-minimized")
# #options.add_argument("--headless")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument("window-size=10,10")
#
#
# #s=Service(ChromeDriverManager().install())
# s=ChromeDriverManager().install()
# driver = webdriver.Chrome(s, options=options)
#driver = webdriver.Chrome(options=options, executable_path=r'C:\Python\chromedriver.exe')

# stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#         )

driver = Driver(uc=True)

url = 'https://derringers.com.au/brands/'

#driver = webdriver.Chrome(r'C:\Python\chromedriver.exe')
driver.minimize_window()
r = driver.get(url)

html = driver.page_source




#r.html.render(timeout=100)

soup = BeautifulSoup(html)

#pprint.pprint(soup)
brands_list = soup.find(id='maincontent')
print(brands_list)

for x in brands_list.find_all(class_='ambrands-brand-item'):
    brand_count = x.find(class_='ambrands-count').text ###Number of items each brand has, will use this for page count later
    brand = x.find(class_='ambrands-label').text
    brand = brand.replace(brand_count, '').strip()

    if brand.lower() == 'tanglewood' or brand.lower() == 'orange' or brand.lower() == 'ernie ball' or brand.lower() == 'korg' or brand.lower() == 'arturia' or brand.lower() == 'jbl' or brand.lower() == 'epiphone' or brand.lower() == 'gibson' or brand.lower() == 'tc electronic' or brand.lower() == 'dbx' or brand.lower() == "d'addario" or brand.lower() == "planet waves" or brand.lower() == "tech 21" or brand.lower() == "lr baggs" or brand.lower() == "universal audio" or brand.lower() == "soundcraft" or brand.lower() == "aguilar" or brand.lower() == "behringer" or brand.lower() == "casio" or brand.lower() == "akg" or "seymour" in brand.lower() or brand.lower() == "blackstar" or "helicon" in brand.lower() or "kyser" in brand.lower() or "akai" in brand.lower() or "marshall" in brand.lower() or "nord" in brand.lower() or "hercules" in brand.lower() or "headrush" in brand.lower() or "boss" in brand.lower() or "ashton" in brand.lower() or "ibanez" in brand.lower() or "cordoba" in brand.lower() or "evans" in brand.lower() or "promark" in brand.lower() or "tascam" in brand.lower() or "gator" in brand.lower() or "valencia" in brand.lower() or "xtreme" in brand.lower() or "v-case" in brand.lower() or "mahalo" in brand.lower() or "dxp" in brand.lower() or "dunlop" in brand.lower() or "mano" in brand.lower() or "mxr" in brand.lower() or "armour" in brand.lower() or "dimarzio" in brand.lower() or 'alesis' in brand.lower() or 'digitech' in brand.lower() or 'crown' in brand.lower() or 'mooer' in brand.lower() or 'samson' in brand.lower() or 'mitello' in brand.lower() or 'powerbeat' in brand.lower() or 'schaller' in brand.lower() or 'xvive' in brand.lower() or 'beale' in brand.lower() or 'snark' in brand.lower() or 'esp' in brand.lower() or 'ltd' in brand.lower() or 'strymon' in brand.lower() or 'rockboard' in brand.lower() or 'sterling' in brand.lower() or 'music man' in brand.lower() or 'vic firth' in brand.lower() or 'ik multimedia' in brand.lower() or 'remo' in brand.lower() or 'darkglass' in brand.lower() or brand.lower() == 'martin' or 'm-audio' in brand.lower() or 'native instruments' in brand.lower() or 'hardcase' in brand.lower() or 'mapex' in brand.lower() or 'udg' in brand.lower() or 'alto' in brand.lower() or 'nux' in brand.lower() or 'se electronic' in brand.lower() or 'radial' in brand.lower() or 'teenage' in brand.lower() or 'teenage' in brand.lower() or 'tama' in brand.lower() or 'loog' in brand.lower() or 'hartke' in brand.lower() or 'roland' in brand.lower() or 'hosa' in brand.lower() or 'oskar' in brand.lower() or 'hotone' in brand.lower():
        pass
    else:
        continue

    for t in x:
        try:
            brand_url = t['href']
            print(t['href'])
            break
        except:
            continue

    page_count = math.ceil(float(brand_count)/65)
    # template url is https://derringers.com.au/zildjian?p={page_number+1}&product_list_limit=65
    for page_number in range(page_count):

        url = f'{brand_url}?p={page_number+1}&product_list_limit=65'


        time.sleep(2)

        ######### Cloudflare Bypass #####
        handle = driver.current_window_handle
        driver.service.stop()
        time.sleep(6)
        while True:
            try:
                 driver = Driver(uc=True)
                 break

            except:
                time.sleep(4)
                print("trying chome again")
                continue
        #driver.switch_to.window(handle)
        try:

            driver.minimize_window()
            r = driver.get(url)

        except:
            continue

        html = driver.page_source



        soup = BeautifulSoup(html)



        soup = soup.find(id='amasty-shopby-product-list')

        try:


            products = soup.find_all(class_='product-item-info type9')
        except:
            continue

        for product in products:
            item_number+=1


            pre_url = product.find(class_='product-item-link')
            url2 = pre_url['href']
            if url2 in url_list:
                print(f'Item {str(item_number)} already in sheet.')
                continue
            items_scrapped +=1 ###URL FOR FINAL PRODUCT, NEED TO ENTER AND SCRAPE FOR ALL INFO


            ######### Cloudflare Bypass #####
            handle = driver.current_window_handle
            driver.service.stop()
            time.sleep(6)
            while True:
                try:
                    driver = Driver(uc=True)
                    break

                except:
                    time.sleep(4)
                    print("trying chome again")
                    continue
            driver.minimize_window()
            #driver.switch_to.window(handle)


            try:
                r = driver.get(url2)
            except:
                time.sleep(4)
                print("trying chome get again")
                continue
           # time.sleep(2)

            html = driver.page_source



            soup = BeautifulSoup(html)


            title = soup.find(class_='page-title').text
            title = title.replace('\n', '').strip()

            #price = soup.find(class_='price-wrapper').text
            pre_price = soup.find(class_='product-info-main')
            try:
                price = pre_price.find(class_='special-price').text
            except:
                price = soup.find(class_='price-wrapper').text
            price = price.replace('\n', '')
            price = price.replace('Special Price', '')
            price = price.replace('$', '')
            price = price.replace(',', '')

            # pre_price = soup.find(class_= 'product-info-main')
            # price = pre_price.find(class_='price').text




           # pprint.pprint(price)


            sku = soup.find(class_='product attribute sku').text

            sku = sku.replace('SKU', '').strip()
            sku = sku.replace('_NOS', '')

            if brand.lower() == 'tanglewood':
                sku = sku.replace('TANG_', '')
                if sku == 'UT14E':
                    sku = 'TUT14E'
                    print('bing')
                    print('bong')

            if 'hotone' in brand.lower():
                sku = sku.replace('HOTO__', '')
                sku = sku.replace('HOTO_', '')

            if 'loog' in brand.lower():
                sku = sku.replace('LOOG__', '')
                sku = sku.replace('LOOG_', '')
                sku = f'{sku}DUNIM'

            if 'oskar' in brand.lower():
                sku = sku.replace('LEE__', '')
                sku = sku.replace('LEE_', '')

            if 'hosa' in brand.lower():
                sku = sku.replace('HOSA__', '')
                sku = sku.replace('HOSA_', '')

            if 'hartke' in brand.lower():
                sku = sku.replace('HART__', '')
                sku = sku.replace('HART_', '')
                sku = f'{sku}DUNIM'

            if 'radial' in brand.lower():
                sku = sku.replace('RADI__', '')
                sku = sku.replace('RADI_', '')

            if 'roland' in brand.lower():
                sku = sku.replace('ROLA__', '')
                sku = sku.replace('ROLA_', '')
                sku = sku.replace('-', '')

            if 'tama' in brand.lower():
                sku = sku.replace('TAMA__', '')
                sku = sku.replace('TAMA_', '')

            if 'teenage' in brand.lower():
                sku = sku.replace('TEEN__', '')
                sku = sku.replace('TEEN_', '')

            if brand.lower() == 'armour':
                if sku == 'ARMO_GS10':
                    sku = '813100'
                if sku == 'ARMO_APCW':
                    sku = '701200'
                if sku == 'ARMO_ARM1550C':
                    sku = '604135'
                if sku == 'ARMO_ARM350G':
                    sku = '604100'
                if sku == 'ARMO_APCTWD':
                    sku = '701245'
                if sku == 'ARMO_ARM350C75':
                    sku = '604104'
                if sku == 'ARMO_KBBL':
                    sku = '604197'
                if sku == 'ARMO_ARM1550W':
                    sku = '604134'


                sku = sku.replace('ARMO__', '')
                sku = sku.replace('ARMO_', '')
                sku = f'{sku}AUSTRALIS'

            if brand.lower() == 'armour':
                sku = sku.replace('ARMO_', '')
                sku = sku.replace('ARMO__', '')
                sku = f'{sku}AUSTRALIS'




            if 'ashton'  in brand.lower():
                sku = sku.replace('ASHT__', '')
                sku = sku.replace('ASHT_', '')
                sku = f'{sku}AUSTRALIS'

            if 'nux' in brand.lower():
                sku = sku.replace('NUX__', '')
                sku = sku.replace('NUX_', '')

            if 'remo' in brand.lower():
                sku = sku.replace('REMO__', '')
                sku = sku.replace('REMO_', '')

            if 'native instruments' in brand.lower():
                sku = sku.replace('NATI__', '')
                sku = sku.replace('NATI_', '')
                sku = f'{sku}CMI'

            if 'darkglass' in brand.lower():
                if sku == 'DARK_M500V2':
                    sku = 'DG-M500V2CMI'
                if sku == 'DARK_AO500':
                    sku = 'DG-AO500CMI'
                if sku == 'DARK_X-7':
                    sku = 'DG-X7CMI'
                if sku == 'DARK_M900V2':
                    sku = 'DG-M900V2CMI'
                if sku == 'DARK_ELM':
                    sku = 'DG-ELMCMI'
                if sku == 'DARK_AOU':
                    sku = 'DG-AOUV2CMI'
                if sku == 'DARK_AO900':
                    sku = 'DG-AO900CMI'
                if sku == 'DARK_MIX':
                    sku = 'DG-MIXCMI'
                if sku == 'DARK_MICROTUBESB3K':
                    sku = 'DG-B3K2CMI'
                if sku == 'DARK_B1K':
                    sku = 'DG-B1KCMI'
                if sku == 'DARK_OMICRON':
                    sku = 'DG-OMNCMI'
                if sku == 'DARK_EXP':
                    sku = 'DG-EXPCMI'
                if sku == 'DARK_SIFOOTSW':
                    sku = 'DG-SIFSBCMI'
                if sku == 'DARK_MICROTUBESB7K':
                    sku = 'DG-B7UV2CMI'
                if sku == 'DARK_M200':
                    sku = 'DG-M200CMI'
                if sku == 'DARK_HLHC':
                    sku = 'DG-HYLCMI'
                if sku == 'DARK_VINTMICROTUBES':
                    sku = 'DG-VMTCMI'
                if sku == 'DARK_INFINITY':
                    sku = 'DG-INFCMI'
                if sku == 'DARK_ADAM':
                    sku = 'DG-ADMCMI'
                if sku == 'DARK_DG112N':
                    sku = 'DG-DG112NCMI'
                if sku == 'DARK_DG-NSG':
                    sku = 'DG-NSGCMI'
                if sku == 'DARK_HBO':
                    sku = 'DG-HBOCMI'
                if sku == 'DARK_VINTAGEULTRA':
                    sku = 'DG-VDUV2CMI'
                if sku == 'DARK_B7KULTRA':
                    sku = 'DG-B7UV2CMI'
                if sku == 'DARK_ALPHA-OMEGA':
                    sku = 'DG-AOCMI'
                if sku == 'DARK_DUALITYFUZZ':
                    sku = 'DG-DFZ3CMI'
                if sku == 'DARK_DG212N':
                    sku = 'DG-DG212NCMI'
                if sku == 'DARK_DG210N':
                    sku = 'DG-DG210NCMI'
                if sku == 'DARK_M900-BAG':
                    sku = 'DG-BAG900CMI'
                if sku == 'DARK_A-O200':
                    sku = 'DG-AO200CMI'
                if sku == 'DARK_AOP':
                    sku = 'DG-AOPCMI'


            if 'vic firth' in brand.lower():
                sku = sku.replace('VICF__', '')
                sku = sku.replace('VICF_', '')
                sku = f'{sku}AUSTRALIS'

            if 'gator'  in brand.lower():
                sku = sku.replace('GATO__', '')
                sku = sku.replace('GATO_', '')
                sku = f'{sku}AUSTRALIS'

            if 'cordoba' in brand.lower():
                sku = sku.replace('CORD__', '')
                sku = sku.replace('CORD_', '')

            if 'sterling' in brand.lower():
                sku = sku.replace('STER__', '')
                sku = sku.replace('STER_', '')
                sku = f'{sku}CMC'

            if 'music man' in brand.lower():
                sku = sku.replace('EBMM__', '')
                sku = sku.replace('EBMM_', '')
                sku = f'{sku}CMC'


            if "seymour" in brand.lower():
                sku = sku.replace('SEYM_', '')
                sku = sku.replace('Seym_', '')
                sku = f'{sku}AUSTRALIS'

            if "xvive" in brand.lower():
                sku = sku.replace('XVIV_', '')
                sku = sku.replace('XVIV__', '')
                sku = f'{sku}AUSTRALIS'

            if "schaller" in brand.lower():
                sku = sku.replace('SCHA_', '')
                sku = sku.replace('SCHA__', '')
                sku = f'{sku}PT'

            if "valencia" in brand.lower():
                sku = sku.replace('VALE__', '')
                sku = sku.replace('VALE_', '')

            if "snark" in brand.lower():
                sku = sku.replace('SNAR__', '')
                sku = sku.replace('SNAR_', '')

            if "mxr" in brand.lower():
                sku = sku.replace('MXR__', '')
                sku = sku.replace('MXR_', '')

            if "mano" in brand.lower():
                sku = sku.replace('MANO__', '')
                sku = sku.replace('MANO_', '')

            if "mitello" in brand.lower():
                sku = sku.replace('MITE__', '')
                sku = sku.replace('MITE_', '')

            if "powerbeat" in brand.lower():
                sku = sku.replace('POWE__', '')
                sku = sku.replace('POWE_', '')

            if "auralex" in brand.lower():
                sku = sku.replace('AURA__', '')
                sku = sku.replace('AURA_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "alto" in brand.lower():
                sku = sku.replace('ALTO__', '')
                sku = sku.replace('ALTO_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if brand.lower() == 'martin':
                sku = sku.replace('MART__', '')
                sku = sku.replace('MART_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "alesis" in brand.lower():
                sku = sku.replace('ALES__', '')
                sku = sku.replace('ALES_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "samson" in brand.lower():
                sku = sku.replace('SAMS__', '')
                sku = sku.replace('SAMS_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "m-audio" in brand.lower():
                sku = sku.replace('M-AU__', '')
                sku = sku.replace('M-AU_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "rockboard" in brand.lower():
                sku = sku.replace('ROCK__', '')
                sku = sku.replace('ROCK_', '')
                sku = sku.replace('WARW__', '')
                sku = sku.replace('WARW_', '')

            if "dimarzio" in brand.lower():
                sku = sku.replace('DIMA__', '')
                sku = sku.replace('DIMA_', '')

            if "dunlop" in brand.lower():
                sku = sku.replace('JIM__', '')
                sku = sku.replace('JIM_', '')
                sku = sku.replace('DUNL__', '')
                sku = sku.replace('DUNL_', '')

            if "mahalo" in brand.lower():
                sku = sku.replace('MAHA__', '')
                sku = sku.replace('MAHA_', '')

            if "xtreme" in brand.lower():
                sku = sku.replace('XTRE__', '')
                sku = sku.replace('XTRE_', '')

            if "dxp" in brand.lower():
                sku = sku.replace('DXP__', '')
                sku = sku.replace('DXP_', '')

            if "v-case" in brand.lower():
                sku = sku.replace('VCAS_', '')
                sku = sku.replace('V CA_', '')

            if "boss" in brand.lower():
                sku = sku.replace('BOSS__', '')
                sku = sku.replace('BOSS_', '')

            if "promark" in brand.lower():
                sku = sku.replace('PRO__', '')
                sku = sku.replace('PRO_', '')


            if "kyser" in brand.lower():
                sku = sku.replace('KYSE_', '')
                split_sku = list(sku)
                if split_sku[-1] != 'A':
                    sku = f'{sku}A'
                sku = f'{sku}CMC'
            if "akai" in brand.lower():
                sku = sku.replace('AKAI__', '')
                sku = sku.replace('AKAI_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "headrush" in brand.lower():
                sku = sku.replace('HEAD__', '')
                sku = sku.replace('HEAD_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "mapex" in brand.lower():
                sku = sku.replace('MAPE__', '')
                sku = sku.replace('MAPE_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "hercules" in brand.lower():
                sku = sku.replace('HERC__', '')
                sku = sku.replace('HERC_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "udg" in brand.lower():
                sku = sku.replace('UDG__', '')
                sku = sku.replace('UDG_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "marshall" in brand.lower():
                sku = sku.replace('MARS__', '')
                sku = sku.replace('MARS_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "nord" in brand.lower():
                sku = sku.replace('NORD__', '')
                sku = sku.replace('NORD_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if "hardcase" in brand.lower():
                sku = sku.replace('HARD__', '')
                sku = sku.replace('HARD_', '')
                sku = sku.replace('/', '')
                sku = f'{sku}EF'

            if brand.lower() == 'casio':
                sku = sku.replace('CASI_', '')
                sku = sku.replace('Casi_', '')

            if 'evan' in brand.lower():
                sku = sku.replace('EVAN__', '')
                sku = sku.replace('EVAN_', '')


            if brand.lower() == 'orange':
                sku = sku.replace('ORAN_', '')
                if sku == 'CRUSHACOUSTIC30':
                    sku = '8900101'
                if sku == 'CRUSHACOUSTIC30BK':
                    sku = '8900102'
                sku = f'{sku}AUSTRALIS'

            if brand.lower() == "d'addario":
                sku = sku.replace('DADD_', '')
                sku = sku.replace('Dadd_', '')

            if 'esp' in brand.lower() or 'ltd' in brand.lower():
                sku = sku.replace('ESP__', '')
                sku = sku.replace('ESP_', '')
                sku = sku.replace('ESP _', '')
                sku = sku.replace('Esp_', '')
                sku = f'{sku}CMI'

            if brand.lower() == 'dbx':
                sku = sku.replace('DBX__', '')
                sku = sku.replace('Dbx__', '')
                sku = sku.replace('DBX_', '')
                sku = sku.replace('Dbx_', '')
                sku = f'{sku}CMI'

            if 'crown' in brand.lower():
                sku = sku.replace('CROW__', '')
                sku = sku.replace('Crow__', '')
                sku = sku.replace('CROW_', '')
                sku = sku.replace('Crow_', '')
                sku = f'{sku}CMI'

            if 'mooer' in brand.lower():
                sku = sku.replace('MOOE__', '')
                sku = sku.replace('Mooe__', '')
                sku = sku.replace('MOOE_', '')
                sku = sku.replace('Mooe_', '')
                sku = f'{sku}JD'

            if brand.lower() == 'digitech':
                sku = sku.replace('DIGI__', '')
                sku = sku.replace('Digi__', '')
                sku = sku.replace('DIGI_', '')
                sku = sku.replace('Digi_', '')
                sku = f'{sku}CMI'

            if 'tascam' in brand.lower():
                sku = sku.replace('TASC__', '')
                sku = sku.replace('Tasc__', '')
                sku = sku.replace('TASC_', '')
                sku = sku.replace('Tasc_', '')
                sku = f'{sku}CMI'

            if brand.lower() == 'arturia':
                sku = sku.replace('ARTU_', '')
                sku = sku.replace('Artu_', '')
                sku = f'{sku}CMI'
            if brand.lower() == 'akg':
                sku = sku.replace('AKG__', '')
                sku = sku.replace('AKG_', '')
                sku = sku.replace('Akg__', '')
                sku = sku.replace('Akg_', '')
                sku = f'{sku}CMI'

            if brand.lower() == "blackstar":
                sku = sku.replace('BLAC__', '')
                sku = sku.replace('BLAC_', '')
                sku = sku.replace('Blac__', '')
                sku = sku.replace('Blac_', '')
                sku = f'{sku}CMI'

            if brand.lower() == 'ernie ball':
                sku = sku.replace('ERNI_', '')
                sku = sku.replace('Erni_', '')
                sku = f'{sku}CMC'

            if brand.lower() == 'epiphone':
                sku = sku.replace('EPIP_', '')
                sku = sku.replace('Epip_', '')
                sku = f'{sku}AUSTRALIS'

            if 'ibanez' in brand.lower():
                sku = sku.replace('AMG__', '')
                sku = sku.replace('AMG_', '')
                sku = sku.replace('IBAN__', '')
                sku = sku.replace('IBAN_', '')
                sku = f'{sku}AUSTRALIS'

            if brand.lower() == 'gibson':
                sku = sku.replace('GIBS_', '')
                sku = sku.replace('Gibs_', '')
                sku = f'{sku}AUSTRALIS'

            if brand.lower() == 'korg':
                sku = sku.replace('KORG_', '')
                sku = sku.replace('Korg_', '')
                sku = f'{sku}CMI'

            if brand.lower() == "planet waves":
                sku = sku.replace('PLAN_', '')
                sku = sku.replace('Plan_', '')



            if brand.lower() == "aguilar":
                sku = sku.replace('AGUI_', '')
                sku = sku.replace('Agui_', '')
                sku = f'{sku}CMI'

            if brand.lower() == 'jbl':
                sku = sku.replace('JBL__', '')
                sku = sku.replace('jbl__', '')
                sku = sku.replace('JBL_', '')
                sku = sku.replace('jbl_', '')
                sku = f'{sku}CMI'

            if brand.lower() == "soundcraft":
                sku = sku.replace('SOUN_', '')
                sku = sku.replace('soun_', '')
                sku = f'{sku}CMI'

            if brand.lower() == "lr baggs":
                sku = sku.replace('LR B_', '')

            if brand.lower() == "tech 21":
                sku = sku.replace('TECH_', '')
                sku = sku.replace('tech_', '')

            if brand.lower() == "universal audio":
                sku = sku.replace('UAD__', '')
                sku = sku.replace('uad__', '')
                sku = sku.replace('UNIV_', '')
                sku = f'{sku}CMI'

            if "beale" in brand.lower():
                sku = sku.replace('BEAL_', '')
                sku = sku.replace('BEAL__', '')
                sku = f'{sku}AUSTRALIS'

            if "strymon" in brand.lower():
                if sku == 'STRY_STR-MULTI_SWITCH':
                    sku = 'SN-MULTI-SWITCH'
                if sku == 'STRY_STR-ORBIT':
                    sku = 'SN-ORBIT'
                if sku == 'STRY_STR-MOBIUS':
                    sku = 'SN-MOBIUS'
                if sku == 'STRY_STR-MINISWITCH':
                    sku = 'SN-MINI-SWITCH'
                if sku == 'STRY_SUNSET':
                    sku = 'SN-SUNSET'
                if sku == 'STRY_STR-ZUMA-R300':
                    sku = 'SN-ZUMA-R300'
                if sku == 'STRYM_STR-NIGHTSKY':
                    sku = 'SN-NIGHT-SKY'
                if sku == 'STRY_STR-LEX':
                    sku = 'SN-LEX'
                if sku == 'STRY_STR-ZUMA':
                    sku = 'SN-ZUMA'
                if sku == 'STRY_SN-VOLANTE':
                    sku = 'SN-VOLANTE'
                if sku == 'STRY_STR-TIMELINE':
                    sku = 'SN-TIMELINE'
                if sku == 'STRY_STR-RIVERSIDE':
                    sku = 'SN-RIVERSIDE'
                if sku == 'STRY_STR-OLA':
                    sku = 'SN-OLA'
                if sku == 'STRY_STR-BRIGADIER':
                    sku = 'SN-BRIGADIER'
                if sku == 'STRY_STR-BLUE_SKY':
                    sku = 'SN-BLUE-SKY'
                if sku == 'STRY_SN-LEX-2':
                    sku = 'SN-LEX-2'
                if sku == 'STRY_SN-IRIDIUM':
                    sku = 'SN-IRIDIUM'
                if sku == 'STRY_STR-DIG':
                    sku = 'SN-DIG'
                if sku == 'STRY_STR-BIGSKY':
                    sku = 'SN-BIG-SKY'
                if sku == 'STRY_STR-FLINT':
                    sku = 'SN-FLINT'
                if sku == 'STRY_SN-DIG-2':
                    sku = 'SN-DIG-2'
                if sku == 'STRY_STR-DECO':
                    sku = 'SN-DECO'
                if sku == 'STRY_STR-COMPADRE':
                    sku = 'SN-COMPADRE'
                if sku == 'STRY_SN-BLUE-SKY-2':
                    sku = 'SN-BLUE-SKY-2'
                if sku == 'STRY_STR-OJAI':
                    sku = 'SN-OJAI'
                if sku == 'STRY_STR-OB.1':
                    sku = 'SN-OB.1'
                if sku == 'STRY_SN-FLINT-2':
                    sku = 'SN-FLINT-2'
                if sku == 'STRY_SN-EL-CAPISTAN-2':
                    sku = 'SN-EL-CAPISTAN-2'
                if sku == 'STRY_SN-DECO-2':
                    sku = 'SN-DECO-2'
                if sku == 'STRY_STR-MAGNETO':
                    sku = 'SN-MAGNETO'


            if "helicon" in brand.lower():
                if sku == 'TEHL-PERFORM-VE':
                    sku = '455113AUSTRALIS'
                if sku == 'TC-H_TC-GIGBAG-TCH':
                    sku = '455098AUSTRALIS'
                if sku == 'TEHL_PERFORMV':
                    sku = '455112AUSTRALIS'
                if sku == 'TEHL_FX150GIGBAG':
                    sku = '455097AUSTRALIS'
                if sku == 'TEHL_DUPLICATOR':
                    sku = '455096AUSTRALIS'
                if sku == 'TEHL_DITTOMICLOOPER':
                    sku = '455095AUSTRALIS'
                if sku == 'TEHL_VOICETONEC1':
                    sku = '455123AUSTRALIS'
                if sku == 'TEHL_455104':
                    sku = '455104AUSTRALIS'
                if sku == 'TEHL_VOICETONER1':
                    sku = '455127AUSTRALIS'
                if sku == 'TEHL_VOICETONED1':
                    sku = '455124AUSTRALIS'
                if sku == 'TC-H_TC-TALKBOX-SYNTH':
                    sku = '455120AUSTRALIS'
                if sku == 'TEHL_SWITCH6':
                    sku = '455119AUSTRALIS'
                if sku == 'TEHL_SWITCH3':
                    sku = '455118AUSTRALIS'
                if sku == 'TEHL_POWERPLUG12':
                    sku = '455117AUSTRALIS'
                if sku == 'TC-H_TC-PERFORM-VG':
                    sku = '455114AUSTRALIS'
                if sku == 'TEHL_455105':
                    sku = '455105AUSTRALIS'
                if sku == 'TC-H_TC-PERFORM-VK':
                    sku = '455115AUSTRALIS'
                if sku == 'TEHL_VOICETONEH1':
                    sku = '455126AUSTRALIS'
                if sku == 'TEHL_VOICETONET1':
                    sku = '455128AUSTRALIS'
                if sku == 'TEHL_VOICETONEE1':
                    sku = '455125AUSTRALIS'
                if sku == 'TEHL_CRITICALMASS':
                    sku = '455094AUSTRALIS'
                if sku == 'TEHL_BLENDER':
                    sku = '455093AUSTRALIS'
                if sku == 'TEHL_VOICELIVE3EXTREME':
                    sku = '455121AUSTRALIS'
                if sku == 'TEHL_VOICETONEX1':
                    sku = '455129AUSTRALIS'
                if sku == 'TEHL_VOICELIVEPLAY':
                    sku = '455122AUSTRALIS'
                if sku == 'TEHL_PLAYACOUSTIC':
                    sku = '455166AUSTRALIS'
                if sku == 'TC-H_TC-MIC-MECHANIC2':
                    sku = '455111AUSTRALIS'
                if sku == 'TEHL_MCA100MICCONTROLADAPTER':
                    sku = '455110AUSTRALIS'
                if sku == 'TEHL_HARMONYSINGER2':
                    sku = '455107AUSTRALIS'
                if sku == 'TEHL_GOVOCAL':
                    sku = '455103AUSTRALIS'
                if sku == 'TEHL_GOGUITAR':
                    sku = '455099AUSTRALIS'
                if sku == 'TEHL_HARMONYV60':
                    sku = '455109AUSTRALIS'
                if sku == 'TEHL_HARMONYV100':
                    sku = '455108AUSTRALIS'
                if sku == 'TEHL_GOSOLO':
                    sku = '455101AUSTRALIS'
                if sku == 'TEHL_455106':
                    sku = '455106AUSTRALIS'
                if sku == 'TEHL_GOGUITARPRO':
                    sku = '455100AUSTRALIS'
                if sku == 'TEHL_GOTWIN':
                    sku = '455102AUSTRALIS'



            if brand.lower() == 'tc electronic':

                if sku == 'TC-E_TC-HOF2-X4':
                    sku = '455043AUSTRALIS'
                if sku == 'TC-E_TC-GRANDMAGUS':
                    sku = '455040AUSTRALIS'
                if sku == 'TC-E_TC-ECHOBRAIN':
                    sku = '455027AUSTRALIS'
                if sku == 'TC-E_TC-CINDERS':
                    sku = '455013AUSTRALIS'
                if sku == 'TC-E_TC-AFTERGLOW':
                    sku = '455001AUSTRALIS'
                if sku == 'TECL_VISCOUSVIBE':
                    sku = '455090AUSTRALIS'
                if sku == 'TECL_THUNDERSTORMFLANGER':
                    sku = '455086AUSTRALIS'
                if sku == 'TECL_THEPROPHETDIGITALDELAY':
                    sku = '455085AUSTRALIS'
                if sku == 'TECL_THEDREAMSCAPE':
                    sku = '455084AUSTRALIS'
                if sku == 'TECL_TAILSPINVIBRATO':
                    sku = '455080AUSTRALIS'
                if sku == 'TECL_SUBNUPMINIOCTAVER':
                    sku = '455078AUSTRALIS'
                if sku == 'TECL_SPECTRACOMPBASS':
                    sku = '455077AUSTRALIS'
                if sku == 'TECL_SPARKMINIBOOSTER':
                    sku = '455076AUSTRALIS'
                if sku == 'TECL_SPARKBOOSTER':
                    sku = '455075AUSTRALIS'
                if sku == 'TECL_SKYSURFERREVERB':
                    sku = '455074AUSTRALIS'
                if sku == 'TCEL_TC-TP-SHKR-MINI':
                    sku = '455072AUSTRALIS'
                if sku == 'TECL_SENTRYNOISEGATE':
                    sku = '455071AUSTRALIS'
                if sku == 'TECL_RUSTYFUZZ':
                    sku = '455070AUSTRALIS'
                if sku == 'TECL_RUSHBOOSTER':
                    sku = '455069AUSTRALIS'
                if sku == 'TCEL_QUINTESSENCE':
                    sku = '455068AUSTRALIS'
                if sku == 'TECL_POWERPLUG9':
                    sku = '455067AUSTRALIS'
                if sku == 'TCEL_PLETHORAX3':
                    sku = '455150AUSTRALIS'
                if sku == 'TECL_PIPELINETAPTREMOLO':
                    sku = '455060AUSTRALIS'
                if sku == 'TC-E_TC-NETHER':
                    sku = '455059AUSTRALIS'
                if sku == 'TECL_MOJOMOJOOVERDRIVE':
                    sku = '455058AUSTRALIS'
                if sku == 'TECL_MIMIQDOUBLER':
                    sku = '455056AUSTRALIS'
                if sku == 'TCEL_IMPULSE':
                    sku = '455145AUSTRALIS'
                if sku == 'TECL_HYPERGRAVITYMINI':
                    sku = '455047AUSTRALIS'
                if sku == 'TECL_HYPERGRAVITYCOMPRESSOR':
                    sku = '455046AUSTRALIS'
                if sku == 'TC-E_TC-HONEY-POT':
                    sku = '455045AUSTRALIS'
                if sku == 'TECL_HELIXPHASER':
                    sku = '455044AUSTRALIS'
                if sku == 'TECL_HALLOFFAME2MINIREVERB':
                    sku = '455041AUSTRALIS'
                if sku == 'TECL_GLT':
                    sku = '455039AUSTRALIS'
                if sku == 'TECL_GLR':
                    sku = '455038AUSTRALIS'
                if sku == 'TECL_GAUSSTAPEECHO':
                    sku = '455037AUSTRALIS'
                if sku == 'TECL_FLASHBACKTRIPLEDELAY':
                    sku = '455034AUSTRALIS'
                if sku == 'TECL_FANGSMETALDISTORTION':
                    sku = '455030AUSTRALIS'
                if sku == 'TECL_DRIPSPRINGREVERB':
                    sku = '455024AUSTRALIS'
                if sku == 'TECL_DITTOX4LOOPER':
                    sku = '455023AUSTRALIS'
                if sku == 'TECL_DARKMATTERDISTORTION':
                    sku = '455019AUSTRALIS'
                if sku == 'TC-E_TC-CRESCENDO':
                    sku = '455018AUSTRALIS'
                if sku == 'TECL_CORONAMINICHORUS':
                    sku = '455017AUSTRALIS'
                if sku == 'TECL_CORONACHORUS':
                    sku = '455016AUSTRALIS'
                if sku == 'TC-E_TC-CHOKA':
                    sku = '455012AUSTRALIS'
                if sku == 'TECL_BRICKWALLHD':
                    sku = '455011AUSTRALIS'
                if sku == 'TECL_BQ500':
                    sku = '455009AUSTRALIS'
                if sku == 'TECL_BQ250':
                    sku = '455008AUSTRALIS'
                if sku == 'TECL_BONAFIDEBUFFER':
                    sku = '455007AUSTRALIS'
                if sku == 'TC-E_BLOODMOON':
                    sku = '455005AUSTRALIS'
                if sku == 'TECL_BH250':
                    sku = '455004AUSTRALIS'
                if sku == 'TC-E_TC2290-DT':
                    sku = '455082AUSTRALIS'
                if sku == 'TECL_VORTEXFLANGER':
                    sku = '455091AUSTRALIS'
                if sku == 'TECL_VIBRACLONEROTARY':
                    sku = '455089AUSTRALIS'
                if sku == 'TECL_SHAKERVIBRATO':
                    sku = '455073AUSTRALIS'
                if sku == 'TECL_SHAKERMINIVIBRATO':
                    sku = '455072AUSTRALIS'
                if sku == 'TECL_MIMIQMINIDOUBLER':
                    sku = '455057AUSTRALIS'
                if sku == 'TECL_MASTERXHD':
                    sku = '455055AUSTRALIS'
                if sku == 'TC-E_TC-M100':
                    sku = '455054AUSTRALIS'
                if sku == 'TECL_LEVELPILOTX':
                    sku = '455053AUSTRALIS'
                if sku == 'TECL_LEVELPILOTC':
                    sku = '455052AUSTRALIS'
                if sku == 'TC-E_TC-IRON-CURTAIN':
                    sku = '455048AUSTRALIS'
                if sku == 'TECL_FLUORESCENCE':
                    sku = '455035AUSTRALIS'
                if sku == 'TC-E_TC-EYEMASTER':
                    sku = '455029AUSTRALIS'
                if sku == 'TC-E_TC-EL-MOCAMBO':
                    sku = '455028AUSTRALIS'
                if sku == 'TECL_DYN3000DT':
                    sku = '455026AUSTRALIS'
                if sku == 'TECL_DVR250NATIVEDVR250DT':
                    sku = '455025AUSTRALIS'
                if sku == 'TC-E_TC-DITTO-X2':
                    sku = '455022AUSTRALIS'
                if sku == 'TECL_DITTOSTEREOLOOPER':
                    sku = '455021AUSTRALIS'
                if sku == 'TECL_DITTOLOOPER':
                    sku = '455020AUSTRALIS'
                if sku == 'TC-E_TC-DITTO-JAM-X2':
                    sku = '455139AUSTRALIS'
                if sku == 'TECL_CLARITYMSTEREO':
                    sku = '455015AUSTRALIS'
                if sku == 'TECL_CLARITYM':
                    sku = '455014AUSTRALIS'
                if sku == 'TECL_BRAINWAVESPITCHSHIFTER':
                    sku = '455010AUSTRALIS'
                if sku == 'TECL_BODYREZ':
                    sku = '455006AUSTRALIS'
                if sku == 'TECL_BC208':
                    sku = '455003AUSTRALIS'
                if sku == 'TECL_BAM200':
                    sku = '455002AUSTRALIS'
                if sku == 'TC-E_TC-3RD-DIMENSION':
                    sku = '455000AUSTRALIS'
                if sku == 'TC-E_TC-1210-DT':
                    sku = '455081AUSTRALIS'

                if 'TCEL_' in sku:
                    sku = sku.replace('TCEL_', '')
                    sku = sku.replace('tcel_', '')
                    sku = f'{sku}AUSTRALIS'
                if 'TC-E_' in sku:
                    sku = sku.replace('TC-E_', '')
                    sku = sku.replace('tc-e_', '')
                    sku = f'{sku}AUSTRALIS'

            # image = soup.find(class_ = 'gallery-placeholder')
            image = soup.find(class_='gallery-placeholder__image')

            try:

                image = image['src']

            except:
                image = 'NA'


            print(f'sku: {sku}')

            description = soup.find(class_='product attribute description').text
            description = description.replace('Derringers', 'Scarlett')
            print(f'description: {description}')
            print(f'price: {price}')

            try:
                stock = soup.find(class_='amstockstatus-status-container stock available')
                stock_avaliable = 'y'

            except:
                stock_avaliable = 'n'

            today = datetime.now()

            date = today.strftime('%m %d %Y')

            sheet.append([sku, brand, title, price, url2, image, description, date, stock_avaliable])
            print(f'Item {str(item_number)} scraped successfully')

            if int(items_scrapped) % 3 == 0:
                print(f'Saving Sheet... Please wait....')
                wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Derringer.xlsx")

wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\Derringer.xlsx")







