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

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
# options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
#options.add_argument("window-size=10,10")
#s=Service(ChromeDriverManager().install())
s=Service(r'\\SERVER\Python\chromedriver.exe')
# driver = webdriver.Chrome(service=s,options=options)
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


wb = openpyxl.load_workbook(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\DJ_City.xlsx")
sheet = wb['Sheet']

url_list = []

for x in range(2, sheet.max_row+1):
    url_list.append(sheet['E'+str(x)].value)

url = 'https://djcity.com.au/brands/'

r = requests.get(url)

soup = BeautifulSoup(r.content, 'html.parser')

item_number = 0

items_scrapped = 0

for x in soup.find_all(class_="w-1/2 sm:w-1/6 px-1 pb-5"):
    url = f"https://djcity.com.au{x.find('a')['href']}"
    brand = x.find('img')['alt']

    if 'orange' in brand.lower() or 'blue' in brand.lower() or brand.lower() == 'ernie ball' or 'korg' in brand.lower() or 'arturia' in brand.lower() or 'jbl' in brand.lower() or 'dbx' in brand.lower() or 'universal audio' in brand.lower() or 'soundcraft' in brand.lower() or 'aguilar' in brand.lower() or 'akg' in brand.lower() or 'blackstar' in brand.lower() or 'helicon' in brand.lower() or 'akai' in brand.lower() or 'hercules' in brand.lower() or 'headrush' in brand.lower() or 'boss' in brand.lower() or 'ashton' in brand.lower() or 'tascam' in brand.lower() or 'gator' in brand.lower() or 'armour' in brand.lower() or 'auralex' in brand.lower() or 'alesis' in brand.lower() or 'digitech' in brand.lower() or 'ebow' in brand.lower() or 'crown' in brand.lower() or 'samson' in brand.lower() or 'xvive' in brand.lower() or 'ik multimedia' in brand.lower() or 'm-audio' in brand.lower() or 'maudio' in brand.lower() or 'native instruments' in brand.lower()  \
            or 'sequenz' in brand.lower() or 'source audio' in brand.lower() or 'udg' in brand.lower() or 'alto' in brand.lower() or 'nektar' in brand.lower() or 'se electronics' in brand.lower() or 'radial' in brand.lower() or 'teenage' in brand.lower() or 'roland' in brand.lower() or 'hosa' in brand.lower():
        pass
    # if 'orange' in brand.lower() or 'universal audio' in brand.lower() or 'soundcraft' in brand.lower():
    #     pass
    else:
        continue

    ###TC ELECTRONIC HAS COOKED SKUS

    for pages in range(10):



        try:

            r = driver.get(f'{url}?prod_products%5Bpage%5D={str(pages+1)}')

        except:
            continue
        html = driver.page_source
        soup2 = BeautifulSoup(html, 'html.parser')

        for xx in soup2.find_all(class_='product-loop-link'):
            item_number += 1
            url2 = xx['href']
            if url2 in url_list:
                print(f'Item {str(item_number)} already in sheet.')
                continue
            items_scrapped += 1

            try:
                r2 = driver.get(url2)

            except:
                continue
            html = driver.page_source
            soup3 = BeautifulSoup(html, 'html.parser')

            try:
             title = soup3.find(class_='product_title entry-title').text
            except:
                continue
            price = soup3.find(class_='price').text
            price = price.replace("\n","")
            price = price.replace("$","")
            description = soup3.find(class_='woocommerce-product-details__short-description').text
            sku = soup3.find(class_='sku').text

            if 'arturia' in brand.lower():
                sku = f'AR-{sku}CMI'
            if 'jbl' in brand.lower():
                sku = f'JBL-{sku}CMI'
            if 'tascam' in brand.lower():
                sku = f'{sku}CMI'
            if 'dbx' in brand.lower():
                sku = f'DBX-{sku}CMI'
            if 'dbx' in brand.lower():
                sku = f'DBX-{sku}CMI'
            if 'digitech' in brand.lower():
                sku = f'{sku}CMI'
            if 'universal audio' in brand.lower():
                sku = f'UA-{sku}CMI'
            if 'soundcraft' in brand.lower():
                sku = f'SCF-{sku}CMI'
            if 'aguilar' in brand.lower():
                sku = f'{sku}CMI'
            if 'ebow' in brand.lower():
                sku = f'E-BOWCMI'
            if 'crown' in brand.lower():
                sku = f'CROWN-{sku}CMI'
            if 'hercules' in brand.lower():
                sku = f'05{sku}EF'
            if 'sequenz' in brand.lower():
                sku = f'KO-{sku}CMI'

            if 'teenage' in brand.lower():
                sku = sku.replace('-', '')
                sku = f'TEE-{sku}'

            if 'blue' in brand.lower():
                if sku == 'BABYBOTTLE-SL':
                    sku = 'BLU-BABYBOTTLESL'
                if sku == 'BLUEBIRD-SL':
                    sku = 'BLU-BLUEBIRDSL'
                if sku == 'EMBER':
                    sku = 'BLU-EMBER'


            if 'roland' in brand.lower():
                if sku == 'DS1W-BOSS':
                    sku = 'DS1W'
                if sku == 'A-49':
                    sku = 'A49BK'
                if sku == 'A-88MKII':
                    sku = 'A88MK2'
                if sku == 'AX-EDGE':
                    sku = 'AXEDGEB'
                if sku == 'BA-330':
                    sku = 'BA330'
                if sku == 'CB-CS1':
                    sku = 'CBCS1'
                if sku == 'CBG49':
                    sku = 'CBG49'
                if sku == 'CBG49D':
                    sku = 'CBG49D'
                if sku == 'CBHPD':
                    sku = 'CBHPD'
                if sku == 'CUBESTREET-EX':
                    sku = 'CUBESTEX'
                if sku == 'BS-943019':
                    sku = 'DJ808'
                if sku == 'DJ-505':
                    sku = 'DJ505'
                if sku == 'DP-2':
                    sku = 'DP2'
                if sku == 'E-4':
                    sku = 'E4'
                if sku == 'FANTOM-06':
                    sku = 'FANTOM06'
                if sku == 'FANTOM-07':
                    sku = 'FANTOM07'
                if sku == 'FANTOM-08':
                    sku = 'FANTOM08'
                if sku == 'GOMIXER-PROX':
                    sku = 'GOMIXERPX'
                if sku == 'GOLIVECAST':
                    sku = 'GOLIVECAST'
                if sku == 'INTEGRA-7':
                    sku = 'INTEGRA7'
                if sku == 'J-6':
                    sku = 'J6'
                if sku == 'JD-08':
                    sku = 'JD08'
                if sku == 'JD-XI':
                    sku = 'JDXI'
                if sku == 'JU-06A':
                    sku = 'JU06A'
                if sku == 'JUNO-DS61':
                    sku = 'JUNODS61'
                if sku == 'JUNO-DS76':
                    sku = 'JUNODS76'
                if sku == 'JUNO-X':
                    sku = 'JUNOX'
                if sku == 'K-25M':
                    sku = 'K25M'
                if sku == 'KPD70BK':
                    sku = 'KPD70BK'
                if sku == 'KPD90BK':
                    sku = 'KPD90BK'
                if sku == 'KSC90BK':
                    sku = 'KSC90BK'
                if sku == 'MC-101':
                    sku = 'MC101'
                if sku == 'MC-707':
                    sku = 'MC707'
                if sku == 'MB-CUBE':
                    sku = 'MB-CUBE'
                if sku == 'MV-1':
                    sku = 'MV1'
                if sku == 'PSB-240A':
                    sku = 'PSB240A'
                if sku == 'RH-200S':
                    sku = 'RH200S'
                if sku == 'RH-5':
                    sku = 'RH5'
                if sku == 'RH-A7':
                    sku = 'RHA7BK'
                if sku == 'RUBIX44':
                    sku = 'RUBIX44'
                if sku == 'SCG61W3':
                    sku = 'SCG61W3'
                if sku == 'SCG76W3':
                    sku = 'SCG76W3'
                if sku == 'SCG88W3':
                    sku = 'SCG88W3'
                if sku == 'SP404MK2':
                    sku = 'SP404MK2'
                if sku == 'SPD1E':
                    sku = 'SPD1E'
                if sku == 'SPD1P':
                    sku = 'SPD1P'
                if sku == 'SPD-SX':
                    sku = 'SPDSX'
                if sku == 'SPD-SXPRO':
                    sku = 'SPDSXPRO'
                if sku == 'SPD-SXSE':
                    sku = 'SPDSXSE'
                if sku == 'T-8':
                    sku = 'T8'
                if sku == 'TD-07DMK':
                    sku = 'TD07DMK'
                if sku == 'TR-06':
                    sku = 'TR06'
                if sku == 'TR-6S':
                    sku = 'TR6S'
                if sku == 'TR-8S':
                    sku = 'TR8S'
                if sku == 'UM-ONEMK2':
                    sku = 'UMONEMK2'
                if sku == 'VAD-103':
                    sku = 'VAD103S'
                if sku == 'VR09B':
                    sku = 'VR09B'
                if sku == 'VT-4':
                    sku = 'VT4'
                if sku == 'A-49WH':
                    sku = 'A49WH'
                if sku == 'AX-EDGEWH':
                    sku = 'AXEDGEW'
                if sku == 'BTY-NIMH':
                    sku = 'BTYNIMH'
                if sku == 'CB-CS2':
                    sku = 'CBCS2'
                if sku == 'CBGO61KP':
                    sku = 'CBGO61KP'
                if sku == 'CB-JDXI':
                    sku = 'CBJDXI'
                if sku == 'CBBDJ505':
                    sku = 'CBBDJ505'
                if sku == 'CBBSPDSX':
                    sku = 'CBBSPDSX'
                if sku == 'CBG61':
                    sku = 'CBG61'
                if sku == 'CBGDJ808':
                    sku = 'CBGDJ808'
                if sku == 'CM-30':
                    sku = 'CM30'
                if sku == 'CUBE-10GX':
                    sku = 'CUBE10GX'
                if sku == 'DP-10':
                    sku = 'DP10'
                if sku == 'EV-5':
                    sku = 'EV5'
                if sku == 'FP10BKS':
                    sku = 'FP10BKS'
                if sku == 'FP30XBK':
                    sku = 'FP30XBK'
                if sku == 'FP30XBKS':
                    sku = 'FP30XBKS'
                if sku == 'FP30XWHS':
                    sku = 'FP30XWHS'
                if sku == 'FP60XBKS':
                    sku = 'FP60XBKS'
                if sku == 'FP60XWH':
                    sku = 'FP60XWH'
                if sku == 'FP60XWHS':
                    sku = 'FP60XWHS'
                if sku == 'FP90XBK':
                    sku = 'FP90XBK'
                if sku == 'FP90XBKS':
                    sku = 'FP90XBKS'
                if sku == 'FP90XWH':
                    sku = 'FP90XWH'
                if sku == 'FP90XWHS':
                    sku = 'FP90XWHS'
                if sku == 'SH-01':
                    sku = 'SH01'
                if sku == 'GOPIANO61P':
                    sku = 'GO61P'
                if sku == 'GO61K':
                    sku = 'GO61K'
                if sku == 'GOPIANO88':
                    sku = 'GO88P'
                if sku == 'HPD-20':
                    sku = 'HPD20'
                if sku == 'HS-5':
                    sku = 'HS5'
                if sku == 'JUNO-DS88':
                    sku = 'JUNODS88'
                if sku == 'JX-08':
                    sku = 'JX08'
                if sku == 'KC-600':
                    sku = 'KC600'
                if sku == 'KPD70WH':
                    sku = 'KPD70WH'
                if sku == 'KPD90WH':
                    sku = 'KPD90WH'
                if sku == 'KSC70BK':
                    sku = 'KSC70BK'
                if sku == 'KSC70WH':
                    sku = 'KSC70WH'
                if sku == 'KSC72BK':
                    sku = 'KSC72BK'
                if sku == 'KSC90WH':
                    sku = 'KSC90WH'
                if sku == 'KSCFP10BK':
                    sku = 'KSCFP10BK'
                if sku == 'MOBILE-AC':
                    sku = 'MOBILE-AC'
                if sku == 'MX-1':
                    sku = 'MX1'
                if sku == 'PDS20':
                    sku = 'PDS20'
                if sku == 'PSB-12U':
                    sku = 'PSB12U'
                if sku == 'R-07BK':
                    sku = 'R07BK'
                if sku == 'R-07RD':
                    sku = 'R07RD'
                if sku == 'R-07WH':
                    sku = 'R07WH'
                if sku == 'RH-200':
                    sku = 'RH200'
                if sku == 'RH-300':
                    sku = 'RH300'
                if sku == 'RH-300V':
                    sku = 'RH300V'
                if sku == 'RUBIX22':
                    sku = 'RUBIX22'
                if sku == 'RUBIX24':
                    sku = 'RUBIX24'
                if sku == 'SE-02':
                    sku = 'SE02'
                if sku == 'SH-01A':
                    sku = 'SH01A'
                if sku == 'SH-4D':
                    sku = 'SH4D'
                if sku == 'SPD1K':
                    sku = 'SPD1K'
                if sku == 'SPD1W':
                    sku = 'SPD1W'
                if sku == 'SPD-20PRO':
                    sku = 'SPD20PRO'
                if sku == 'SYSTEM-8':
                    sku = 'SYSTEM8'
                if sku == 'TB-3':
                    sku = 'TB3'
                if sku == 'TD07KV':
                    sku = 'TD07KV'
                if sku == 'TD1DMK':
                    sku = 'TD1DMK'
                if sku == 'TR-8':
                    sku = 'TR8'
                if sku == 'VP-03':
                    sku = 'VP03'
                if sku == 'VR1HD':
                    sku = 'VR1HD'
                if sku == 'VR730':
                    sku = 'VR730'
                if sku == 'DJ-202':
                    sku = 'DJ202'

            if 'hosa' in brand.lower():
                sku = sku.replace('-', '')



            if 'radial' in brand.lower():
                if sku == 'JDI':
                    sku = 'RA-JDI'
                if sku == 'JDI-STEREO':
                    sku = 'RA-JDI-STEREO'
                if sku == 'KEY-LARGO':
                    sku = 'RA-KEY-LARGO'
                if sku == 'PRO48':
                    sku = 'RA-PRO48'
                if sku == 'PRO-D2':
                    sku = 'RA-PRO-D2'
                if sku == 'SB-5':
                    sku = 'RA-SB-5'
                if sku == 'TRIM-TWO':
                    sku = 'RA-TRIM2'
                if sku == 'USB-PRO':
                    sku = 'RA-USB-PRO'
                if sku == 'BT-PRO-V2':
                    sku = 'RA-BT-PRO-V2'
                if sku == 'J33':
                    sku = 'RA-J33'
                if sku == 'J48':
                    sku = 'RA-J48'
                if sku == 'J48-STEREO':
                    sku = 'RA-J48-STEREO'
                if sku == 'PROAV1':
                    sku = 'RA-PROAV1'
                if sku == 'PROAV1':
                    sku = 'RA-PROAV1'
                if sku == 'PRO-DI':
                    sku = 'RA-PRO-DI'
                if sku == 'SB-1':
                    sku = 'RA-SB-1'
                if sku == 'SB-2':
                    sku = 'RA-SB-2'
                if sku == 'VOCO-LOCO':
                    sku = 'RA-VOCO-LOCO'


            if 'se electronics' in brand.lower():
                if sku == 'SE-DM1':
                    sku = 'SEEL_DM1MICPRE'
                if sku == 'SE-DM2':
                    sku = 'SEEL_DM2'
                if sku == 'SE-DM3':
                    sku = 'SEEL_DM3'
                if sku == 'sE-DUALPOP':
                    sku = 'SEEL_DUALPOP'
                if sku == 'SE-DYNACASTERDCM3':
                    sku = 'SEEL_DYNACASTER_DCM3'
                if sku == 'SE-ISOLATIONPACK':
                    sku = 'SEEL_ISOLATIONP'
                if sku == 'SE-DYNACASTER':
                    sku = 'SEEL_DYNACASTER'
                if sku == 'NEOM':
                    sku = 'SEEL_NEOMUSB'
                if sku == 'SE-RFBK':
                    sku = 'SEEL_RFBLACK'
                if sku == 'SE-RFX':
                    sku = 'SEEL_RFX'
                if sku == 'SE-RFXRD':
                    sku = 'SEEL_RFXRED'
                if sku == 'SE-RFXWH':
                    sku = 'SEEL_RFXWHITE'
                if sku == 'SE-RN17':
                    sku = 'SEEL_RN17'
                if sku == 'SE-RN17MP':
                    sku = 'SEEL_RN17ST'
                if sku == 'SE-RNR':
                    sku = 'SEEL_RNR1'
                if sku == 'SE-RNT':
                    sku = 'SEEL_RNT'
                if sku == 'SE-2200':
                    sku = 'SEEL_2200'
                if sku == 'SE-V7BK':
                    sku = 'SEEL_V7BLACK'
                if sku == 'SE-V7CH':
                    sku = 'SEEL_V7CHROME'
                if sku == 'SE-V7VE':
                    sku = 'SEEL_V7VE'
                if sku == 'SE-7':
                    sku = 'SEEL_SE7'
                if sku == 'SE-7PAIR':
                    sku = 'SEEL_SE7PAIR'
                if sku == 'SE-2200VE':
                    sku = 'SEEL_2200VE'
                if sku == 'SE-2300':
                    sku = 'SEEL_2300'
                if sku == 'SE-4400MP':
                    sku = 'SEEL_4400AST'
                if sku == 'SE-8':
                    sku = 'SEEL_SE8'
                if sku == 'SE-8PAIR':
                    sku = 'SEEL_SE8PAIR'
                if sku == 'SE-RFSPACE':
                    sku = 'SEEL_RFSPACE'
                if sku == 'SE-ARENA':
                    sku = 'SEEL_VPACKARENA'
                if sku == 'SE-V3':
                    sku = 'SEEL_V3'
                if sku == 'SE-V7':
                    sku = 'SEEL_V7'
                if sku == 'SE-V7MC1':
                    sku = 'SEEL_V7MC1'
                if sku == 'SE-V7MC1BK':
                    sku = 'SEEL_V7MC1BLACK'
                if sku == 'SE-V7MC2':
                    sku = 'SEEL_V7MC2'
                if sku == 'SE-V7X':
                    sku = 'SEEL_V7X'
                if sku == 'SE-VCLAMP':
                    sku = 'SEEL_VCLAMP'
                if sku == 'SE-VR2':
                    sku = 'SEEL_VR2'
                if sku == 'SE-X1A':
                    sku = 'SEEL_X1A'
                if sku == 'SE-X1S':
                    sku = 'SEEL_X1S'
                if sku == 'SE-X1SPACK':
                    sku = 'SEEL_X1SPACKAGE'
                if sku == 'SE-X1VOCAL':
                    sku = 'SEEL_X1SVOCALPACK'
                if sku == 'SE-POP':
                    sku = 'SEEL_POP'
                if sku == 'SE-RF':
                    sku = 'SEEL_RF'
                if sku == 'SE-VR1':
                    sku = 'SEEL_VR1'
                if sku == 'SE-Z5600AII':
                    sku = 'SEEL_Z5600AII'
                if sku == 'SE-GEMINI':
                    sku = 'SEEL_GEMINIII'
                if sku == 'SE-RFXBS':
                    sku = 'SEEL_RFX_BLSW'
                if sku == 'SE-VBEAT':
                    sku = 'SEEL_VBEAT'
                if sku == 'SE-VKICK':
                    sku = 'SEEL_VKICK'
                if sku == 'SE-8PAIR-OMNI':
                    sku = 'SEEL_SE8OMNIP'
                if sku == 'SE-8PAIRVE':
                    sku = 'SEEL_SE8PVE'
                if sku == 'SE-4400A':
                    sku = 'SEEL_4400A'
                if sku == 'SE-VR1VE':
                    sku = 'SEEL_VR1VE'
                if sku == 'SE-GUITARF':
                    sku = 'SEEL_GUITARF'


            if 'source audio' in brand.lower():

                if sku == 'DAISY-CHAIN':
                    sku = '160DCC'
                if sku == 'DUAL-EXPRESSION':
                    sku = '161DEP'
                if sku == 'HOT-HAND':
                    sku = '115WRS'
                if sku == 'SOLEMAN':
                    sku = '165'
                if sku == 'NEURO':
                    sku = '164MPW'

                sku = f'SA-{sku}CMI'

            if 'auralex' in brand.lower():
                sku = f'62{sku}EF'

            if 'alto' in brand.lower():
                sku = f'57{sku}EF'

            if brand.lower() == 'udg':
                sku = f'63{sku}EF'

            if 'nektar' in brand.lower():

                if sku == 'AURA':
                    sku = 'NEKT_AURA'
                if sku == 'IMPACT-GX49':
                    sku = 'NEKT_GX49'
                if sku == 'IMPACT-GX61':
                    sku = 'NEKT_GX61'
                if sku == 'IMPACT-GXP49':
                    sku = 'NEKT_GXP49'
                if sku == 'IMPACT-GXP61':
                    sku = 'NEKT_GXP61'
                if sku == 'IMPACT-GXP88':
                    sku = 'NEKT_GXP88'
                if sku == 'IMPACT-GXMINI':
                    sku = 'NEKT_GXMINI'
                if sku == 'IMPACT-LX25PLUS':
                    sku = 'NEKT_LX25'
                if sku == 'IMPACT-LX49PLUS':
                    sku = 'NEKT_LX49'
                if sku == 'IMPACT-LX61PLUS':
                    sku = 'NEKT_LX61'
                if sku == 'IMPACT-LX88PLUS':
                    sku = 'NEKT_LX88'
                if sku == 'IMPACT-LXMINI':
                    sku = 'NEKT_LXMINI'
                if sku == 'PACER':
                    sku = 'NEKT_PACER'
                if sku == 'PANORAMA-T4':
                    sku = 'NEKT_PANORAMAT4'
                if sku == 'PANORAMA-T6':
                    sku = 'NEKT_PANORAMAT6'
                if sku == 'SE25':
                    sku = 'NEKT_SE25'
                if sku == 'SE49':
                    sku = 'NEKT_SE49'
                if sku == 'NP-1':
                    sku = 'NEKT_NP-1'
                if sku == 'NP-2':
                    sku = 'NEKT_NP-2'
                if sku == 'PANORAMA-P4':
                    sku = 'NEKT_PANORAMAP4'
                if sku == 'PANORAMA-P6':
                    sku = 'NEKT_PANORAMAP6'
                if sku == 'NX-P':
                    sku = 'NEKT_NX-P'
                if sku == 'PANORAMA-P1':
                    sku = 'NEKT_PANORAMAP1'


            if 'native instruments' in brand.lower():

                if sku == 'KOMPLETE-AUDIO6MK2':
                    sku = 'NI-KA6CMI'
                if sku == 'KONTROL-A25':
                    sku = 'NI-KKA25CMI'
                if sku == 'KONTROL-A49':
                    sku = 'NI-KKA49CMI'
                if sku == 'KONTROL-A61':
                    sku = 'NI-KKA61CMI'
                if sku == 'NI-K13':
                    sku = 'NI-K13CMI'
                if sku == 'NI-K13S':
                    sku = 'NI-K13SCMI'
                if sku == 'NI-K13U':
                    sku = 'NI-K13UCMI'
                if sku == 'NI-K13UCEUPGK13':
                    sku = 'NI-K13UCEUPK13CMI'
                if sku == 'NI-K13UUPD':
                    sku = 'NI-K13UUPDCMI'
                if sku == 'NI-K13UPGK13':
                    sku = 'NI-K13UPGK13CMI'
                if sku == 'NI-K13UUPGKS':
                    sku = 'NI-K13UUPGKSCMI'
                if sku == 'NI-K13UPG':
                    sku = 'NI-K13UPGCMI'
                if sku == 'NI-K14UCE':
                    sku = 'NI-K14UCECMI'
                if sku == 'NI-K14UCEUPD':
                    sku = 'NI-K14UCEUPDCMI'
                if sku == 'NI-K14UCEUPGK14':
                    sku = 'NI-K14UCEUPGK14CMI'
                if sku == 'NI-K14UCEUPGU14':
                    sku = 'NI-K14UCEUPGU14CMI'
                if sku == 'NI-K14S':
                    sku = 'NI-K14SCMI'
                if sku == 'NI-K14SUPG':
                    sku = 'NI-K14SUPGCMI'
                if sku == 'NI-K14':
                    sku = 'NI-K14CMI'
                if sku == 'NI-K14UPD':
                    sku = 'NI-K14UPDCMI'
                if sku == 'NI-K14UPG':
                    sku = 'NI-K14UPGCMI'
                if sku == 'NI-K14UPGC':
                    sku = 'NI-K14UPGCCMI'
                if sku == 'NI-K14U':
                    sku = 'NI-K14UCMI'
                if sku == 'NI-K14UUPD':
                    sku = 'NI-K14UUPDCMI'
                if sku == 'NI-K14UUPG':
                    sku = 'NI-K14UUPGCMI'
                if sku == 'NI-K14UUPGK14':
                    sku = 'NI-K14UUPGK14CMI'
                if sku == 'KOMPLETE-AUDIO1':
                    sku = 'NI-KA1CMI'
                if sku == 'KOMPLETE-AUDIO2':
                    sku = 'NI-KA2CMI'
                if sku == 'KONTROL-M32':
                    sku = 'NI-KKM32CMI'
                if sku == 'KONTROL-S49MK2':
                    sku = 'NI-KKS49MK2CMI'
                if sku == 'KONTROL-S61MK2':
                    sku = 'NI-KKS61MK2CMI'
                if sku == 'KONTROL-S88MK2':
                    sku = 'NI-KKS88MK2CMI'
                if sku == 'MASCHINEMIKRO-MK3':
                    sku = 'NI-MMIKROMK3CMI'
                if sku == 'MASCHINE-MK3':
                    sku = 'NI-MSCHMK3CMI'
                if sku == 'MASCHINE-PLUS':
                    sku = 'NI-MSCHPLUSCMI'
                if sku == 'VINYL-BLACK':
                    sku = 'NI-TRKSCVBKCMI'
                if sku == 'VINYL-BLUE':
                    sku = 'NI-TRKSCVBLCMI'
                if sku == 'VINYL-CLEAR':
                    sku = 'NI-TRKSCVCLCMI'
                if sku == 'VINYL-RED':
                    sku = 'NI-TRKSCVRDCMI'
                if sku == 'VINYL-WHITE':
                    sku = 'NI-TRKSCVWHCMI'
                if sku == 'TRKBR':
                    sku = 'NI-TRKBRCMI'
                if sku == 'TRKSCOCD':
                    sku = 'NI-TRKSCOCDCMI'
                if sku == 'TRKDJCABLE':
                    sku = 'NI-TRKDJCABLECMI'
                if sku == 'KONTROL-S3':
                    sku = 'NI-TKS3CMI'
                if sku == 'KONTROL-S4MK3':
                    sku = 'NI-TKS4MK3CMI'
                if sku == 'KONTROL-Z1':
                    sku = 'NI-KNTRLZ1CMI'
                if sku == 'KONTROL-F1':
                    sku = 'NI-KNTRLF1CMI'
                if sku == 'KONTROL-Z2':
                    sku = 'NI-KNTRLZ2CMI'
                if sku == 'KONTROL-S2MK3':
                    sku = 'NI-TKS2MK3CMI'
                if sku == 'KONTROL-S8':
                    sku = 'NI-KNTRLS8CMI'



            if 'm-audio' in brand.lower() or 'maudio' in brand.lower():

                if sku == 'AIR192X4':
                    sku = '46AIR192X4EF'
                if sku == 'AIR192X6':
                    sku = '46AIR192X6EF'
                if sku == 'BX3D4-BT':
                    sku = '46BX3D4-BTEF'
                if sku == 'BX4D3':
                    sku = '46BX4D3EF'
                if sku == 'BX4D4-BT':
                    sku = '46BX4D4-BTEF'
                if sku == 'BX5D3':
                    sku = '46BX5D3EF'
                if sku == 'BX8D3':
                    sku = '46BX8D3EF'
                if sku == 'EXP':
                    sku = '46EXPEF'
                if sku == 'KEYSTATION49-MK3':
                    sku = '46KEYSTATION49MK3EF'
                if sku == 'KEYSTATION61-MK3':
                    sku = '46KEYSTATION61MK3EF'
                if sku == 'KEYSTATION88-MK3':
                    sku = '46KEYSTATION88MK3EF'
                if sku == 'KEYSTATIONMINI32-MK3':
                    sku = '46KEYSTATIONMINI32MK3EF'
                if sku == 'MTRACK-SOLO':
                    sku = '46MTRACKSOLOEF'
                if sku == 'OXYGEN25V':
                    sku = '46OXYGEN25MKVEF'
                if sku == 'OXYGEN49V':
                    sku = '46OXYGEN49MKVEF'
                if sku == 'OXYGEN61V':
                    sku = '46OXYGEN61MKVEF'
                if sku == 'OXYGENPRO25':
                    sku = '46OXYGENPRO25EF'
                if sku == 'OXYGENPRO61':
                    sku = '46OXYGENPRO61EF'
                if sku == 'OXYGENPROMINI':
                    sku = '46OXYGENPROMINIEF'
                if sku == 'UBERMIC':
                    sku = '46UBERMICEF'
                if sku == 'AIR192X14':
                    sku = '46AIR192X14EF'
                if sku == 'AIR192X4SPRO':
                    sku = '46AIR192X4SPROEF'
                if sku == 'AIRXHUB':
                    sku = '46AIRXHUBEF'
                if sku == 'ACC-BASSTRAV':
                    sku = '46BASSTRAVELEREF'
                if sku == 'BX3D3':
                    sku = '46BX3D3EF'
                if sku == 'HAMMER88':
                    sku = '46HAMMER88EF'
                if sku == 'HAMMER88PRO':
                    sku = '46HAMMER88PROEF'
                if sku == 'MTRACK-DUO':
                    sku = '46MTRACKDUOEF'
                if sku == 'OXYGENPRO49':
                    sku = '46OXYGENPRO49EF'
                if sku == 'ACC-SP1':
                    sku = '46SP1EF'
                if sku == 'UNO':
                    sku = '46UNOEF'
                if sku == 'ACC-SP2':
                    sku = '46SP2EF'





            if 'alesis' in brand.lower():
                if sku == 'ASP-1MK2':
                    sku = 'ASP1MKII'
                if sku == 'HARMONY61-MK2':
                    sku = 'HARMONY61MK2'
                if sku == 'Q49MKII':
                    sku = 'Q49MK2'
                if sku == 'PRESTIGE-ARTIST':
                    sku = 'PRESTIGEARTIST'
                if sku == 'Q88MKII':
                    sku = 'Q88MK2'


                sku = fr'16{sku}EF'

            if 'ik multimedia' in brand.lower():
                if sku == 'IRIG-ACOUSTIC':
                    sku = 'IKMT_IP-IRIG-ACOUSTI'
                if sku == 'ILINE-KIT':
                    sku = 'IKMT_IP-ILINE-KIT-IN'
                if sku == 'ARC3':
                    sku = 'IKMT_AC-300-HCD'
                if sku == 'AXE-IO':
                    sku = 'IKMT_IP-INT-AXEIO'
                if sku == 'AXE-IOSOLO':
                    sku = 'IKMT_IP-INT-AXEIOSOLO'
                if sku == 'IKLIP-GRIPPRO':
                    sku = 'IKMT_IP-IKLIP-GPROB'
                if sku == 'IKLIP3-DLX':
                    sku = 'IKMT_IP-IKLIP-3DLX'
                if sku == 'IKLIP3':
                    sku = 'IKMT_IP-IKLIP-3'
                if sku == 'IKLIP3-VIDEO':
                    sku = 'IKMT_IP-IKLIP-3VIDEO'
                if sku == 'IRIG2':
                    sku = 'IKMT_IP-IRIG2-PLG-IN'
                if sku == 'ILOUD-MICROMONITORS':
                    sku = 'IKMT_IP-ILOUD-MM-IN'
                if sku == 'IRIG-HD2':
                    sku = 'IKMT_IP-IRIG-HD2-IN'
                if sku == 'IRIG-KEYS2PRO':
                    sku = 'IKMT_IP-IRIG-KEYS2PRO'
                if sku == 'IRIG-MICHD2':
                    sku = 'IKMT_IP-IRIG-MICHD2'
                if sku == 'IRIG-CAST2':
                    sku = 'IKMT_IP-IRIG-CAST2'
                if sku == 'IRIG-CASTHD':
                    sku = 'IKMT_IP-IRIG-CASTHD'
                if sku == 'IRIG-MICLAVDUAL':
                    sku = 'IKMT_IP-IRIG-MICLDUA'
                if sku == 'IRIG-MICVIDEOGP':
                    sku = 'IKMT_CB-MICVIDEOGP-HCD'
                if sku == 'IRIG-MICVIDEO':
                    sku = 'IKMT_IP-IRIG-MICVIDEO'
                if sku == 'IRIG-NANOAMPRD':
                    sku = 'IKMT_IP-NANOAMPR-IN'
                if sku == 'IRIG-PREHD':
                    sku = 'IKMT_IP-IRIG-PREHD'
                if sku == 'IRIG-NANOAMPWH':
                    sku = 'IKMT_IP-NANOAMPW-IN'
                if sku == 'IRIG-STREAMPRO':
                    sku = 'IKMT_IP-IRIG-STREAMPRO-IN'
                if sku == 'IRIG-VIDEOHD':
                    sku = 'IKMT_CB-MICHD2GP-HCD'
                if sku == 'IRIG-VIDEO':
                    sku = 'IKMT_CB-MICLAVGP-HCD'
                if sku == 'UNO-DRUM':
                    sku = 'IKMT_IP-UNO-DRUM'
                if sku == 'UNO-SYNTH':
                    sku = 'IKMT_IP-UNO-SYNTH-IN'
                if sku == 'UNO-SYNTHDESK':
                    sku = 'IKMT_IP-UNO-SYNTHPRODT'
                if sku == 'UNO-SYNTHPRO':
                    sku = 'IKMT_IP-UNO-SYNTHPRO'
                if sku == 'XGEAR-DRIVE':
                    sku = 'IKMT_XG-PEDAL-XDRIVE-IN'
                if sku == 'XGEAR-TIME':
                    sku = 'IKMT_XG-PEDAL-XTIME-IN'
                if sku == 'XGEAR-VIBE':
                    sku = 'IKMT_XG-PEDAL-XVIBE-IN'
                if sku == 'IRIG-PADS':
                    sku = 'IKMT_IP-IRIG-PADS-IN'
                if sku == 'IKLIP-GRIP':
                    sku = 'IKMT_IP-IKLIP-GRIP-I'
                if sku == 'IRIG-MIDI2':
                    sku = 'IKMT_IP-IRIG-MIDI2-I'
                if sku == 'IRIG-BLUEBOARD':
                    sku = 'IKMT_IP-IRIG-BBRD-IN'
                if sku == 'IRIG-BTURN':
                    sku = 'IKMT_IP-IRIG-BTURN'
                if sku == 'IRIG-UA':
                    sku = 'IKMT_IP-IRIG-UA-IN'
                if sku == 'IRIG-MIC':
                    sku = 'IKMT_IP-IRIG-MIC-IN'
                if sku == 'IRIG-MICVOW':
                    sku = 'IKMT_IP-IRIG-MICVOW-'
                if sku == 'IRIG-MICVOB':
                    sku = 'IKMT_IP-IRIG-MICVOB-'
                if sku == 'IRIG-MICVOP':
                    sku = 'IKMT_IP-IRIG-MICVOP-'
                if sku == 'IRIG-MICVOY':
                    sku = 'IKMT_IP-IRIG-MICVOY-'
                if sku == 'IKLIPXPAND-MINI':
                    sku = 'IKMT_IP-IKLIP-XPANDM'
                if sku == 'IRIG-KEYS25':
                    sku = 'IKMT_IP-IRIG-KEYS25'
                if sku == 'IRIG-MICROAMP':
                    sku = 'IKMT_IP-IRIG-MICROAMP'
                if sku == 'IRIG-STREAMSOLO':
                    sku = 'IKMT_IP-IRIG-STREAMSL-IN'
                if sku == 'IKLIP-AV':
                    sku = 'IKMT_IP-IKLIP-AV-IN'
                if sku == 'ILOUD-MTM':
                    sku = 'IKMT_IP-ILOUD-MTM'
                if sku == 'ILOUD-MICROMONITORSW':
                    sku = 'IKMT_IP-ILOUD-MMW-IN'
                if sku == 'IRIG-KEYS2':
                    sku = 'IKMT_IP-IRIG-KEYS2'
                if sku == 'IRIG-NANOAMP':
                    sku = 'IKMT_IP-NANOAMP-IN'
                if sku == 'IRIG-KEYS37':
                    sku = 'IKMT_IP-IRIG-KEYS37'
                if sku == 'IRIG-KEYS37PRO':
                    sku = 'IKMT_IP-IRIG-KEYSPR'
                if sku == 'IRIG-PRE2':
                    sku = 'IKMT_IP-IRIG-PRE2'
                if sku == 'IRIG-POWERBRIDGE':
                    sku = 'IKMT_IP-IRIG-PBRDG'
                if sku == 'IRIG-PRODUOIO':
                    sku = 'IKMT_IP-IRIG-PRODUOIO'
                if sku == 'IRIG-PROIO':
                    sku = 'IKMT_IP-IRIG-PROIO'
                if sku == 'IRIG-STREAM':
                    sku = 'IKMT_IP-IRIG-STREAM'
                if sku == 'IRIG-MICLAV':
                    sku = 'IKMT_IP-IRIG-MICLAV'
                if sku == 'IRIG-KEYIO25':
                    sku = 'IKMT_IP-IRIG-KEYIO25'
                if sku == 'IRIG-PROQUATTRO':
                    sku = 'IKMT_IP-IRIG-QUATTRO-IN'
                if sku == 'IRIG-PROQUATTRODLX':
                    sku = 'IKMT_IP-IRIG-QTRDLX-IN'
                if sku == 'XGEAR-SPACE':
                    sku = 'IKMT_XG-PEDAL-XSPACE-IN'
                if sku == 'IK-BTXP':
                    sku = 'IKMT_CB-BTXP-HCD-IN'
                if sku == 'IRIGMIC-STUDIOBL':
                    sku = 'IKMT_IP-IRIG-MICSTBL'
                if sku == 'IRIG-MICVOG':
                    sku = 'IKMT_IP-IRIG-MICVOG-'
                if sku == 'IKLIPXPAND':
                    sku = 'IKMT_IP-IKLIP-XPAND-'

            if 'samson' in brand.lower():
                if sku == 'C01UPRO':
                    sku = '29C01UPROEF'
                if sku == 'CM15P':
                    sku = '29CM15PEF'
                if sku == 'CON88-PRES':
                    sku = '14/CON88-PRESEF'
                if sku == 'CON288M-ALL-D':
                    sku = '14CON288M-ALL-DEF'
                if sku == 'CON288M-PRES-D':
                    sku = '14CON288M-PRES-DEF'
                if sku == 'DE50X':
                    sku = '14DE50XEF'
                if sku == 'DE60X':
                    sku = '14DE60XEF'
                if sku == 'GTRACKPRO':
                    sku = '29GTRACKPROEF'
                if sku == 'GOMIC':
                    sku = '29GOMICEF'
                if sku == 'LM8X':
                    sku = '14LM8XEF'
                if sku == 'MBA18':
                    sku = '29MBA18EF'
                if sku == 'MBA28':
                    sku = '29MBA28EF'
                if sku == 'MD5':
                    sku = '29MD5EF'
                if sku == 'METEOR':
                    sku = '29METEOREF'
                if sku == 'PS01':
                    sku = '29PS01EF'
                if sku == 'Q63P':
                    sku = '29Q63PEF'
                if sku == 'RXD2':
                    sku = '14RXD2EF'
                if sku == 'SR850':
                    sku = '29SR850EF'
                if sku == 'SRK12':
                    sku = '29SRK12EF'
                if sku == 'CON88-ALL':
                    sku = '14CON88-ALLEF'
                if sku == 'CON88-DUAL':
                    sku = '14CON88-HANDHELD-DUALEF'
                if sku == 'XP106W':
                    sku = '29XP106WEF'
                if sku == 'XP208W':
                    sku = '29XP208WEF'
                if sku == 'XP310W':
                    sku = '29XP310WEF'
                if sku == 'XP312W':
                    sku = '29XP312WEF'
                if sku == 'XPD2-HEADSET':
                    sku = '14XPD2-HEADSETEF'
                if sku == 'XPD2-PRES':
                    sku = '14XPD2-PRESEF'
                if sku == 'XP106':
                    sku = '29XP106EF'
                if sku == 'LTS50':
                    sku = '29LTS50EF'
                if sku == 'RESOLVSEA5':
                    sku = '29RESOLVSEA5EF'
                if sku == 'RESOLVSEA6':
                    sku = '29RESOLVSEA6EF'
                if sku == 'AIR99-FITNESS':
                    sku = '14AIR99M-FITNESSEF'
                if sku == 'AIR99-VOCAL':
                    sku = '14AIR99M-VOCALEF'
                if sku == 'CL7A':
                    sku = '29CL7AEF'
                if sku == 'CL8A':
                    sku = '29CL8AEF'
                if sku == 'CON88X-HANDHELD-D':
                    sku = '14CON88X-HANDHELD-DEF'
                if sku == 'CON88X-HEADSET-D':
                    sku = '14CON88X-HEADSET-DEF'
                if sku == 'CON88X-LAPEL-D':
                    sku = '14CON88X-LAPEL-DEF'
                if sku == 'LM7X':
                    sku = '14LM7XEF'
                if sku == 'MBA38':
                    sku = '29MBA38EF'
                if sku == 'MD2PRO':
                    sku = '29MD2PROEF'
                if sku == 'M30':
                    sku = '29M30EF'
                if sku == 'Q9U':
                    sku = '29Q9UEF'
                if sku == 'M50-SAM':
                    sku = '29M50EF'
                if sku == 'RL112A':
                    sku = '29RL112AEF'
                if sku == 'RL115A':
                    sku = '29RL115AEF'
                if sku == 'RESOLVSEA8':
                    sku = '29RESOLVSEA8EF'
                if sku == 'SATELLITE':
                    sku = '29SATELLITEEF'

            if 'akai' in brand.lower():
                if sku == 'APCMINIMK2':
                    sku = '69APCMINIEF'
                if sku == 'APCKEY25MK2':
                    sku = '69APCKEY25EF'
                if sku == 'EWI-SOLO':
                    sku = '69EWI-SOLOEF'
                if sku == 'EXP-PEDAL':
                    sku = '69EXPEF'
                if sku == 'FIRE':
                    sku = '69FIREEF'
                if sku == 'FIRENS':
                    sku = '69FIRENSEF'
                if sku == 'FORCE':
                    sku = '69FORCEEF'
                if sku == 'LPD8MK2':
                    sku = '69LPD8EF'
                if sku == 'LPK25MK2':
                    sku = '69LPK25EF'
                if sku == 'MPC-LIVE2':
                    sku = '69MPC-L2EF'
                if sku == 'MPC-KEY61':
                    sku = '69MPC-KEY61EF'
                if sku == 'MPC-ONE':
                    sku = '69MPC-OEF'
                if sku == 'MPC-STUDIO2':
                    sku = '69MPC-BSEF'
                if sku == 'MPKMINI-MK3':
                    sku = '69MPKMINI3EF'
                if sku == 'MPC-X':
                    sku = '69MPC-XEF'
                if sku == 'MPKMINI3-BK':
                    sku = '69MPKMINI3-BKEF'
                if sku == 'MPKMINI3-WH':
                    sku = '69MPKMINI3-WHEF'
                if sku == 'MPKMINI-PLAYMK3':
                    sku = '69MPKMINIPLAY3EF'
                if sku == 'MPKMINI-PLUS':
                    sku = '69MPKMINIPLUSEF'
                if sku == 'MPK249':
                    sku = '69MPK249EF'
                if sku == 'MPK261':
                    sku = '69MPK261EF'
                if sku == 'MPK225':
                    sku = '69MPK225EF'
                if sku == 'MPD218':
                    sku = '69MPD218EF'
                if sku == 'MPD226':
                    sku = '69MPD226EF'
                if sku == 'APC40MKII':
                    sku = '69APC40MK2EF'
                if sku == 'EWI-SOLO-WH':
                    sku = '69EWI-SOLO-WHEF'
                if sku == 'MPK249-BK':
                    sku = '69MPK249-BKEF'
                if sku == 'MPX8':
                    sku = '69MPX8EF'
                if sku == 'APCKEY25':
                    sku = '69EF'
                if sku == 'APCMINI':
                    sku = '69APCMINIEF'
                if sku == 'EWI5000':
                    sku = '69EWI5000EF'
                if sku == 'MPX16':
                    sku = '69MPX16EF'

            if 'headrush' in brand.lower():
                if sku == 'HEADRUSH-EXP':
                    sku = '11HREXPEF'
                if sku == 'FRFR112':
                    sku = '11FRFR112EF'
                if sku == 'MX5':
                    sku = '11MX5EF'
                if sku == 'HEADRUSH':
                    sku = '11HEADRUSHEF'
                if sku == 'FRFR108':
                    sku = '11FRFR108EF'

            if 'xvive' in brand.lower():
                if sku == 'MD1':
                    sku = '352447AUSTRALIS'
                if sku == 'XVIVE-P1':
                    sku = '352446AUSTRALIS'
                if sku == 'U2-CARBON':
                    sku = '352444AUSTRALIS'
                if sku == 'U2-GREY':
                    sku = '352334AUSTRALIS'
                if sku == 'U2-WOOD':
                    sku = '352445AUSTRALIS'
                if sku == 'U5':
                    sku = '352571AUSTRALIS'
                if sku == 'U5C':
                    sku = '352573AUSTRALIS'
                if sku == 'U5T':
                    sku = '352574AUSTRALIS'
                if sku == 'U5R':
                    sku = '352575AUSTRALIS'
                if sku == 'U5T2':
                    sku = '352572AUSTRALIS'
                if sku == 'U6':
                    sku = '352581AUSTRALIS'
                if sku == 'V21':
                    sku = '352563AUSTRALIS'
                if sku == 'LV2':
                    sku = '352577AUSTRALIS'
                if sku == 'H1':
                    sku = '352338AUSTRALIS'
                if sku == 'LV1':
                    sku = '352576AUSTRALIS'
                if sku == 'U2-BK':
                    sku = '352333AUSTRALIS'
                if sku == 'U3':
                    sku = '352555AUSTRALIS'
                if sku == 'U3C':
                    sku = '352559AUSTRALIS'
                if sku == 'U4':
                    sku = '352565AUSTRALIS'
                if sku == 'U4R2':
                    sku = '352568AUSTRALIS'
                if sku == 'U4R4':
                    sku = '352569AUSTRALIS'


            if 'armour' in brand.lower():
                if sku == 'ABDBR':
                    sku = '701310AUSTRALIS'
                if sku == 'ABDLP':
                    sku = '701315AUSTRALIS'
                if sku == 'APCSG':
                    sku = '701242AUSTRALIS'
                if sku == 'ARMSP12':
                    sku = '606132AUSTRALIS'
                if sku == 'ARMUNOB':
                    sku = '604212AUSTRALIS'
                if sku == 'ARMUNOC':
                    sku = '604217AUSTRALIS'
                if sku == 'ARMUNOG':
                    sku = '604210AUSTRALIS'
                if sku == 'ARMUNOW':
                    sku = '604215AUSTRALIS'
                if sku == 'ARM10SPX':
                    sku = '604410AUSTRALIS'
                if sku == 'ABDER':
                    sku = '701305AUSTRALIS'
                if sku == 'ARM12SPX':
                    sku = '604413AUSTRALIS'
                if sku == 'ARM15SPX':
                    sku = '604416AUSTRALIS'
                if sku == 'ARMSP15':
                    sku = '606135AUSTRALIS'



            if 'gator' in brand.lower():
                if sku == 'GIN-EAR-SYSTEM':
                    sku = '488339AUSTRALIS'
                if sku == 'G-MIXERBAG-1515':
                    sku = '488269AUSTRALIS'
                if sku == 'G-MIXERBAG-1815':
                    sku = '488270AUSTRALIS'
                if sku == 'G-MIXERBAG-1818':
                    sku = '488271AUSTRALIS'
                if sku == 'GLRODECASTER2':
                    sku = '488918AUSTRALIS'
                if sku == 'GLRODECASTER4':
                    sku = '488919AUSTRALIS'
                if sku == 'GM1WEVAA':
                    sku = '488342AUSTRALIS'
                if sku == 'GM1WP':
                    sku = '488343AUSTRALIS'
                if sku == 'GM-4':
                    sku = '488345AUSTRALIS'
                if sku == 'GR-4L':
                    sku = '488476AUSTRALIS'
                if sku == 'GR-6L':
                    sku = '488478AUSTRALIS'
                if sku == 'GTSA-KEY61':
                    sku = '488244AUSTRALIS'
                if sku == 'GTSA-KEY76D':
                    sku = '488246AUSTRALIS'
                if sku == 'GX33':
                    sku = '488369AUSTRALIS'
                if sku == 'GPA-712LG':
                    sku = '488307AUSTRALIS'
                if sku == 'GPA-712SM':
                    sku = '488308AUSTRALIS'
                if sku == 'GPA-715':
                    sku = '488309AUSTRALIS'
                if sku == 'GR-2L':
                    sku = '488473AUSTRALIS'
                if sku == 'GR-6S':
                    sku = '488479AUSTRALIS'
                if sku == 'GTSA-KEY49':
                    sku = '488243AUSTRALIS'
                if sku == 'GTSA-KEY88D':
                    sku = '488248AUSTRALIS'
                if sku == 'GTSA-KEY88SLXL':
                    sku = '488250AUSTRALIS'
                if sku == 'GTSA-KEY76':
                    sku = '488245AUSTRALIS'
                if sku == 'GTSA-KEY88':
                    sku = '488247AUSTRALIS'
                if sku == 'GTSA-MIX181806':
                    sku = '488297AUSTRALIS'
                if sku == 'GTSA-KEY88SL':
                    sku = '488249AUSTRALIS'
                if sku == 'GFWISOPADLG':
                    sku = '488915AUSTRALIS'
                if sku == 'GFWISOPADMD':
                    sku = '488913AUSTRALIS'
                if sku == 'GFWISOPADSM':
                    sku = '488914AUSTRALIS'
                if sku == 'GFWSPKSTMNDSK':
                    sku = '488907AUSTRALIS'
                if sku == 'GFWELITEDESKRKBRN':
                    sku = '488935AUSTRALIS'
                if sku == 'GFWELITEDESKBRN':
                    sku = '488933AUSTRALIS'
                if sku == 'GFWELITEDESKMPL':
                    sku = '488930AUSTRALIS'
                if sku == 'GFWSPKSTMNDSKCMP':
                    sku = '488908AUSTRALIS'
                if sku == 'GELITESM-BK':
                    sku = '488948AUSTRALIS'
                if sku == 'GFWMIC2020':
                    sku = '488430AUSTRALIS'
                if sku == 'GFWMICACCTRAY':
                    sku = '488435AUSTRALIS'
                if sku == 'GFWDESKMAIN':
                    sku = '488926AUSTRALIS'

            if 'ashton' in brand.lower():
                if sku == 'AG232BK':
                    sku = '509570AUSTRALIS'
                if sku == 'AG232TDB':
                    sku = '509580AUSTRALIS'
                if sku == 'AG232TSB':
                    sku = '509575AUSTRALIS'
                if sku == 'D20BK':
                    sku = '505177AUSTRALIS'
                if sku == 'JOEYBK':
                    sku = '505321AUSTRALIS'
                if sku == 'JOEY-RD':
                    sku = '505326AUSTRALIS'
                if sku == 'APWCC':
                    sku = '700245AUSTRALIS'
                if sku == 'PK-D20BK':
                    sku = '505185PAUSTRALIS'
                if sku == 'PK-D20NTM':
                    sku = '505156PAUSTRALIS'
                if sku == 'D20NTM':
                    sku = '505149AUSTRALIS'
                if sku == 'D20SCEQ':
                    sku = '412558AUSTRALIS'
                if sku == 'D20SNTM':
                    sku = '412555AUSTRALIS'
                if sku == 'D20TSB':
                    sku = '505178AUSTRALIS'
                if sku == 'PK-D20TSB':
                    sku = '505186PAUSTRALIS'
                if sku == 'GA10':
                    sku = '300532AUSTRALIS'



            if 'helicon' in brand.lower():
                if sku == 'GO-GUITAR':
                    sku = '455099AUSTRALIS'
                if sku == 'GO-SOLO':
                    sku = '455101AUSTRALIS'
                if sku == 'GO-VOCAL':
                    sku = '455103AUSTRALIS'
                if sku == 'GO-XLR':
                    sku = '455104AUSTRALIS'
                if sku == 'GO-XLRMINI':
                    sku = '455106AUSTRALIS'
                if sku == 'MIC-MECHANIC2':
                    sku = '455111AUSTRALIS'
                if sku == 'PERFORM-VK':
                    sku = '455115AUSTRALIS'
                if sku == 'VL-PLAY-ACSTC':
                    sku = '455116AUSTRALIS'
                if sku == 'TALKBOX-SYNTH':
                    sku = '455120AUSTRALIS'
                if sku == 'VT-E1':
                    sku = '455125AUSTRALIS'
                if sku == 'VT-T1':
                    sku = '455128AUSTRALIS'
                if sku == 'BLENDER':
                    sku = '455093AUSTRALIS'
                if sku == 'DITTO-MIC':
                    sku = '455095AUSTRALIS'
                if sku == 'CRITICAL-MASS':
                    sku = '455094AUSTRALIS'
                if sku == 'DUPLICATOR':
                    sku = '455096AUSTRALIS'
                if sku == 'GO-GUITARPRO':
                    sku = '455100AUSTRALIS'
                if sku == 'HARM-SINGER2':
                    sku = '455107AUSTRALIS'
                if sku == 'PERFORM-VE':
                    sku = '455113AUSTRALIS'
                if sku == 'PERFORM-VG':
                    sku = '455114AUSTRALIS'
                if sku == 'VL3-EXTREME':
                    sku = '455121AUSTRALIS'
                if sku == 'VL-PLAY':
                    sku = '455112AUSTRALIS'
                if sku == 'VT-D1':
                    sku = '455124AUSTRALIS'
                if sku == 'VT-H1':
                    sku = '455126AUSTRALIS'
                if sku == 'VT-R1':
                    sku = '455127AUSTRALIS'
                if sku == 'VT-X1':
                    sku = '455129AUSTRALIS'
                if sku == 'VT-C1':
                    sku = '455123AUSTRALIS'



            if brand.lower() == 'blackstar':
                if sku == 'BLA-AMPED2':
                    sku = 'BS-AMPED2CMI'
                if sku == 'BLA-FLY3':
                    sku = 'FLY-3CMI'
                if sku == 'BLA-AMPED1':
                    sku = 'BS-AMPED1CMI'
                if sku == 'BLA-IDCORE10CV3':
                    sku = 'ID-CORE10CV3CMI'
                if sku == 'BLA-FLYAMPLUG':
                    sku = 'FLY-AMPLUGCMI'
                if sku == 'BLA-FLY3BASS':
                    sku = 'FLY-3BASSCMI'
                if sku == 'BLA-FLY3BT':
                    sku = 'FLY-3BTCMI'
                if sku == 'BLA-IDCORE100C':
                    sku = 'ID-CORE100CCMI'
                if sku == 'BLA-FLYAMPLUGB':
                    sku = 'FLY-AMPLUGBCMI'
                if sku == 'BLA-DEBUT15E':
                    sku = 'DEBUT-15ECMI'
                if sku == 'BLA-IDCORE150C':
                    sku = 'ID-CORE150CCMI'
                if sku == 'BLA-DEBUT10E':
                    sku = 'DEBUT-10ECMI'
                if sku == 'BLA-IDCORE20CV3':
                    sku = 'ID-CORE20CV3CMI'
                if sku == 'BLA-FLYPACKBASS':
                    sku = 'FLY-PACKBASSCMI'
                if sku == 'BLA-DP10BOOST':
                    sku = 'BS-DP10BOOSTCMI'
                if sku == 'BLA-IDCORE40CV3':
                    sku = 'ID-CORE40CV3CMI'
                if sku == 'BLA-FLY103':
                    sku = 'FLY-103CMI'
                if sku == 'BLA-FLY103ACO':
                    sku = 'FLY-103ACOCMI'
                if sku == 'BLA-HT5RHMK2':
                    sku = 'HT-5RHMK2CMI'
                if sku == 'BLA-DP10DRIVE':
                    sku = 'BS-DP10DRIVECMI'
                if sku == 'BLA-HT5RCMK2':
                    sku = 'HT-5RCMK2CMI'
                if sku == 'BLA-DP10DIST':
                    sku = 'BS-DP10DISTCMI'
                if sku == 'BLA-FLYSUPERFLY':
                    sku = 'FLY-SUPERFLYCMI'
                if sku == 'BLA-HT1RCMK2':
                    sku = 'HT-1RCMK2CMI'
                if sku == 'BLA-LIVELOGIC':
                    sku = 'BS-LIVELOGICCMI'
                if sku == 'BLA-U500':
                    sku = 'U-500CMI'
                if sku == 'BLA-ACCORE30C':
                    sku = 'AC-CORE30CCMI'
                if sku == 'BLA-IDCOREBEAM':
                    sku = 'ID-COREBEAMCMI'
                if sku == 'BLA-HT112MK2':
                    sku = 'HT-112MK2CMI'
                if sku == 'BLA-HT1RHMK2':
                    sku = 'HT-1RHMK2CMI'
                if sku == 'BLA-U30':
                    sku = 'U-30CMI'
                if sku == 'BLA-U60':
                    sku = 'U-60CMI'
                if sku == 'BLA-FS14':
                    sku = 'FS-14CMI'
                if sku == 'BLA-FLYSFLYCAB':
                    sku = 'FLY-SFLYCABCMI'
                if sku == 'BLA-FLYSFLYPACK':
                    sku = 'FLY-SFLYPACKCMI'
                if sku == 'BLA-BSCOGBK':
                    sku = 'BS-COGBKCMI'
                if sku == 'BLA-BSCOGWH':
                    sku = 'BS-COGWHCMI'
                if sku == 'BLA-FLY3ACO':
                    sku = 'FLY-3ACOCMI'
                if sku == 'BLA-FLYPACK':
                    sku = 'FLY-PACKCMI'
                if sku == 'BLA-FLYPACKAC':
                    sku = 'FLY-PACKACCMI'
                if sku == 'BLA-FLYSFLYBAG':
                    sku = 'FLY-SFLYBAGCMI'
                if sku == 'BLA-FLYSFLYPSU':
                    sku = 'FLY-SFLYPSUCMI'
                if sku == 'BLA-FS12':
                    sku = 'FS-12CMI'
                if sku == 'BLA-FS2':
                    sku = 'FS-2CMI'
                if sku == 'BLA-FS6':
                    sku = 'FS-6CMI'
                if sku == 'BLA-HT20CMK2':
                    sku = 'HT-20CMK2CMI'
                if sku == 'BLA-HT20HMK2':
                    sku = 'HT-20HMK2CMI'
                if sku == 'BLA-HT212VOC':
                    sku = 'HT-212VOCCMI'
                if sku == 'BLA-HTCLUB40CMK2':
                    sku = 'HT-CLUB40CMK2CMI'
                if sku == 'BLA-FPFC49':
                    sku = 'FP-FC49CMI'
                if sku == 'BLA-FLYPSU':
                    sku = 'FLY-PSUCMI'
                if sku == 'BLA-FS11':
                    sku = 'FS-11CMI'
                if sku == 'BLA-FLYSFLYBAT':
                    sku = 'FLY-SFLYBATCMI'
                if sku == 'BLA-FS3':
                    sku = 'FS-3CMI'
                if sku == 'BLA-FS4':
                    sku = 'FS-4CMI'
                if sku == 'BLA-FS7':
                    sku = 'FS-7CMI'
                if sku == 'BLA-FS8':
                    sku = 'FS-8CMI'
                if sku == 'BLA-FS9':
                    sku = 'FS-9CMI'



            if 'orange' in brand.lower():

                if sku == 'ACOUSTIC-PEDAL':
                    sku = '8900131AUSTRALIS'
                if sku == 'CRUSH12':
                    sku = '8900036AUSTRALIS'
                if sku == 'CRUSH20RT':
                    sku = '8900040AUSTRALIS'
                if sku == 'CRUSH-MINI':
                    sku = '8900035AUSTRALIS'
                if sku == 'CRUSH12-BK':
                    sku = '8900037AUSTRALIS'
                if sku == 'CRUSH20-BK':
                    sku = '8900039AUSTRALIS'
                if sku == 'CRUSH20':
                    sku = '8900038AUSTRALIS'
                if sku == 'CRUSH20RT-BK':
                    sku = '8900041AUSTRALIS'
                if sku == 'CRUSH35RT':
                    sku = '8900042AUSTRALIS'
                if sku == 'CRUSH-BASS25':
                    sku = '8900044AUSTRALIS'
                if sku == 'CRUSH-BASS50':
                    sku = '8900045AUSTRALIS'
                if sku == 'MICRO-DARK':
                    sku = '8900024AUSTRALIS'
                if sku == 'MICRO-TERROR':
                    sku = '8900023AUSTRALIS'

            if 'korg' in brand.lower():
                if sku == 'NANOKONTROL2-WH':
                    sku = 'KO-NANOKNTRL2WHCMI'
                if sku == 'DS-DAC-100M':
                    sku = 'KO-DSDAC100MCMI'
                if sku == 'DS-DAC-100':
                    sku = 'KO-DSDAC100CMI'
                if sku == 'ARP2600M':
                    sku = 'KO-ARP2600MCMI'
                if sku == 'B1ST-BK':
                    sku = 'KO-B1STBKCMI'
                if sku == 'B2-BK':
                    sku = 'KO-B2BKCMI'
                if sku == 'B2-WH':
                    sku = 'KO-B2WHCMI'
                if sku == 'B2N':
                    sku = 'KO-B2BNCMI'
                if sku == 'B2SP-BK':
                    sku = 'KO-B2SPBKCMI'
                if sku == 'B2SP-WH':
                    sku = 'KO-B2SPWHCMI'
                if sku == 'D1':
                    sku = 'KO-D1CMI'
                if sku == 'D1-WH':
                    sku = 'KO-D1WHCMI'
                if sku == 'DRUMLOGUE':
                    sku = 'KO-DRUMLOGUECMI'
                if sku == 'EK-50':
                    sku = 'KO-EK50CMI'
                if sku == 'EK-50L':
                    sku = 'KO-EK50LCMI'
                if sku == 'HAS':
                    sku = 'KO-HASCMI'
                if sku == 'I3-BK':
                    sku = 'KO-I3CMI'
                if sku == 'I3-SL':
                    sku = 'KO-I3SVCMI'
                if sku == 'KAOSSILATOR2S':
                    sku = 'KO-KAOSSILATOR2SCMI'
                if sku == 'KROME61EX':
                    sku = 'KO-KROME61EXCMI'
                if sku == 'KROME73EX':
                    sku = 'KO-KROME73EXCMI'
                if sku == 'NAUTILUS61':
                    sku = 'KO-NAUTILUS61CMI'
                if sku == 'NAUTILUS73':
                    sku = 'KO-NAUTILUS73CMI'
                if sku == 'NAUTILUS88':
                    sku = 'KO-NAUTILUS88CMI'
                if sku == 'LP-380BK':
                    sku = 'KO-LP380BKCMI'
                if sku == 'LP-380RW':
                    sku = 'KO-LP380RWCMI'
                if sku == 'LP-380WH':
                    sku = 'KO-LP380WHCMI'
                if sku == 'MICROKEY-25':
                    sku = 'KO-MICROKEY25CMI'
                if sku == 'MICROKEY2-AIR25':
                    sku = 'KO-MKEY225AIRCMI'
                if sku == 'MICROKEY2-AIR37':
                    sku = 'KO-MKEY237AIRCMI'
                if sku == 'MICROKORG-MK1':
                    sku = 'KO-MIKORGMK1CMI'
                if sku == 'MICROKORG-MK1S':
                    sku = 'KO-MIKORGMK1SCMI'
                if sku == 'MICROKORG-XL+':
                    sku = 'KO-MIKORGXL+CMI'
                if sku == 'MINIKORG-700FS':
                    sku = 'KO-MINI700FSCMI'
                if sku == 'MINILOGUE':
                    sku = 'KO-MINILOGUECMI'
                if sku == 'MINILOGUEXD':
                    sku = 'KO-MINILOGUEXDCMI'
                if sku == 'MINILOGUEXDM':
                    sku = 'KO-MINILOGUEXDMCMI'
                if sku == 'MINILOGUE-BASS':
                    sku = 'KO-MINILOGUEBACMI'
                if sku == 'MODWAVE':
                    sku = 'KO-MODWAVECMI'
                if sku == 'MONOLOG-BK':
                    sku = 'KO-MONOLOGBKCMI'
                if sku == 'MONOLOG-BL':
                    sku = 'KO-MONOLOGBLCMI'
                if sku == 'MONOLOG-SV':
                    sku = 'KO-MONOLOGSVCMI'
                if sku == 'MS20-MINIWH':
                    sku = 'KO-MS20MINIWHCMI'
                if sku == 'MW-2408':
                    sku = 'KO-MW2408CMI'
                if sku == 'NANOKEY-STUDIO':
                    sku = 'KO-NANOKEYSTCMI'
                if sku == 'NANOKONTROL-STUDIO':
                    sku = 'KO-NANOKNTSTCMI'
                if sku == 'NANOKONTROL2':
                    sku = 'KO-NANOKONTROL2CMI'
                if sku == 'NC-Q1WH':
                    sku = 'KO-NCQ1WHCMI'
                if sku == 'NTS-1':
                    sku = 'KO-NTS1CMI'
                if sku == 'ODS':
                    sku = 'KO-ODS1CMI'
                if sku == 'OPSIX':
                    sku = 'KO-OPSIXCMI'
                if sku == 'SQ-64':
                    sku = 'KO-SQ64CMI'
                if sku == 'B1ST-WH':
                    sku = 'KO-B1STWHCMI'
                if sku == 'TINYPIANO-PK':
                    sku = 'KO-TINYPIANOPKCMI'
                if sku == 'TINYPIANO-RD':
                    sku = 'KO-TINYPIANORDCMI'
                if sku == 'TINYPIANO-WH':
                    sku = 'KO-TINYPIANOWHCMI'
                if sku == 'VOLCABASS':
                    sku = 'KO-VOLCABASSCMI'
                if sku == 'VOLCABEATS':
                    sku = 'KO-VOLCABEATSCMI'
                if sku == 'VOLCADRUM':
                    sku = 'KO-VOLCADRUMCMI'
                if sku == 'VOLCAFM':
                    sku = 'KO-VOLCAFMCMI'
                if sku == 'VOLCAFM2':
                    sku = 'KO-VOLCAFM2CMI'
                if sku == 'VOLCAKEYS':
                    sku = 'KO-VOLCAKEYSCMI'
                if sku == 'VOLCAKICK':
                    sku = 'KO-VOLCAKICKCMI'
                if sku == 'VOLCAMIX':
                    sku = 'KO-VOLCAMIXCMI'
                if sku == 'VOLCAMODULAR':
                    sku = 'KO-VOLCAMODULARCMI'
                if sku == 'VOLCANUBASS':
                    sku = 'KO-VOLCANUBASSCMI'
                if sku == 'VOLCASAMPLE2':
                    sku = 'KO-VOLCASAMPLE2CMI'
                if sku == 'WAVESTATE':
                    sku = 'KO-WAVESTATECMI'
                if sku == 'XE20':
                    sku = 'KO-XE20CMI'
                if sku == 'MONOTRON-DUO':
                    sku = 'KO-MONOTRONDUOCMI'
                if sku == 'SCKROME61':
                    sku = 'KO-SCKROME61CMI'
                if sku == 'SCKROME73':
                    sku = 'KO-SCKROME73CMI'
                if sku == 'GM-12':
                    sku = 'KO-GM12CMI'
                if sku == 'GM-14':
                    sku = 'KO-GM14CMI'
                if sku == 'MONOTRON-DELAY':
                    sku = 'KO-MONOTRONDELAYCMI'
                if sku == 'NANOKEY2-WH':
                    sku = 'KO-NANOKEY2WHCMI'
                if sku == 'MICROKEY2-37':
                    sku = 'KO-MICKEY237CMI'
                if sku == 'MICROKEY2-61':
                    sku = 'KO-MICKEY261CMI'
                if sku == 'TINYPIANO':
                    sku = 'KO-TINYPIANOBKCMI'
                if sku == 'ARP2600MLTD':
                    sku = 'KO-ARP2600MLTDCMI'
                if sku == 'ELECTRIBE2-BL':
                    sku = 'KO-ELECTR2BLCMI'
                if sku == 'KA350':
                    sku = 'KO-KA350CMI'
                if sku == 'KONNECT':
                    sku = 'KO-KONNECTCMI'
                if sku == 'KR-55PRO':
                    sku = 'KO-KR55PROCMI'
                if sku == 'KROME88EX':
                    sku = 'KO-KROME88EXCMI'
                if sku == 'KROSS2-61':
                    sku = 'KO-KROSS261CMI'
                if sku == 'KROSS2-88':
                    sku = 'KO-KROSS288CMI'
                if sku == 'MICROKEY2-49':
                    sku = 'KO-MICKEY249CMI'
                if sku == 'MICROKEY2-AIR49':
                    sku = 'KO-MKEY249AIRCMI'
                if sku == 'MICROKEY2-AIR61':
                    sku = 'KO-MKEY261AIRCMI'
                if sku == 'KP2S':
                    sku = 'KO-KP2SCMI'
                if sku == 'MINILOGUESC':
                    sku = 'KO-MINILOGUESCCMI'
                if sku == 'MS20-MINI':
                    sku = 'KO-MS20CMI'
                if sku == 'MW-1608':
                    sku = 'KO-MW1608CMI'
                if sku == 'NANOPAD2-BK':
                    sku = 'KO-NANOPAD2BKCMI'
                if sku == 'NC-Q1BK':
                    sku = 'KO-NCQ1BKCMI'
                if sku == 'NTS-2PT':
                    sku = 'KO-NTS2BOOKCMI'
                if sku == 'PBAD':
                    sku = 'KO-PBCSBKCMI'
                if sku == 'PROLOGUE8':
                    sku = 'KO-PROLOGUE8CMI'
                if sku == 'PROLOGUE16':
                    sku = 'KO-PROLOGUE16CMI'
                if sku == 'GACSBK':
                    sku = 'KO-GACSBKCMI'
                if sku == 'GACSRD':
                    sku = 'KO-GACSRDCMI'
                if sku == 'GACSWH':
                    sku = 'KO-GACSWHCMI'
                if sku == 'GA1':
                    sku = 'KO-GA1CMI'
                if sku == 'CA2':
                    sku = 'KO-CA2CMI'
                if sku == 'CA50':
                    sku = 'KO-CA50CMI'
                if sku == 'KDM3':
                    sku = 'KO-KDM3BCMI'
                if sku == 'LMA120':
                    sku = 'KO-LMA120CMI'
                if sku == 'TM60BK':
                    sku = 'KO-TM60BKCMI'
                if sku == 'TM60CWH':
                    sku = 'KO-TM60CWHCMI'
                if sku == 'TM60WH':
                    sku = 'KO-TM60WHCMI'
                if sku == 'TMR50PW':
                    sku = 'KO-TMR50PWCMI'
                if sku == 'HA40':
                    sku = 'KO-HA40CMI'
                if sku == 'NUVIBE':
                    sku = 'KO-NUVIBECMI'
                if sku == 'HMBEATBK':
                    sku = 'KO-HMBEATBKCMI'
                if sku == 'HMBEATWH':
                    sku = 'KO-HMBEATWHCMI'
                if sku == 'MG1':
                    sku = 'KO-MG1CMI'
                if sku == 'GACSBL':
                    sku = 'KO-GACSBLCMI'
                if sku == 'DS1H':
                    sku = 'KO-DS1HCMI'
                if sku == 'MA2RD':
                    sku = 'KO-MA2RDCMI'
                if sku == 'PITCHCLIP2':
                    sku = 'KO-PITCHCLIP2CMI'
                if sku == 'PITCHCLIP2PL':
                    sku = 'KO-PITCHCLIP2PLCMI'
                if sku == 'RIMPITCHC2':
                    sku = 'KO-RIMPITCHC2CMI'
                if sku == 'TM60CBK':
                    sku = 'KO-TM60CBKCMI'
                if sku == 'PU2':
                    sku = 'KO-PU2CMI'
                if sku == 'KRMINI':
                    sku = 'KO-KRMINICMI'
                if sku == 'PBCSBK':
                    sku = 'KO-PBCSBKCMI'
                if sku == 'AW4GBK':
                    sku = 'KO-AW4GBKCMI'
                if sku == 'SHPRO':
                    sku = 'KO-SHPROCMI'
                if sku == 'SLM1CM':
                    sku = 'KO-SLM1CMCMI'
                if sku == 'SLM1CMPG':
                    sku = 'KO-SLM1CMPGCMI'
                if sku == 'SLM1CMPW':
                    sku = 'KO-SLM1CMPWCMI'
                if sku == 'PS3':
                    sku = 'KO-PS3CMI'
                if sku == 'PS1':
                    sku = 'KO-PS1CMI'
                if sku == 'OT120':
                    sku = 'KO-OT120CMI'

            try:

                stock = soup3.find(class_='stock in-stock').text

                if 'accepting' in stock.lower():
                    stock_avaliable = 'n'

                else:
                    stock_avaliable = 'y'

            except:
                stock_avaliable = 'n'

            today = datetime.now()

            date = today.strftime('%m %d %Y')

            image = 'Not Scraped'

            sheet.append([sku, brand, title, price, url2, image, description, date, stock_avaliable])
            print(f'Item {str(item_number)} scraped successfully')

            if int(items_scrapped) % 20 == 0:
                print(f'Saving Sheet... Please wait....')
                try:
                    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\DJ_City.xlsx")
                except:
                    print(f"Error occurred while saving the Excel file:")
try:
    wb.save(rf"\\SERVER\Python\Pricing\Pricing Spreadsheets\DJ_City.xlsx")
except:
    print(f"Error occurred while saving the Excel file:")