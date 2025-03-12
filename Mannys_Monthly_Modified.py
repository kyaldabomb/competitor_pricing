import requests
from bs4 import BeautifulSoup
import pprint, time, math, os, traceback
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import argparse
import openpyxl
from send2trash import send2trash

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run monthly scraper for Mannys')
parser.add_argument('scraper', nargs='?', default='mannys_monthly', 
                    help='Scraper name from config')
args = parser.parse_args()

# Email notification function
def send_email_notification(success, items_count=0, error_msg=""):
    print("Sending email notification...")
    try:
        # Email settings
        sender = "kyal@scarlettmusic.com.au"
        receiver = "kyal@scarlettmusic.com.au"
        password = os.environ.get('EMAIL_PASSWORD')
        if not password:
            print("Email password not found in environment variables")
            return
            
        host = "mail.scarlettmusic.com.au"
        port = 587
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        
        if success:
            msg['Subject'] = f"Mannys Monthly Scraper Success: {items_count} new items added"
            body = f"The Mannys monthly web scraper ran successfully and added {items_count} new items."
        else:
            msg['Subject'] = "Mannys Monthly Scraper Failed"
            body = f"The Mannys monthly web scraper encountered an error:\n\n{error_msg}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        print(traceback.format_exc())

# Setup Chrome options for headless operation in GitHub Actions
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

try:
    # Initialize WebDriver using webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Print Chrome and ChromeDriver version for debugging
    print(f"Chrome version: {driver.capabilities['browserVersion']}")
    print(f"ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]}")
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    # Use local path instead of network path
    file_path = "Pricing Spreadsheets/Mannys.xlsx"
    wb = openpyxl.load_workbook(file_path)
    sheet = wb['Sheet']
    
    url_list = []
    
    for x in range(2, sheet.max_row+1):
        url = sheet['E'+str(x)].value
        if url:
            url_list.append(url)
            
    print(f"Found {len(url_list)} existing URLs in the spreadsheet")
    
    item_number = 0
    items_scrapped = 0
    
    pre_url = 'https://www.mannys.com.au'
    url = 'https://www.mannys.com.au/brands'
    
    # Retry logic for brands page
    max_retries = 3
    for retry in range(max_retries):
        try:
            r = driver.get(url)
            # Add a longer wait time for the JavaScript to render the page
            time.sleep(5)
            break
        except Exception as e:
            if retry == max_retries - 1:
                raise
            print(f"Retry {retry+1}/{max_retries} for brands page: {str(e)}")
            time.sleep(5)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    brand_links = soup.find(class_='brand-list')
    
    if not brand_links:
        raise Exception("Could not find brand_links element on the page. Check if the page structure has changed.")
    
    # Process brands of interest
    for x in brand_links.find_all('li'):
        brand = x.text
        brand_url = x.find('a')['href']
        url = f'{pre_url}{brand_url}'
        
        # Filter for desired brands only
        if brand.lower() == 'orange' or brand.lower() == 'ernie ball' or brand.lower() == 'morely' or brand.lower() == 'blue microphones' or brand.lower() == 'soundbrenner' or brand.lower() == 'strandberg' or brand.lower() == 'korg' or brand.lower() == 'arturia' or 'tc electronic' in brand.lower() or brand.lower() == 'jbl' or brand.lower() == 'epiphone' or 'gibson' in brand.lower() or brand.lower() == 'dbx' or brand.lower() == "d'addario" or brand.lower() == "tech 21" or brand.lower() == "lr baggs" or brand.lower() == "universal audio" or brand.lower() == "soundcraft" or brand.lower() == "aguilar" or brand.lower() == "casio" or brand.lower() == "akg" or "seymour" in brand.lower() or "helicon" in brand.lower() or "kyser" in brand.lower() or "gruv" in brand.lower() or "akai" in brand.lower() or "marshall" in brand.lower() or "nord" in brand.lower() or "hercules" in brand.lower() or "headrush" in brand.lower() or "boss" in brand.lower() or "ashton" in brand.lower() or "ibanez" in brand.lower() or "evans" in brand.lower() or "tascam" in brand.lower() or "gator" in brand.lower() or "valencia" in brand.lower() or "xtreme" in brand.lower() or "cnb" in brand.lower() or "v-case" in brand.lower() or "mahalo" in brand.lower() or "dxp" in brand.lower() or "dunlop" in brand.lower() or "mano" in brand.lower() or "carson" in brand.lower() or "mxr" in brand.lower() or "armour" in brand.lower() or "dimarzio" in brand.lower() or 'auralex' in brand.lower() or 'alesis' in brand.lower() or 'digitech' in brand.lower() or 'crown' in brand.lower() or 'samson' in brand.lower() or 'x-vive' in brand.lower() or 'beale' in brand.lower() or 'snark' in brand.lower() or 'esp' in brand.lower() or 'ghs' in brand.lower() or 'strymon' in brand.lower() or 'rockboard' in brand.lower() or 'vic firth' in brand.lower() or 'ik multimedia' in brand.lower() or 'remo' in brand.lower() or 'darkglass' in brand.lower() or 'martin' in brand.lower() or 'm-audio' in brand.lower() or 'native instruments' in brand.lower() or 'source audio' in brand.lower() or 'emg' in brand.lower() or 'mapex' in brand.lower() or 'udg' in brand.lower() or 'alto' in brand.lower() or 'nektar' in brand.lower() or brand.lower() == 'se' or 'radial' in brand.lower() or 'teenage' in brand.lower() or 'tama' in brand.lower() or 'roland' in brand.lower() or 'hosa' in brand.lower() or 'oskar' in brand.lower() or 'hotone' in brand.lower() or 'vox' in brand.lower() or 'ampeg' in brand.lower() or 'singular' in brand.lower():
            try:
                print(f"Processing brand: {brand}")
                # Retry logic for brand page
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        r = driver.get(url)
                        time.sleep(5)  # Increased wait time
                        break
                    except Exception as e:
                        if retry == max_retries - 1:
                            raise
                        print(f"Retry {retry+1}/{max_retries} for {brand}: {str(e)}")
                        time.sleep(5)
                
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # Get number of products and pages
                try:
                    number_of_brand_products_total = soup.find(class_='products-found').text.split(' ')[0]
                    number_of_pages = math.ceil(float(number_of_brand_products_total)/20)
                    print(f"Found {number_of_brand_products_total} products across {number_of_pages} pages")
                except Exception as e:
                    print(f"Could not determine product count for {brand}: {str(e)}")
                    continue
                    
                # Click "Load More" button to get all products
                for _ in range(int(number_of_pages)+30):  # Adding buffer for safety
                    try:
                        element = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div/div/section/div[2]/div[2]/div/div/button")
                        
                        actions = ActionChains(driver)
                        actions.move_to_element(element).perform()
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", element)
                        
                    except Exception as e:
                        # Silently continue if button not found (likely reached the end)
                        time.sleep(1)
                        
                    time.sleep(1)  # Wait after each click attempt
                
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                all_products = soup.find(class_='products-container')
                
                if not all_products:
                    print(f"No products container found for {brand}")
                    continue
                
                # Process all products
                for t in all_products.find_all(class_='product-card'):
                    item_number += 1
                    
                    try:
                        # Extract URL and check if already in spreadsheet
                        product_url = t.find('a')['href']
                        url = f'{pre_url}{product_url}'
                        
                        if url in url_list:
                            print(f'Item {str(item_number)} already in sheet, skipping')
                            continue
                        
                        items_scrapped += 1
                        
                        # Get basic product info from listing page
                        sku = t.find(class_='sku').text if t.find(class_='sku') else "N/A"
                        if not sku or sku == "N/A":
                            print(f"No SKU found for item {item_number}, skipping")
                            continue
                            
                        # Apply brand-specific SKU modifications
                        if 'OBX' in sku:
                            continue
                        if brand.lower() == 'arturia':
                            sku = sku.replace('ART-', 'AR-')
                            sku = f'{sku}CMI'
            
                        if 'hosa' in brand.lower():
                            sku = sku.replace('HOS-', '')
            
                        if 'singular' in brand.lower():
                            if sku == 'SIN-BEABBMINI2':
                                sku = 'BEA-BBMINI2'
                            if sku == 'SIN-BEABB':
                                sku = 'BEA-BB'
                            if sku == 'SIN-AEROS':
                                sku = 'BEA-AEROS'
                            if sku == 'SIN-BEAMIDISYNC':
                                sku = 'BEA-MIDISYNC'
                            if sku == 'SIN-BEABBFS':
                                sku = 'BEA-BBFS'
                            if sku == 'SIN-MIDIMAESTRO':
                                sku = 'BEA-MIDIMAESTRO'
            
            
                        if 'ampeg' in brand.lower():
                            if sku == 'AMP-RB110':
                                sku = 'AAF6307'
                            if sku == 'AMP-SVT410HLF':
                                sku = 'AAF4469'
                            if sku == 'AMP-PF500':
                                sku = 'AAF4549'
                            if sku == 'AMP-RB210':
                                sku = 'AAF6325'
                            if sku == 'AMP-PF210HE':
                                sku = 'AAF4536'
                            if sku == 'AMP-CLASSIC':
                                sku = 'AAF4609'
                            if sku == 'AMP-RB108':
                                sku = 'AAF6301'
                            if sku == 'AMP-PF115HE':
                                sku = 'AAF4523'
                            if sku == 'AMP-MICROVRH':
                                sku = 'AAF4631'
                            if sku == 'AMP-MICROCLSTK':
                                sku = 'AAF4630'
                            if sku == 'AMP-SCRDI':
                                sku = 'AAF4512'
                            if sku == 'AMP-SVT210AV':
                                sku = 'AAF4463'
                            if sku == 'AMP-RB112':
                                sku = 'RB-112'
                            if sku == 'AMP-OPTOCOMP':
                                sku = 'AAF4612'
                            if sku == 'AMP-SCRAMBLER':
                                sku = 'AAF4614'
                            if sku == 'AMP-RB115':
                                sku = 'AAF6319'
                            if sku == 'AMP-SVT7PRO':
                                sku = 'SVT-7PRO'
                            if sku == 'AMP-SVT410HE':
                                sku = 'AAF4467'
                            if sku == 'AMP-LIQUIFIER':
                                sku = 'AAF4610'
                            if sku == 'AMP-SVT810E':
                                sku = 'AAF4475'
                            if sku == 'AMP-SVT212AV':
                                sku = 'AAF4465'
                            if sku == 'AMP-SGTDI':
                                sku = 'AAF6639'
                            if sku == 'AMP-V4B':
                                sku = 'AAF4498'
                            if sku == 'AMP-PF410HLF':
                                sku = 'AAF4546'
                            if sku == 'AMP-SVT15E':
                                sku = 'AAF4461'
                            if sku == 'AMP-SVT4PRO':
                                sku = 'AAF4633'
                            if sku == 'AMP-PF350':
                                sku = 'AAF4539'
                            if sku == 'AMP-PF20T':
                                sku = 'AAF4532'
                            if sku == 'AMP-PF50T':
                                sku = 'AAF4561'
                            if sku == 'AMP-HSVTCL':
                                sku = 'AAF4629'
                            if sku == 'AMP-SVTCL':
                                sku = 'AAF4481'
                            if sku == 'AMP-HSVT410HLF':
                                sku = 'AAF4516'
                            if sku == 'AMP-PN410HLF':
                                sku = 'AAF4574'
                            if sku == 'AMP-SVT610HLF':
                                sku = 'AAF4471'
                            if sku == 'AMP-SVT3PRO':
                                sku = 'AAF4634'
                            if sku == 'AMP-SVT810AV':
                                sku = 'AAF4473'
                            if sku == 'AMP-SVT112AV':
                                sku = 'AAF4459'
                            if sku == 'AMP-PF115LF':
                                sku = 'AAF4525'
                            if sku == 'AMP-PF112HLF':
                                sku = 'PF-112HLF'
                            if sku == 'AMP-PN210HLF':
                                sku = 'AAF4573'
                            if sku == 'AMP-HSVT810E':
                                sku = 'AAF4517'
                            if sku == 'AMP-AFP1':
                                sku = 'AFP1'
                            if sku == 'AMP-SVT410HLFCV':
                                sku = 'AAF4599'
                            if sku == 'AMP-SVT210AVCVR':
                                sku = 'AAF4463'
                            if sku == 'AMP-SVTCLCVR':
                                sku = 'AAF4602'
                            if sku == 'AMP-SVT610HLFCV':
                                sku = 'AAF4600'
                            if sku == 'AMP-SVT15ECVR':
                                sku = 'AAF4595'
                            if sku == 'AMP-SVT410HECVR':
                                sku = 'AAF4598'
                            if sku == 'AMP-SVT810CVR':
                                sku = 'AAF4601'
                            if sku == 'AMP-SVT212AVCVR':
                                sku = 'AAF4597'
                            if sku == 'AMP-AFP3':
                                sku = 'AAF4515'
                            if sku == 'AMP-PF500800BAG':
                                sku = 'AAF4608'
            
            
                        if 'vox' in brand.lower():
                            if sku == 'VOX-AP2AC':
                                sku = 'VOX-AP2-AC'
                            if sku == 'VOX-PATHF10':
                                sku = 'VOX-PFINDER10'
                            if sku == 'VOX-AC10':
                                sku = 'VOX-AC10C1'
                            if sku == 'VOX-AP2BS':
                                sku = 'VOX-AP2-BS'
                            if sku == 'VOX-PATHF10B':
                                sku = 'VOX-PFINDERB10'
                            if sku == 'VOX-AC4C112':
                                sku = 'VOX-AC4C1-12'
                            if sku == 'VOX-AC4C1BL':
                                sku = 'VOX-AC4C1-BL'
                            if sku == 'VOX-VX15GT':
                                sku = 'VOX-VX15-GT'
                            if sku == 'VOX-VX50GTV':
                                sku = 'VOX-VX50-GTV'
                            if sku == 'VOX-VMG3':
                                sku = 'VOX-VMG-3'
                            if sku == 'VOX-AP2CR':
                                sku = 'VOX-AP2-CR'
                            if sku == 'VOX-AP2MT':
                                sku = 'VOX-AP2-MT'
                            if sku == 'VOX-VX50AG':
                                sku = 'VOX-VX50-AG'
                            if sku == 'VOX-VX50BA':
                                sku = 'VOX-VX50-BA'
                            if sku == 'VOX-AP2CAB':
                                sku = 'VOX-AP2-CAB'
                            if sku == 'VOX-APBMSESET':
                                sku = 'VOX-AP-BM-SET'
                            if sku == 'VOX-VMG50':
                                sku = 'VOX-VMG-50'
                            if sku == 'VOX-APBM':
                                sku = 'VOX-AP-BM'
                            if sku == 'VOX-V846HW':
                                sku = 'VOX-V846-HW'
                            if sku == 'VOX-MV50BM':
                                sku = 'VOX-MV50-BM'
                            if sku == 'VOX-VT100X':
                                sku = 'VOX-VT100X'
                            if sku == 'VOX-STOMPG2':
                                sku = 'VOX-SL2G'
                            if sku == 'VOX-VMG10':
                                sku = 'VOX-VMG-10'
                            if sku == 'VOX-SDC1BL':
                                sku = 'VOX-SDC-1MBK'
                            if sku == 'VOX-VFS2':
                                sku = 'VOX-VFS-2'
                            if sku == 'VOX-MK3MINIMB':
                                sku = 'VOX-MINIMB'
                            if sku == 'VOX-VHQ1BK':
                                sku = 'VOX-VH-Q1BK'
                            if sku == 'VOX-MV50BMSESET':
                                sku = 'VOX-MV50-BMSET'
                            if sku == 'VOX-STOMPGI':
                                sku = 'VOX-SL1G'
                            if sku == 'VOX-MSB50BA':
                                sku = 'VOX-MSB50BASS'
                            if sku == 'VOX-SDC1WH':
                                sku = 'VOX-SDC-1MWH'
                            if sku == 'VOX-MV50ACSET':
                                sku = 'VOX-MV50-ACSET'
                            if sku == 'VOX-VEME':
                                sku = 'VOX-VE-ME'
                            if sku == 'VOX-MV50CLSET':
                                sku = 'VOX-MV50-CLSET'
                            if sku == 'VOX-VECE':
                                sku = 'VOX-VE-CE'
                            if sku == 'VOX-STOMPB2':
                                sku = 'VOX-SL2B'
                            if sku == 'VOX-VHQ1WH':
                                sku = 'VOX-VH-Q1WH'
                            if sku == 'VOX-SDC1RD':
                                sku = 'VOX-SDC-1MRD'
                            if sku == 'VOX-STOMPBI':
                                sku = 'VOX-SL1B'
                            if sku == 'VOX-VAC19BR':
                                sku = 'VOX-VAC19-6M'
                            if sku == 'VOX-VGC19BK':
                                sku = 'VOX-VGC19-6M'
                            if sku == 'VOX-VBC19BL':
                                sku = 'VOX-VBC19-6M'
                            if sku == 'VOX-AP2CL':
                                sku = 'VOX-AP2-CL'
                            if sku == 'VOX-AP2BL':
                                sku = 'VOX-AP2-BL'
                            if sku == 'VOX-MV50CR':
                                sku = 'VOX-MV50-CR'
                            if sku == 'VOX-AP2LD':
                                sku = 'VOX-AP2-LD'
                            if sku == 'VOX-MV50BQ':
                                sku = 'VOX-MV50-BQ'
                            if sku == 'VOX-MV50HG':
                                sku = 'VOX-MV50-HG'
                            if sku == 'VOX-VGHAC30':
                                sku = 'VOX-VGH-AC30'
                            if sku == 'VOX-MV50AC':
                                sku = 'VOX-MV50-AC'
                            if sku == 'VOX-VGHROCK':
                                sku = 'VOX-VGH-ROCK'
                            if sku == 'VOX-VESD':
                                sku = 'VOX-VE-SD'
                            if sku == 'VOX-MV50CL':
                                sku = 'VOX-MV50-CL'
                            if sku == 'VOX-ADIOAIRGT':
                                sku = 'VOX-ADIO-AIR-GT'
                            if sku == 'VOX-VGHBASS':
                                sku = 'VOX-VGH-BASS'
                            if sku == 'VOX-VFS3':
                                sku = 'VOX-VFS3'
                            if sku == 'VOX-ADIOAIRBS':
                                sku = 'VOX-ADIO-AIR-BS'
                            if sku == 'VOX-VECD':
                                sku = 'VOX-VE-CD'
                            if sku == 'VOX-VCC090WH':
                                sku = 'VOX-VCC-90WH'
                            if sku == 'VOX-VX50KB':
                                sku = 'VOX-VX50-KB'
                            if sku == 'VOX-VCC090SL':
                                sku = 'VOX-VCC-90SL'
                            if sku == 'VOX-VCC090RD':
                                sku = 'VOX-VCC-90RD'
                            if sku == 'VOX-VCC090BK':
                                sku = 'VOX-VCC-90BK'
                            if sku == 'VOX-VCC090BL':
                                sku = 'VOX-VCC-90BL'
                            if sku == 'VOX-VXT1':
                                sku = 'VOX-VXT-1'
                            if sku == 'VOX-VGS050':
                                sku = 'VOX-VGS-50'
                            if sku == 'VOX-VGS030':
                                sku = 'VOX-VGS-30'
                            sku = f'{sku}CMI'
            
            
            
            
            
                        if 'hotone' in brand.lower():
                            if sku == 'HOT-AMPEROII':
                                sku = 'HT-AMPERO-II'
                            if sku == 'HOT-SOULPR':
                                sku = 'HT-SOUL-PRESS-II'
                            if sku == 'HOT-AMPEROONE':
                                sku = 'HT-AMPERO-ONE'
                            if sku == 'HOT-AMPERO':
                                sku = 'HT-AMPERO'
                            if sku == 'HOT-AMPEROCNTRL':
                                sku = 'HT-AMPERO-CONTRL'
                            if sku == 'HOT-AMPEROSWITCH':
                                sku = 'HT-AMPERO-SW'
                            if sku == 'HOT-AMPEROPR':
                                sku = 'HT-AMPERO-PRESS'
                            if sku == 'HOT-AMPEROIIRED':
                                sku = 'HT-AMPERO-II-RED'
                            if sku == 'HOT-MOJODIAMOND':
                                sku = 'HT-MOJO-DIAMOND'
                            if sku == 'HOT-PURPLEWIND':
                                sku = 'HT-PURPLE-WIND'
                            if sku == 'HOT-HEARTATTACK':
                                sku = 'HT-HEARTATTACK'
                            if sku == 'HOT-BRITWIND':
                                sku = 'HT-BRITWIND'
                            if sku == 'HOT-THUNDERBASS':
                                sku = 'HT-THUNDERBASS'
                            if sku == 'HOT-BRITISH':
                                sku = 'HT-BRIT-INVASION'
                            if sku == 'HOT-SOULPRESS':
                                sku = 'HT-SOULPRESS'
                            if sku == 'HOT-AMPEROGIGBAG':
                                sku = 'HT-AGB-1'
                            if sku == 'HOT-MOJOATTACK':
                                sku = 'HT-MOJO-ATTACK'
            
            
            
                        if 'oskar' in brand.lower():
                            if sku == 'LO-1910C':
                                sku = 'LO1910-C'
                            if sku == 'LO-1910G':
                                sku = 'LO1910-G'
                            if sku == 'LO-10HH':
                                sku = 'LO10HH'
                            if sku == 'LO-1910A':
                                sku = 'LO1910-A'
                            if sku == 'LO-1910D':
                                sku = 'LO1910-D'
                            if sku == 'LO-1910NA':
                                sku = 'LO1910N-A'
                            if sku == 'LO-1910BFLAT':
                                sku = 'LO1910-BFLAT'
                            if sku == 'LO-1910F':
                                sku = 'LO1910-F'
                            if sku == 'LO-1910E':
                                sku = 'LO1910-E'
                            if sku == 'LO-1910AFLAT':
                                sku = 'LO1910-AFLAT'
                            if sku == 'LO-1910LF':
                                sku = 'LO1910L-F'
                            if sku == 'LO-1910HA':
                                sku = 'LO1910H-A'
                            if sku == 'LO-1910RPC':
                                sku = 'LO1910RP-C'
                            if sku == 'LO-1910B':
                                sku = 'LO1910-B'
                            if sku == 'LO-1910RPG':
                                sku = 'LO1910RP-G'
                            if sku == 'LO-1910EFLAT':
                                sku = 'LO1910-EFLAT'
                            if sku == 'LO-1910RPA':
                                sku = 'LO1910RP-A'
                            if sku == 'LO-LO1910NC':
                                sku = 'LO1910N-C'
                            if sku == 'LO-LO1910ND':
                                sku = 'LO1910N-D'
                            if sku == 'LO-LO1910NG':
                                sku = 'LO1910N-G'
                            if sku == 'LO-1910LD':
                                sku = 'LO1910-LD'
                            if sku == 'LO-LO1910NB':
                                sku = 'LO1910N-B'
                            if sku == 'LO-LO1910HC':
                                sku = 'LO1910H-C'
                            if sku == 'LO-LO1910NE':
                                sku = 'LO1910N-E'
                            if sku == 'LO-LO1910NF':
                                sku = 'LO1910N-F'
            
            
            
                        if 'roland' in brand.lower():
            
                            if sku == 'ROL-FP30XBK':
                                sku = 'FP30XBK'
                            if sku == 'ROL-SP404MK2':
                                sku = 'SP404MK2'
                            if sku == 'ROL-FP10BK':
                                sku = 'FP10BK'
                            if sku == 'ROL-TR8S':
                                sku = 'TR8S'
                            if sku == 'ROL-RD88':
                                sku = 'RD88'
                            if sku == 'ROL-TD07DMK':
                                sku = 'TD07DMK'
                            if sku == 'ROL-CUBESTEXBL':
                                sku = 'CUBESTEX'
                            if sku == 'ROL-JUNODS88':
                                sku = 'JUNODS88'
                            if sku == 'ROL-TD07KV':
                                sku = 'TD07KV'
                            if sku == 'ROL-RD2000':
                                sku = 'RD2000'
                            if sku == 'ROL-FANTOM08':
                                sku = 'FANTOM08'
                            if sku == 'ROL-JUNOX':
                                sku = 'JUNOX'
                            if sku == 'ROL-FPE50BK':
                                sku = 'FPE50BK'
                            if sku == 'ROL-GOKEYS61K':
                                sku = 'GO61K'
                            if sku == 'ROL-FP60XBK':
                                sku = 'FP60XBK'
                            if sku == 'ROL-FP90XBK':
                                sku = 'FP90XBK'
                            if sku == 'ROL-T8':
                                sku = 'T8'
                            if sku == 'ROL-FANTOM06':
                                sku = 'FANTOM06'
                            if sku == 'ROL-TD02KV':
                                sku = 'TD02KV'
                            if sku == 'ROL-RPB100BK':
                                sku = 'RPB100BK'
                            if sku == 'ROL-TD02K':
                                sku = 'TD02K'
                            if sku == 'ROL-JU06A':
                                sku = 'JU06A'
                            if sku == 'ROL-PM100':
                                sku = 'PM100'
                            if sku == 'ROL-FP30XWH':
                                sku = 'FP30XWH'
                            if sku == 'ROL-RDT10':
                                sku = 'RDT10'
                            if sku == 'ROL-MC707':
                                sku = 'MC707'
                            if sku == 'ROL-J6':
                                sku = 'J6'
                            if sku == 'ROL-RKP50D':
                                sku = 'RKP50D'
                            if sku == 'ROL-VT4':
                                sku = 'VT4'
                            if sku == 'ROL-JUPITERX':
                                sku = 'JUPITERX'
                            if sku == 'ROL-TR6S':
                                sku = 'TR6S'
                            if sku == 'ROL-JC40':
                                sku = 'JC40'
                            if sku == 'ROL-SPDSX':
                                sku = 'SPDSX'
                            if sku == 'ROL-UMONEMK2':
                                sku = 'UMONEMK2'
                            if sku == 'ROL-RDT50':
                                sku = 'RDT50'
                            if sku == 'ROL-DP10':
                                sku = 'DP10'
                            if sku == 'ROL-RKP50':
                                sku = 'RKP50'
                            if sku == 'ROL-E4':
                                sku = 'E4'
                            if sku == 'ROL-PM200':
                                sku = 'PM200'
                            if sku == 'ROL-GOMIXERPROX':
                                sku = 'GOMIXERPX'
                            if sku == 'ROL-MDSCOM':
                                sku = 'MDSCOM'
                            if sku == 'ROL-MC101':
                                sku = 'MC101'
                            if sku == 'ROL-TR08':
                                sku = 'TR08'
                            if sku == 'ROL-KSCFP10BK':
                                sku = 'KSCFP10BK'
                            if sku == 'ROL-JUNODS61':
                                sku = 'JUNODS61'
                            if sku == 'ROL-KSC70BK':
                                sku = 'KSC70BK'
                            if sku == 'ROL-KC200':
                                sku = 'KC200'
                            if sku == 'ROL-F107BK':
                                sku = 'F107BK'
                            if sku == 'ROL-MBCUBE':
                                sku = 'MB-CUBE'
                            if sku == 'ROL-JX08':
                                sku = 'JX08'
                            if sku == 'ROL-SPD30BK':
                                sku = 'SPD30BK'
                            if sku == 'ROL-RKP10D':
                                sku = 'RKP10D'
                            if sku == 'ROL-JDXI':
                                sku = 'JDXI'
                            if sku == 'ROL-JD08':
                                sku = 'JD08'
                            if sku == 'ROL-RKP10':
                                sku = 'RKP10'
                            if sku == 'ROL-KPD70BK':
                                sku = 'KPD70BK'
                            if sku == 'ROL-RSS50':
                                sku = 'RSS50'
                            if sku == 'ROL-RH5':
                                sku = 'RH5'
                            if sku == 'ROL-K25M':
                                sku = 'K25M'
                            if sku == 'ROL-RHH50':
                                sku = 'RHH50'
                            if sku == 'ROL-KD200MS':
                                sku = 'KD200MS'
                            if sku == 'ROL-PDS20':
                                sku = 'PDS20'
                            if sku == 'ROL-FANTOM8':
                                sku = 'FANTOM8'
                            if sku == 'ROL-TB03':
                                sku = 'TB03'
                            if sku == 'ROL-RP701LA':
                                sku = 'RP701LA'
                            if sku == 'ROL-RP701CB':
                                sku = 'RP701CB'
                            if sku == 'ROL-CBGO61KP':
                                sku = 'CBGO61KP'
                            if sku == 'ROL-KC80':
                                sku = 'KC80'
                            if sku == 'ROL-GOPIANO88':
                                sku = 'GO88P'
                            if sku == 'ROL-RP107BK':
                                sku = 'RP107BK'
                            if sku == 'ROL-SE02':
                                sku = 'SE02'
                            if sku == 'ROL-SH01A':
                                sku = 'SH01A'
                            if sku == 'ROL-VR09B':
                                sku = 'VR09B'
                            if sku == 'ROL-EC10':
                                sku = 'EC10'
                            if sku == 'ROL-A88MK2':
                                sku = 'A88MK2'
                            if sku == 'ROL-JUPITERXM':
                                sku = 'JUPITERXM'
                            if sku == 'ROL-KD140BC':
                                sku = 'KD140BC'
                            if sku == 'ROL-KT10':
                                sku = 'KT10'
                            if sku == 'ROL-GOPIANO61P':
                                sku = 'GO61P'
                            if sku == 'ROL-MDSSTD2':
                                sku = 'MDSSTD2'
                            if sku == 'ROL-F701LA':
                                sku = 'F701LA'
                            if sku == 'ROL-JC22':
                                sku = 'JC22'
                            if sku == 'ROL-AC33':
                                sku = 'AC33'
                            if sku == 'ROL-KC220':
                                sku = 'KC220'
                            if sku == 'ROL-KC400':
                                sku = 'KC400'
                            if sku == 'ROL-EV5':
                                sku = 'EV5'
                            if sku == 'ROL-TR06':
                                sku = 'TR06'
                            if sku == 'ROL-VH14D':
                                sku = 'VH14D'
                            if sku == 'ROL-A49BK':
                                sku = 'A49BK'
                            if sku == 'ROL-CBB61':
                                sku = 'CBB61'
                            if sku == 'ROL-DJ707M':
                                sku = 'DJ707M'
                            if sku == 'ROL-EV30':
                                sku = 'EV30'
                            if sku == 'ROL-RHH10':
                                sku = 'RHH10'
                            if sku == 'ROL-GR55GKBK':
                                sku = 'GR55GKBK'
                            if sku == 'ROL-SPD1P':
                                sku = 'SPD1P'
                            if sku == 'ROL-F701CB':
                                sku = 'F701CB'
                            if sku == 'ROL-KC600':
                                sku = 'KC600'
                            if sku == 'ROL-DAP2X':
                                sku = 'DAP2X'
                            if sku == 'ROL-TDM10':
                                sku = 'TDM10'
                            if sku == 'ROL-CBCS2':
                                sku = 'CBCS2'
                            if sku == 'ROL-DTS30S':
                                sku = 'DTS30S'
                            if sku == 'ROL-SPD1W':
                                sku = 'SPD1W'
                            if sku == 'ROL-TDM20':
                                sku = 'TDM20'
                            if sku == 'ROL-CS10EM':
                                sku = 'CS10EM'
                            if sku == 'ROL-MDSGND2':
                                sku = 'MDSGND2'
                            if sku == 'ROL-KD222GN':
                                sku = 'KD222GN'
                            if sku == 'ROL-CBRU10':
                                sku = 'CBRU10'
                            if sku == 'ROL-RPB100WH':
                                sku = 'RPB100WH'
                            if sku == 'ROL-BTYNIMH':
                                sku = 'BTYNIMH'
                            if sku == 'ROL-RPU3':
                                sku = 'RPU3'
                            if sku == 'ROL-RUBIX22':
                                sku = 'RUBIX22'
                            if sku == 'ROL-FP60XWH':
                                sku = 'FP60XWH'
                            if sku == 'ROL-APC33':
                                sku = 'APC33'
                            if sku == 'ROL-BT1':
                                sku = 'BT1'
                            if sku == 'ROL-GK3':
                                sku = 'GK3'
                            if sku == 'ROL-EX50':
                                sku = 'EX50'
                            if sku == 'ROL-DP2':
                                sku = 'DP2'
                            if sku == 'ROL-KSFE50BK':
                                sku = 'KSFE50BK'
                            if sku == 'ROL-SPD1E':
                                sku = 'SPD1E'
                            if sku == 'ROL-KSC72BK':
                                sku = 'KSC72BK'
                            if sku == 'ROL-RT30HR':
                                sku = 'RT30HR'
                            if sku == 'ROL-WC1':
                                sku = 'WC1'
                            if sku == 'ROL-GAIASH01':
                                sku = 'SH01'
                            if sku == 'ROL-CBB76':
                                sku = 'CBB76'
                            if sku == 'ROL-WM1':
                                sku = 'WM1'
                            if sku == 'ROL-CBBOCT':
                                sku = 'CBBOCT'
                            if sku == 'ROL-RSB1':
                                sku = 'RSB1'
                            if sku == 'ROL-RMIDIG5A':
                                sku = 'RMIDIG5A'
                            if sku == 'ROL-CY14CT':
                                sku = 'CY14CT'
                            if sku == 'ROL-RMIDIG3':
                                sku = 'RMIDIG3'
                            if sku == 'ROL-RUBIX44':
                                sku = 'RUBIX44'
                            if sku == 'ROL-NE10':
                                sku = 'NE10'
                            if sku == 'ROL-CUBESTBAG':
                                sku = 'CBCS1'
                            if sku == 'ROL-RUBIX24':
                                sku = 'RUBIX24'
                            if sku == 'ROL-UVC02':
                                sku = 'UVC02'
                            if sku == 'ROL-DK01':
                                sku = 'DK01'
                            if sku == 'ROL-APC10':
                                sku = 'APC10'
                            if sku == 'ROL-RSJ1':
                                sku = 'RSJ1'
                            if sku == 'ROL-TDM3':
                                sku = 'TDM3'
                            if sku == 'ROL-KPD90WH':
                                sku = 'KPD90WH'
                            if sku == 'ROL-GOLIVECAST':
                                sku = 'GOLIVECAST'
                            if sku == 'ROL-PSB240A':
                                sku = 'PSB240A'
                            if sku == 'ROL-SSPC1':
                                sku = 'SSPC1'
                            if sku == 'ROL-PK-TD27KV2S':
                                sku = 'TD27KV2S'
                            if sku == 'ROL-PK-FP30XBKS':
                                sku = 'FP30XBKS'
                            if sku == 'ROL-PK-VAD706GES':
                                sku = 'VAD706GES'
                            if sku == 'ROL-PK-TD17KVX2S':
                                sku = 'TD17KVX2S'
                            if sku == 'ROL-PK-TD50K2S':
                                sku = 'TD50K2S'
                            if sku == 'ROL-PK-TD17KV2S':
                                sku = 'TD17KV2S'
                            if sku == 'ROL-PK-VAD503S':
                                sku = 'VAD503S'
                            if sku == 'ROL-PK-VAD706GNS':
                                sku = 'VAD706GNS'
                            if sku == 'ROL-PK-TD02KDAP':
                                sku = 'TD02KDAP'
                            if sku == 'ROL-PK-FPE50BKS':
                                sku = 'FPE50BKS'
                            if sku == 'ROL-PK-TD02KVDAP':
                                sku = 'TD02KVDAP'
                            if sku == 'ROL-F701WH':
                                sku = 'F701WH'
                            if sku == 'ROL-RP701WH':
                                sku = 'RP701WH'
                            if sku == 'ROL-TD50X':
                                sku = 'TD50X'
                            if sku == 'ROL-CUBESTEXBTY':
                                sku = 'CUBESTEXBTY'
                            if sku == 'ROL-SPDSXSE':
                                sku = 'SPDSXSE'
                            if sku == 'ROL-TAIKO1':
                                sku = 'TAIKO1'
                            if sku == 'ROL-FANTOM07':
                                sku = 'FANTOM07'
                            if sku == 'ROL-SCG88W3':
                                sku = 'SCG88W3'
                            if sku == 'ROL-MV1':
                                sku = 'MV1'
                            if sku == 'ROL-RPB400BK':
                                sku = 'RPB400BK'
                            if sku == 'ROL-PK-FP60XBKS':
                                sku = 'FP60XBKS'
                            if sku == 'ROL-FANTOM7':
                                sku = 'FANTOM7'
                            if sku == 'ROL-SYSTEM8':
                                sku = 'SYSTEM8'
                            if sku == 'ROL-KPD90BK':
                                sku = 'KPD90BK'
                            if sku == 'ROL-RPB400PE':
                                sku = 'RPB400PE'
                            if sku == 'ROL-PDA120MS':
                                sku = 'PDA120MS'
                            if sku == 'ROL-INTEGRA7':
                                sku = 'INTEGRA7'
                            if sku == 'ROL-KC990':
                                sku = 'KC990'
                            if sku == 'ROL-KSC90BK':
                                sku = 'KSC90BK'
                            if sku == 'ROL-MDYSTD':
                                sku = 'MDYSTD'
                            if sku == 'ROL-SCG61W3':
                                sku = 'SCG61W3'
                            if sku == 'ROL-PK-TD50KV2S':
                                sku = 'TD50KV2S'
                            if sku == 'ROL-AXEDGEBK':
                                sku = 'AXEDGEBK'
                            if sku == 'ROL-PCS10TRA':
                                sku = 'PCS10TRA'
                            if sku == 'ROL-SPD20PRO':
                                sku = 'SPD20PRO'
                            if sku == 'ROL-PDA120GN':
                                sku = 'PDA120GN'
                            if sku == 'ROL-DAP3X':
                                sku = 'DAP3X'
                            if sku == 'ROL-PDA100GN':
                                sku = 'PDA100GN'
                            if sku == 'ROL-RP701DR':
                                sku = 'RP701DR'
                            if sku == 'ROL-PD140DS':
                                sku = 'PD140DS'
                            if sku == 'ROL-KD222GE':
                                sku = 'KD222GE'
                            if sku == 'ROL-CY16RT':
                                sku = 'CY16RT'
                            if sku == 'ROL-JC120':
                                sku = 'JC120'
                            if sku == 'ROL-RH200':
                                sku = 'RH200'
                            if sku == 'ROL-CY5':
                                sku = 'CY5'
                            if sku == 'ROL-STAX2':
                                sku = 'STAX2'
                            if sku == 'ROL-PDA140FMS':
                                sku = 'PDA140FMS'
                            if sku == 'ROL-RT30K':
                                sku = 'RT30K'
                            if sku == 'ROL-KSC70WH':
                                sku = 'KSC70WH'
                            if sku == 'ROL-RMIDIG10':
                                sku = 'RMIDIG10'
                            if sku == 'ROL-RPB400RW':
                                sku = 'RPB400RW'
                            if sku == 'ROL-STA95':
                                sku = 'STA95'
                            if sku == 'ROL-CY13RBK':
                                sku = 'CY13RBK'
                            if sku == 'ROL-PDA140FGE':
                                sku = 'PDA140FGE'
                            if sku == 'ROL-DCS10':
                                sku = 'DCS10'
                            if sku == 'ROL-BNC05':
                                sku = 'BNC05'
                            if sku == 'ROL-SCG76W3':
                                sku = 'SCG76W3'
                            if sku == 'ROL-RSH1':
                                sku = 'RSH1'
                            if sku == 'ROL-CBRAC':
                                sku = 'CBRAC'
                            if sku == 'ROL-BAGFR3':
                                sku = 'BAGFR3'
                            if sku == 'ROL-CBHPD':
                                sku = 'CBHPD'
                            if sku == 'ROL-KPD70WH':
                                sku = 'KPD70WH'
                            if sku == 'ROL-DBS30':
                                sku = 'DBS30'
                            if sku == 'ROL-FD8':
                                sku = 'FD8'
                            if sku == 'ROL-CBTDP':
                                sku = 'CBTDP'
                            if sku == 'ROL-CBBSPDSX':
                                sku = 'CBBSPDSX'
                            if sku == 'ROL-GKC5':
                                sku = 'GKC5'
                            if sku == 'ROL-NE1':
                                sku = 'NE1'
                            if sku == 'ROL-PK-FP30XWHS':
                                sku = 'FP30XWHS'
                            if sku == 'ROL-RACKC200':
                                sku = 'RACKC200'
                            if sku == 'ROL-AC33RW':
                                sku = 'AC33RW'
                            if sku == 'ROL-VRC01':
                                sku = 'VRC01'
                            if sku == 'ROL-MH216':
                                sku = 'MH216'
                            if sku == 'ROL-MOBILEAC':
                                sku = 'MOBILE-AC'
                            if sku == 'ROL-RT30H':
                                sku = 'RT30H'
                            if sku == 'ROL-MDHSTD':
                                sku = 'MDHSTD'
                            if sku == 'ROL-TM2':
                                sku = 'TM2'
                            if sku == 'ROL-CY8':
                                sku = 'CY8'
                            if sku == 'ROL-PDX12':
                                sku = 'PDX12'
                            if sku == 'ROL-MDSSTG2':
                                sku = 'MDSSTG2'
                            if sku == 'ROL-PCS15TRA':
                                sku = 'PCS15TRA'
                            if sku == 'ROL-GKKITGT3':
                                sku = 'GKKITGT3'
                            if sku == 'ROL-GK3B':
                                sku = 'GK3B'
                            if sku == 'ROL-GKC10':
                                sku = 'GKC10'
                            if sku == 'ROL-KSC72WH':
                                sku = 'KSC72WH'
                            if sku == 'ROL-PDX6':
                                sku = 'PDX6'
                            if sku == 'ROL-V02HDMK2':
                                sku = 'V02HDMK2'
                            if sku == 'ROL-MH210':
                                sku = 'MH210'
                            if sku == 'ROL-EC10M':
                                sku = 'EC10M'
                            if sku == 'ROL-KD180':
                                sku = 'KD180'
                            if sku == 'ROL-KD7':
                                sku = 'KD7'
                            if sku == 'ROL-MH214':
                                sku = 'MH214'
                            if sku == 'ROL-MH212':
                                sku = 'MH212'
                            if sku == 'ROL-OPTD1C':
                                sku = 'OPTD1C'
                            if sku == 'ROL-MH222BD':
                                sku = 'MH222BD'
                            if sku == 'ROL-MDP7':
                                sku = 'MDP7'
                            if sku == 'ROL-CYM10':
                                sku = 'CYM10'
                            if sku == 'ROL-MH28':
                                sku = 'MH28'
                            if sku == 'ROL-DBS10':
                                sku = 'DBS10'
                            if sku == 'ROL-RHA30':
                                sku = 'RHA30'
                            if sku == 'ROL-PD128BC':
                                sku = 'PD128BC'
                            if sku == 'ROL-PK-VAD307S':
                                sku = 'VAD307S'
                            if sku == 'ROL-PK-FP90XBKS':
                                sku = 'FP90XBKS'
                            if sku == 'ROL-VR1HD':
                                sku = 'VR1HD'
                            if sku == 'ROL-A88':
                                sku = 'A88MK2'
                            if sku == 'ROL-AE20W':
                                sku = 'AE20W'
                            if sku == 'ROL-BCARTIST':
                                sku = 'BCARTIST'
                            if sku == 'ROL-BCHOTVB':
                                sku = 'BCHOTVB'
                            if sku == 'ROL-BCSTAGE':
                                sku = 'BCSTAGE'
                            if sku == 'ROL-BK3BK':
                                sku = 'BK3BK'
                            if sku == 'ROL-CBG49':
                                sku = 'CBG49'
                            if sku == 'ROL-CY18DR':
                                sku = 'CY18DR'
                            if sku == 'ROL-DAP2D':
                                sku = 'DAP2D'
                            if sku == 'ROL-DAP2DP':
                                sku = 'DAP2DP'
                            if sku == 'ROL-DAP2S':
                                sku = 'DAP2S'
                            if sku == 'ROL-DAP2SP':
                                sku = 'DAP2SP'
                            if sku == 'ROL-DAP3D':
                                sku = 'DAP3D'
                            if sku == 'ROL-DAP3DP':
                                sku = 'DAP3DP'
                            if sku == 'ROL-DAP3S':
                                sku = 'DAP3S'
                            if sku == 'ROL-DAP3SP':
                                sku = 'DAP3SP'
                            if sku == 'ROL-DAP4DP':
                                sku = 'DAP4DP'
                            if sku == 'ROL-DAP4SP':
                                sku = 'DAP4SP'
                            if sku == 'ROL-EA7':
                                sku = 'EA7'
                            if sku == 'ROL-FANTOM6':
                                sku = 'FANTOM6'
                            if sku == 'ROL-FC300':
                                sku = 'FC300'
                            if sku == 'ROL-FP10BKS':
                                sku = 'FP10BKS'
                            if sku == 'ROL-GR55SBK':
                                sku = 'GR55SBK'
                            if sku == 'ROL-KD220':
                                sku = 'KD220'
                            if sku == 'ROL-MDYSTAGE':
                                sku = 'MDYSTG'
                            if sku == 'ROL-MH213':
                                sku = 'MH213'
                            if sku == 'ROL-MH218BD':
                                sku = 'MH218BD'
                            if sku == 'ROL-PD108BC':
                                sku = 'PD108BC'
                            if sku == 'ROL-PDA100MS':
                                sku = 'PDA100MS'
                            if sku == 'ROL-PDA140FGN':
                                sku = 'PDA140FGN'
                            if sku == 'ROL-PDX100':
                                sku = 'PDX100'
                            if sku == 'ROL-PDX8':
                                sku = 'PDX8'
                            if sku == 'ROL-PK-VAD507S':
                                sku = 'VAD507S'
                            if sku == 'ROL-RACKC400':
                                sku = 'RACKC400'
                            if sku == 'ROL-RACKC600':
                                sku = 'RACKC600'
                            if sku == 'ROL-RH200S':
                                sku = 'RH200S'
                            if sku == 'ROL-TD27':
                                sku = 'TD27'
                            if sku == 'ROL-TM1':
                                sku = 'TM1'
                            if sku == 'ROL-TM2KS':
                                sku = 'TM2KS'
                            if sku == 'ROL-TM6PRO':
                                sku = 'TM6PRO'
                            if sku == 'ROL-SPDSXPRO':
                                sku = 'SPDSXPRO'
                            if sku == 'ROL-CBB88V2':
                                sku = 'CBB88V2'
                            if sku == 'ROL-FP90XWH':
                                sku = 'FP90XWH'
                            if sku == 'ROL-SH4D':
                                sku = 'SH4D'
                            if sku == 'ROL-KS10Z':
                                sku = 'KS10Z'
                            if sku == 'ROL-AE30':
                                sku = 'AE30'
                            if sku == 'ROL-PK-VAD103S':
                                sku = 'VAD103S'
                            if sku == 'ROL-R07BK':
                                sku = 'R07BK'
                            if sku == 'ROL-SPD1K':
                                sku = 'SPD1K'
                            if sku == 'ROL-BA330':
                                sku = 'BA330'
                            if sku == 'ROL-HPD20':
                                sku = 'HPD20'
                            if sku == 'ROL-AE20':
                                sku = 'AE20'
                            if sku == 'ROL-RPB500PE':
                                sku = 'RPB500PE'
                            if sku == 'ROL-PM03':
                                sku = 'PM03'
                            if sku == 'ROL-KS20X':
                                sku = 'KS20X'
                            if sku == 'ROL-UVC01':
                                sku = 'UVC01'
                            if sku == 'ROL-RPB400PW':
                                sku = 'RPB400WH'
                            if sku == 'ROL-AE05':
                                sku = 'AE05'
                            if sku == 'ROL-KD10':
                                sku = 'KD10'
                            if sku == 'ROL-KSG8B':
                                sku = 'KSG8B'
                            if sku == 'ROL-VR730':
                                sku = 'VR730'
                            if sku == 'ROL-JUNODS76':
                                sku = 'JUNODS76'
                            if sku == 'ROL-CBBAX':
                                sku = 'CBBAX'
                            if sku == 'ROL-CBJDXI':
                                sku = 'CBJDXI'
                            if sku == 'ROL-RPB500PW':
                                sku = 'RPB500PW'
                            if sku == 'ROL-VH10':
                                sku = 'VH10'
                            if sku == 'ROL-V1HD':
                                sku = 'V1HD'
                            if sku == 'ROL-RHA7BK':
                                sku = 'RHA7BK'
                            if sku == 'ROL-KS10X':
                                sku = 'KS10X'
                            if sku == 'ROL-WM1D':
                                sku = 'WM1D'
                            if sku == 'ROL-CUBE10GX':
                                sku = 'CUBE10GX'
                            if sku == 'ROL-FD9':
                                sku = 'FD9'
                            if sku == 'ROL-CM30':
                                sku = 'CM30'
                            if sku == 'ROL-VT12':
                                sku = 'VT12'
                            if sku == 'ROL-A49WH':
                                sku = 'A49WH'
                            if sku == 'ROL-BAGFR1':
                                sku = 'BAGFR1'
                            if sku == 'ROL-CBBDJ505':
                                sku = 'CBBDJ505'
                            if sku == 'ROL-CBG49D':
                                sku = 'CBG49D'
                            if sku == 'ROL-DCS30':
                                sku = 'DCS30'
                            if sku == 'ROL-KD222GC':
                                sku = 'KD222GC'
                            if sku == 'ROL-KD222PW':
                                sku = 'KD222PW'
                            if sku == 'ROL-KDA22':
                                sku = 'KDA22'
                            if sku == 'ROL-KSC90WH':
                                sku = 'KSC90WH'
                            if sku == 'ROL-KT9':
                                sku = 'KT9'
                            if sku == 'ROL-MH220BD':
                                sku = 'MH220BD'
                            if sku == 'ROL-PD8':
                                sku = 'PD8'
                            if sku == 'ROL-PK-FP60XWHS':
                                sku = 'FP60XWHS'
                            if sku == 'ROL-RH300':
                                sku = 'RH300'
                            if sku == 'ROL-GP3PE':
                                sku = 'GP3PE'
            
            
            
                        if 'tama' in brand.lower():
            
                            if sku == 'TAM-MS736BK':
                                sku = '6101326AUSTRALIS'
                            if sku == 'TAM-MS205BK':
                                sku = '1003727AUSTRALIS'
                            if sku == 'TAM-HT430B':
                                sku = '6102793AUSTRALIS'
                            if sku == 'TAM-HH315D':
                                sku = '6102876AUSTRALIS'
                            if sku == 'TAM-HT750BC':
                                sku = '6102790AUSTRALIS'
                            if sku == 'TAM-HP600D':
                                sku = '6101160AUSTRALIS'
                            if sku == 'TAM-HP900PWN':
                                sku = '610907AUSTRALIS'
                            if sku == 'TAM-HP200PTW':
                                sku = '2602306AUSTRALIS'
                            if sku == 'TAM-HH205':
                                sku = '2602500AUSTRALIS'
                            if sku == 'TAM-HT530B':
                                sku = '6102791AUSTRALIS'
                            if sku == 'TAM-MS205STBK':
                                sku = '10037240AUSTRALIS'
                            if sku == 'TAM-TDK10':
                                sku = '2592911AUSTRALIS'
                            if sku == 'TAM-HP200P':
                                sku = '2602305AUSTRALIS'
                            if sku == 'TAM-HP30':
                                sku = '2606000AUSTRALIS'
                            if sku == 'TAM-HT130':
                                sku = '260048AUSTRALIS'
                            if sku == 'TAM-HT850BC':
                                sku = '6102788AUSTRALIS'
                            if sku == 'TAM-HPDS1TW':
                                sku = '6103368AUSTRALIS'
                            if sku == 'TAM-MS205':
                                sku = '1003722AUSTRALIS'
                            if sku == 'TAM-HP910LWN':
                                sku = '6101295AUSTRALIS'
                            if sku == 'TAM-HP310LW':
                                sku = '260381AUSTRALIS'
                            if sku == 'TAM-HT741B':
                                sku = '6102789AUSTRALIS'
                            if sku == 'TAM-MS436BK':
                                sku = '6101325AUSTRALIS'
                            if sku == 'TAM-HP310L':
                                sku = '260380AUSTRALIS'
                            if sku == 'TAM-MCA53':
                                sku = 'AUSTRALIS'
                            if sku == 'TAM-RW200':
                                sku = 'AUSTRALIS'
                            if sku == 'TAM-HP200PTWL':
                                sku = 'AUSTRALIS'
                            if sku == 'TAM-STCD7':
                                sku = '249420AUSTRALIS'
                            if sku == 'TAM-TMT9':
                                sku = '6101332AUSTRALIS'
                            if sku == 'TAM-HC63BW':
                                sku = '2606011AUSTRALIS'
                            if sku == 'TAM-HPDS1':
                                sku = '6103367AUSTRALIS'
                            if sku == 'TAM-MHA623':
                                sku = '249448AUSTRALIS'
                            if sku == 'TAM-HP900RN':
                                sku = '249448AUSTRALIS'
            
            
            
                        if 'radial' in brand.lower():
            
                            if sku == 'RAD-J48':
                                sku = 'RA-J48'
                            if sku == 'RAD-JDI':
                                sku = 'RA-JDI'
                            if sku == 'RAD-PRORMP':
                                sku = 'RA-PRORMP'
                            if sku == 'RAD-TWINCITY':
                                sku = 'RA-TWIN-CITY'
                            if sku == 'RAD-KEYLARGO':
                                sku = 'RA-KEY-LARGO'
                            if sku == 'RAD-SB1':
                                sku = 'RA-SB-1'
                            if sku == 'RAD-EXTCSTEREO':
                                sku = 'RA-EXTC-STEREO'
                            if sku == 'RAD-REAMPHP':
                                sku = 'RA-REAMP-HP'
                            if sku == 'RAD-MCBOOST':
                                sku = 'RA-MCBOOST'
                            if sku == 'RAD-PROD8':
                                sku = 'RA-PROD8'
                            if sku == 'RAD-JRAK4':
                                sku = 'RA-J-RAK4'
                            if sku == 'RAD-SGI':
                                sku = 'RA-SGI'
                            if sku == 'RAD-PROMS2':
                                sku = 'RA-PRO-MS2'
                            if sku == 'RAD-6PACK':
                                sku = 'RA-SIXPACK'
                            if sku == 'RAD-HDI':
                                sku = 'RA-HDI'
                            if sku == 'RAD-JX44V2':
                                sku = 'RA-JX44-V2'
                            if sku == 'RAD-REAMPSTN':
                                sku = 'RA-REAMP-STN'
                            if sku == 'RAD-PRODI':
                                sku = 'RA-PRODI'
                            if sku == 'RAD-SB2':
                                sku = 'RA-SB-2'
                            if sku == 'RAD-PROD2':
                                sku = 'RA-PROD2'
                            if sku == 'RAD-PRO48':
                                sku = 'RA-PRO48'
                            if sku == 'RAD-MIX21':
                                sku = 'RA-MIX-2:1'
                            if sku == 'RAD-PROAV2':
                                sku = 'RA-PROAV2'
                            if sku == 'RAD-PZPRO':
                                sku = 'RA-PZ-PRO'
                            if sku == 'RAD-SB5':
                                sku = 'RA-SB-5'
                            if sku == 'RAD-BTPROV2':
                                sku = 'RA-BT-PRO-V2'
                            if sku == 'RAD-USBPRO':
                                sku = 'RA-USB-PRO'
                            if sku == 'RAD-JDISTEREO':
                                sku = 'RA-JDI-STEREO'
                            if sku == 'RAD-CATAPMINITX':
                                sku = 'RA-CATAP-MINI-TX'
                            if sku == 'RAD-CATAPMINIRX':
                                sku = 'RA-CATAP-MINI-RX'
                            if sku == 'RAD-J48STEREO':
                                sku = 'RA-J48-STEREO'
                            if sku == 'RAD-EXTC500':
                                sku = 'RA-EXTC-500'
                            if sku == 'RAD-SHOTGUN':
                                sku = 'RA-SHOTGUN'
                            if sku == 'RAD-REAMPJCR':
                                sku = 'RA-REAMP-JCR'
                            if sku == 'RAD-IC1':
                                sku = 'RA-IC-1'
                            if sku == 'RAD-HEADBONEVT':
                                sku = 'RA-HEADBONE-VT'
                            if sku == 'RAD-SB6':
                                sku = 'RA-SB-6'
                            if sku == 'RAD-HOTSHOTABO':
                                sku = 'RA-HOTSHOT-ABO'
                            if sku == 'RAD-SWITCHBONEV2':
                                sku = 'RA-SWITCHBONE-V2'
                            if sku == 'RAD-TRIM2':
                                sku = 'RA-TRIM2'
                            if sku == 'RAD-PROAV1':
                                sku = 'RA-PROAV1'
                            if sku == 'RAD-JCLAMP':
                                sku = 'RA-J-CLAMP'
                            if sku == 'RAD-SA19RA':
                                sku = 'RA-SA19-RA'
                            if sku == 'RAD-WHB1':
                                sku = 'RA-WH-B1'
                            if sku == 'RAD-BIGSHOTIO':
                                sku = 'RA-BIGSHOT-I/O'
                            if sku == 'RAD-EXTCSA':
                                sku = 'RA-EXTC-SA'
                            if sku == 'RAD-JDIDUPLEX':
                                sku = 'RA-DUPLEX'
                            if sku == 'RAD-JISO':
                                sku = 'RA-J-ISO'
                            if sku == 'RAD-JR2':
                                sku = 'RA-JR2'
                            if sku == 'RAD-JS2':
                                sku = 'RA-JS2'
                            if sku == 'RAD-LX3':
                                sku = 'RA-LX-3'
                            if sku == 'RAD-POWERHOUSE':
                                sku = 'RA-POWERHOUSE'
                            if sku == 'RAD-PZPRE':
                                sku = 'RA-PZ-PRE'
                            if sku == 'RAD-SAT2':
                                sku = 'RA-SAT-2'
                            if sku == 'RAD-SW8MK2':
                                sku = 'RA-SW8-MK2'
                            if sku == 'RAD-TWINISO':
                                sku = 'RA-TWIN-ISO'
                            if sku == 'RAD-WORKHORSE':
                                sku = 'RA-WORKHORSE'
                            if sku == 'RAD-WR8':
                                sku = 'RA-W-R8'
            
            
            
                        if brand.lower() == 'se':
                            if sku == 'SE-DM1':
                                sku = 'SEEL_DM1MICPRE'
                            if sku == 'SE-RFX':
                                sku = 'SEEL_RFX'
                            if sku == 'SE-V7':
                                sku = 'SEEL_V7'
                            if sku == 'SE-DYNACASTER':
                                sku = 'SEEL_DYNACASTER'
                            if sku == 'SE-VR2':
                                sku = 'SEEL_VR2'
                            if sku == 'SE-SE8PAIR':
                                sku = 'SEEL_SE8PAIR'
                            if sku == 'SE-V7VE':
                                sku = 'SEEL_V7VE'
                            if sku == 'SE-HB52':
                                sku = 'SEEL_HB52'
                            if sku == 'SE-RF':
                                sku = 'SEEL_RF'
                            if sku == 'SE-V7BFG':
                                sku = 'SEEL_V7BFG'
                            if sku == 'SE-DM2':
                                sku = 'SEEL_DM2'
                            if sku == 'SE-VR1':
                                sku = 'SEEL_VR1'
                            if sku == 'SE-RFXRD':
                                sku = 'SEEL_RFXRED'
                            if sku == 'SE-V7X':
                                sku = 'SEEL_V7X'
                            if sku == 'SE-RFXWH':
                                sku = 'SEEL_RFXWHITE'
                            if sku == 'SE-RFSPACE':
                                sku = 'SEEL_RFSPACE'
                            if sku == 'SE-X1SPACKAGE':
                                sku = 'SEEL_X1SPACKAGE'
                            if sku == 'SE-2200':
                                sku = 'SEEL_2200'
                            if sku == 'SE-RFBK':
                                sku = 'SEEL_RFBLACK'
                            if sku == 'SE-SEPOP':
                                sku = 'SEEL_POP'
                            if sku == 'SE-X1A':
                                sku = 'SEEL_X1A'
                            if sku == 'SE-RFXBLSW':
                                sku = 'SEEL_RFX_BLSW'
                            if sku == 'SE-V3':
                                sku = 'SEEL_V3'
                            if sku == 'SE-SEDUALPOP':
                                sku = 'SEEL_DUALPOP'
                            if sku == 'SE-NEOMUSB':
                                sku = 'SEEL_NEOMUSB'
                            if sku == 'SE-DM3':
                                sku = 'SEEL_DM3'
                            if sku == 'SE-ISOLATIONPACK':
                                sku = 'SEEL_ISOLATIONP'
                            if sku == 'SE-VBEAT':
                                sku = 'SEEL_VBEAT'
                            if sku == 'SE-4400AST':
                                sku = 'SEEL_4400AST'
                            if sku == 'SE-VPACKARENA':
                                sku = 'SEEL_VPACKARENA'
                            if sku == 'SE-SE8PAIRVE':
                                sku = 'SEEL_SE8PVE'
                            if sku == 'SE-GEMINI-II':
                                sku = 'SEEL_GEMINIII'
                            if sku == 'SE-VR1VE':
                                sku = 'SEEL_VR1VE'
                            if sku == 'SE-Z5600AII':
                                sku = 'SEEL_Z5600AII'
                            if sku == 'SE-SEX1R':
                                sku = 'SEEL_X1R'
                            if sku == 'SE-2200VE':
                                sku = 'SEEL_2200VE'
                            if sku == 'SE-X1SVOCALPACK':
                                sku = 'SEEL_X1SVOCALPACK'
                            if sku == 'SE-V7MC1':
                                sku = 'SEEL_V7MC1'
                            if sku == 'SE-V7SWITCH':
                                sku = 'SEEL_V7SWITCH'
                            if sku == 'SE-VKICK':
                                sku = 'SEEL_VKICK'
                            if sku == 'SE-SE7PAIR':
                                sku = 'SEEL_SE7PAIR'
                            if sku == 'SE-SE7':
                                sku = 'SEEL_SE7'
                            if sku == 'SE-SE8':
                                sku = 'SEEL_SE8'
                            if sku == 'SE-RFPROB2':
                                sku = 'SEEL_RFPROB2'
                            if sku == 'SE-2300':
                                sku = 'SEEL_2300'
                            if sku == 'SE-GUITARF':
                                sku = 'SEEL_GUITARF'
                            if sku == 'SE-PROMICLASER':
                                sku = 'SEEL_PROMICLASER'
                            if sku == 'SE-RN17':
                                sku = 'SEEL_RN17'
                            if sku == 'SE-RN17ST':
                                sku = 'SEEL_RN17ST'
                            if sku == 'SE-RNR1':
                                sku = 'SEEL_RNR1'
                            if sku == 'SE-RNT':
                                sku = 'SEEL_RNT'
                            if sku == 'SE-SE4400A':
                                sku = 'SEEL_4400A'
                            if sku == 'SE-T2':
                                sku = 'SEEL_T2'
                            if sku == 'SE-VCLAMP':
                                sku = 'SEEL_VCLAMP'
            
            
            
                        if brand.lower() == 'akg':
                            if sku == 'AKG-K371':
                                sku = 'K-371CMI'
                            if sku == 'AKG-K52':
                                sku = 'K-52CMI'
                            if sku == 'AKG-DMS100VOC':
                                sku = 'DMS-100VOCCMI'
                            if sku == 'AKG-DRUMPACKS1':
                                sku = 'DP-SESSION1CMI'
                            if sku == 'AKG-K240S':
                                sku = 'K-240SCMI'
                            if sku == 'AKG-K92':
                                sku = 'K-92CMI'
                            if sku == 'AKG-K702':
                                sku = 'K-702CMI'
                            if sku == 'AKG-C414XLII':
                                sku = 'C-414XLIICMI'
                            if sku == 'AKG-C414XLS':
                                sku = 'C-414XLSCMI'
                            if sku == 'AKG-K371BT':
                                sku = 'K-371BTCMI'
                            if sku == 'AKG-K-712':
                                sku = 'CMI'
                            if sku == 'AKG-D112MK2':
                                sku = 'D-112MKIICMI'
                            if sku == 'AKG-K612':
                                sku = 'K-612CMI'
                            if sku == 'AKG-D7':
                                sku = 'D-7CMI'
                            if sku == 'AKG-P420':
                                sku = 'P-420CMI'
                            if sku == 'AKG-C214':
                                sku = 'C-214CMI'
                            if sku == 'AKG-K361BT':
                                sku = 'K-361BTCMI'
                            if sku == 'AKG-K240MKII':
                                sku = 'K-240MKIICMI'
                            if sku == 'AKG-K72':
                                sku = 'K-72CMI'
                            if sku == 'AKG-CK99L':
                                sku = 'CK-99LCMI'
                            if sku == 'AKG-P120':
                                sku = 'P-120CMI'
                            if sku == 'AKG-EK300':
                                sku = 'EK-300CMI'
                            if sku == 'AKG-D5':
                                sku = 'D-5CMI'
                            if sku == 'AKG-P170':
                                sku = 'P-170CMI'
                            if sku == 'AKG-K361':
                                sku = 'K-361CMI'
                            if sku == 'AKG-P5S':
                                sku = 'P-5SCMI'
                            if sku == 'AKG-C417L':
                                sku = 'C417LCMI'
                            if sku == 'AKG-C1000SMKIV':
                                sku = 'C-1000SMKIVCMI'
                            if sku == 'AKG-D12VR':
                                sku = 'D-12VRCMI'
                            if sku == 'AKG-EK500':
                                sku = 'EK-500SCMI'
                            if sku == 'AKG-P220':
                                sku = 'P-220CMI'
                            if sku == 'AKG-C5':
                                sku = 'C-5CMI'
                            if sku == 'AKG-K275':
                                sku = 'K-275CMI'
                            if sku == 'AKG-K182':
                                sku = 'K-182CMI'
                            if sku == 'AKG-K271MKII':
                                sku = 'K-271MKIICMI'
                            if sku == 'AKG-C314':
                                sku = 'C-314CMI'
                            if sku == 'AKG-K175':
                                sku = 'K-175CMI'
                            if sku == 'AKG-C414XLIIST':
                                sku = 'C-414XLIISTCMI'
                            if sku == 'AKG-C520':
                                sku = 'C-520CMI'
                            if sku == 'AKG-DMS300VOC':
                                sku = 'DMS-300VOCCMI'
                            if sku == 'AKG-LYRA':
                                sku = 'LYRACMI'
                            if sku == 'AKG-MKGL':
                                sku = 'MK-GLCMI'
                            if sku == 'AKG-C544L':
                                sku = 'C-544LCMI'
                            if sku == 'AKG-H85':
                                sku = 'H-85CMI'
                            if sku == 'AKG-MPAVL':
                                sku = 'MPA-VLCMI'
                            if sku == 'AKG-C111L':
                                sku = 'C-111LCMI'
                            if sku == 'AKG-B48L':
                                sku = 'B-48LCMI'
                            if sku == 'AKG-ARA':
                                sku = 'AKG-ARACMI'
                            if sku == 'AKG-PODCAST':
                                sku = 'AKG-PODCASTCMI'
                            if sku == 'AKG-C12VR':
                                sku = 'C-12VRCMI'
                            if sku == 'AKG-C214ST':
                                sku = 'C-214STCMI'
                            if sku == 'AKG-C3000':
                                sku = 'C-3000CMI'
                            if sku == 'AKG-C314ST':
                                sku = 'C-314STCMI'
                            if sku == 'AKG-C411L':
                                sku = 'C-411LCMI'
                            if sku == 'AKG-C414XLSST':
                                sku = 'C-414XLSSTCMI'
                            if sku == 'AKG-C451B':
                                sku = 'C-451BCMI'
                            if sku == 'AKG-C451BST':
                                sku = 'C-451BSTCMI'
                            if sku == 'AKG-C480BCOMBO':
                                sku = 'C-480BCOMBOCMI'
                            if sku == 'AKG-C519M':
                                sku = 'C-519MCMI'
                            if sku == 'AKG-C520L':
                                sku = 'C-520LCMI'
                            if sku == 'AKG-C555L':
                                sku = 'C-555LCMI'
                            if sku == 'AKG-C5WL1':
                                sku = 'C-5WL1CMI'
                            if sku == 'AKG-C7':
                                sku = 'C-7CMI'
                            if sku == 'AKG-CBL99':
                                sku = 'CB-L99CMI'
                            if sku == 'AKG-D7WL1':
                                sku = 'D-7WL1CMI'
                            if sku == 'AKG-DGN99E':
                                sku = 'DG-N99ECMI'
                            if sku == 'AKG-DMS100INST':
                                sku = 'DMS-100INSTCMI'
                            if sku == 'AKG-DMS300INST':
                                sku = 'DMS-300INSTCMI'
                            if sku == 'AKG-HSC171':
                                sku = 'HS-C171CMI'
                            if sku == 'AKG-HSD171':
                                sku = 'HS-C171CMI'
                            if sku == 'AKG-HSD271':
                                sku = 'HS-D271CMI'
                            if sku == 'AKG-HT470C5':
                                sku = 'HT-470C5CMI'
                            if sku == 'AKG-HT470D5D':
                                sku = 'HT-470D5DCMI'
                            if sku == 'AKG-K812':
                                sku = 'K-812PROCMI'
                            if sku == 'AKG-P3S':
                                sku = 'P-3SCMI'
                            if sku == 'AKG-P5I':
                                sku = 'P-5ICMI'
                            if sku == 'AKG-C411PP':
                                sku = 'C-411PPCMI'
                            if sku == 'AKG-PT470':
                                sku = 'PT-470CMI'
                            if sku == 'AKG-PF80':
                                sku = 'PF-80CMI'
                            if sku == 'AKG-SA60':
                                sku = 'SA-60CMI'
                            if sku == 'AKG-K872':
                                sku = 'K-872CMI'
                            if sku == 'AKG-C519ML':
                                sku = 'C-519MLCMI'
                            if sku == 'AKG-C636BLK':
                                sku = 'C-636BLKCMI'
                            if sku == 'AKG-CU800':
                                sku = 'CU-800CMI'
                            if sku == 'AKG-D40':
                                sku = 'D-40CMI'
                            if sku == 'AKG-D5S':
                                sku = 'D-5SCMI'
                            if sku == 'AKG-D5WL1':
                                sku = 'D-5WL1CMI'
                            if sku == 'AKG-D7S':
                                sku = 'D-7SCMI'
                            if sku == 'AKG-DHT800AU':
                                sku = 'DHT-800AUCMI'
                            if sku == 'AKG-DMM8ULD':
                                sku = 'DMM-8ULDCMI'
                            if sku == 'AKG-DSR800AU':
                                sku = 'DSR-800AUCMI'
                            if sku == 'AKG-HSC271':
                                sku = 'CMI'
                            if sku == 'AKG-HT4500':
                                sku = 'HS-C271CMI'
                            if sku == 'AKG-PT45A':
                                sku = 'PT-45ACMI'
                            if sku == 'AKG-SR4500':
                                sku = 'SR-4500CMI'
            
                        if brand.lower() == 'dbx':
                            sku = sku.replace('DIG-', '')
                            sku = f'{sku}CMI'
            
                        if 'darkglass' in brand.lower():
                            sku = sku.replace('DGE-', 'DG-')
                            sku = f'{sku}CMI'
            
                        if 'source audio' in brand.lower():
                            sku = f'{sku}CMI'
            
                        if 'native instruments' in brand.lower():
                            sku = f'{sku}CMI'
            
                        if 'nektar' in brand.lower():
            
                            if sku == 'NEK-GX61':
                                sku = 'NEKT_GX61'
                            if sku == 'NEK-PACER':
                                sku = 'NEKT_PACER'
                            if sku == 'NEK-NP2':
                                sku = 'NEKT_NP-2'
                            if sku == 'NEK-SE61':
                                sku = 'NEKT_SE61'
                            if sku == 'NEK-IMPACTLX88P':
                                sku = 'NEKT_LX88'
                            if sku == 'NEK-IMPACTLX49P':
                                sku = 'NEKT_LX49'
                            if sku == 'NEK-SE49':
                                sku = 'NEKT_SE49'
                            if sku == 'NEK-GX49':
                                sku = 'NEKT_GX49'
                            if sku == 'NEK-IMPACTLX61P':
                                sku = 'NEKT_LX61'
                            if sku == 'NEK-LXMINI':
                                sku = 'NEKT_LXMINI'
                            if sku == 'NEK-MIDIFLEX4':
                                sku = 'NEKT_MIDIFLEX4'
                            if sku == 'NEK-SE25':
                                sku = 'NEKT_SE25'
                            if sku == 'NEK-GXP88':
                                sku = 'NEKT_GXP88'
                            if sku == 'NEK-NP1':
                                sku = 'NEKT_NP-1'
                            if sku == 'NEK-IMPACTLX25P':
                                sku = 'NEKT_LX25'
                            if sku == 'NEK-GXMINI':
                                sku = 'NEKT_GXMINI'
                            if sku == 'NEK-PANORAMAT4':
                                sku = 'NEKT_PANORAMAT4'
                            if sku == 'NEK-PANORAMAP6':
                                sku = 'NEKT_PANORAMAP6'
                            if sku == 'NEK-PANORAMAP4':
                                sku = 'NEKT_PANORAMAP4'
                            if sku == 'NEK-PANORAMAT6':
                                sku = 'NEKT_PANORAMAT6'
                            if sku == 'NEK-GXP61':
                                sku = 'NEKT_GXP61'
                            if sku == 'NEK-AURA':
                                sku = 'NEKT_AURA'
                            if sku == 'NEK-GXP49':
                                sku = 'NEKT_GXP49'
                            if sku == 'NEK-PANORAMAP1':
                                sku = 'NEKT_PANORAMAP1'
                            if sku == 'NEK-NXP':
                                sku = 'NEKT_NX-P'
                            if sku == 'NEK-BOLT':
                                sku = 'NEKT_BOLT'
            
            
            
                        if brand.lower() == 'rockboard':
            
                            if sku == 'RB-WRQUAD42GB':
                                sku = 'WR-QUAD-4.2-GB'
                            if sku == 'RB-WRQUAD41GB':
                                sku = 'WR-QUAD-4.2-GB'
                            if sku == 'RB-WRTRES31GB':
                                sku = 'WR-TRES-3.1-GB'
                            if sku == 'RB-WRMODULE1XLR':
                                sku = 'WR-MODULE1-XLR'
                            if sku == 'RB-WRTRES30GB':
                                sku = 'WR-TRES-3.0-0GB'
                            if sku == 'RB-WRTRES32GB':
                                sku = 'WR-TRES-3.2-GB'
                            if sku == 'RB-WRDUO21GB':
                                sku = 'WR-DUO-2.1-GB'
                            if sku == 'RB-WRQUAD42FC':
                                sku = 'WR-QUAD-4.2-FC'
                            if sku == 'RB-WRQUAD43FC':
                                sku = 'WR-QUAD-4.3-FC'
                            if sku == 'RB-WRDUO20GB':
                                sku = 'WR-DUO-2.0-GB'
                            if sku == 'RB-WRQUAD43GB':
                                sku = 'WR-QUAD-4.3-GB'
                            if sku == 'RB-WRTRES31FC':
                                sku = 'WR-TRES-3.1-FC'
                            if sku == 'RB-WRMODULE2MIDI':
                                sku = 'WR-MODULE2-MIDI'
                            if sku == 'RB-WRTHETRAY':
                                sku = 'WR-THE-TRAY'
                            if sku == 'RB-WRHLTAPE300':
                                sku = 'WR-HLTAPE-300'
                            if sku == 'RB-WRCINQUE52GB':
                                sku = 'WR-CINQUE-5.2-GB'
                            if sku == 'RB-WRRBSTOMPETES':
                                sku = 'WR-RB-STOMPETE-S'
                            if sku == 'RB-WRRBQMTA':
                                sku = 'WR-RBQM-TA'
                            if sku == 'RB-WRRBQMTF':
                                sku = 'WR-RBQM-TF'
                            if sku == 'RB-WRRBQMQR':
                                sku = 'WR-RBQM-QR'
                            if sku == 'RB-WRFLTRS30BK':
                                sku = 'WR-FL-TRS-30-BK'
                            if sku == 'RB-WRFLYS30BK':
                                sku = 'WR-FL-YS-30-BK'
                            if sku == 'RB-WRFLTRS15BK':
                                sku = 'WR-FL-TRS-15-BK'
                            if sku == 'RB-WRCINQUE53FC':
                                sku = 'WR-CINQUE-5.3-FC'
                            if sku == 'RB-WRRBQMTE':
                                sku = 'WR-RBQM-TE'
                            if sku == 'RB-WRCIN52CASE':
                                sku = 'WR-CIN-5.2-CASE'
                            if sku == 'RB-WRQUAD41BAG':
                                sku = 'WR-QUAD-4.1-BAG'
                            if sku == 'RB-WRCINQUE53GB':
                                sku = 'WR-CINQUE-5.3-GB'
                            if sku == 'RB-WRQUAD43A':
                                sku = 'WR-QUAD-4.3-A'
                            if sku == 'RB-WRDUO22GB':
                                sku = 'WR-DUO-2.2-GB'
                            if sku == 'RB-WRQUAD42CASE':
                                sku = 'WR-QUAD-4.2-CASE'
                            if sku == 'RB-WRMODULE3':
                                sku = 'WR-MODULE-3'
                            if sku == 'RB-WRQUAD41FC':
                                sku = 'WR-QUAD-4.1-FC'
                            if sku == 'RB-WRRBSTOMPETEB':
                                sku = 'WR-RB-STOMPETE-B'
                            if sku == 'RB-WRPOWERV16':
                                sku = 'WR-POWER-V16'
                            if sku == 'RB-WRRBLEDPB':
                                sku = 'WR-RB-LED-PB'
                            if sku == 'RB-WRMODULE5':
                                sku = 'WR-MODULE-5'
                            if sku == 'RB-WRTRES30FC':
                                sku = 'WR-TRES-3.0-FC'
                            if sku == 'RB-WRRBQMTG':
                                sku = 'WR-RBQM-TG'
                            if sku == 'RB-WRRBQMTK':
                                sku = 'WR-RBQM-TK'
                            if sku == 'RB-WRCINQUE52FC':
                                sku = 'WR-CINQUE-5.2-FC'
                            if sku == 'RB-WRCINQUE54GB':
                                sku = 'WR-CINQUE-5.4-GB'
                            if sku == 'RB-WRRBQMTJ':
                                sku = 'WR-RBQM-TJ'
            
                        if brand.lower() == 'strymon':
            
                            if sku == 'STR-BIGSKY':
                                sku = 'SN-BIG-SKY'
                            if sku == 'STR-ZUMA':
                                sku = 'SN-ZUMA'
                            if sku == 'STR-IRIDIUM':
                                sku = 'SN-IRIDIUM'
                            if sku == 'STR-TIMELINE':
                                sku = 'SN-TIMELINE'
                            if sku == 'STR-FLINTMK2':
                                sku = 'SN-FLINT-2'
                            if sku == 'STR-NIGHTSKY':
                                sku = 'SN-NIGHT-SKY'
                            if sku == 'STR-VOLANTE':
                                sku = 'SN-VOLANTE'
                            if sku == 'STR-DECOMK2':
                                sku = 'SN-DECO-2'
                            if sku == 'STR-OJAI':
                                sku = 'SN-OJAI'
                            if sku == 'STR-MOBIUS':
                                sku = 'SN-MOBIUS'
                            if sku == 'STR-OJAIR30':
                                sku = 'SN-OJAI-R30'
                            if sku == 'STR-BLUESKY':
                                sku = 'SN-BLUE-SKY'
                            if sku == 'STR-OJAIEXKIT':
                                sku = 'SN-OJAI-EXP'
                            if sku == 'STR-ZUMAR300':
                                sku = 'SN-ZUMA-R300'
                            if sku == 'STR-BLUESKYMK2':
                                sku = 'SN-BLUE-SKY-2'
                            if sku == 'STR-SUNSET':
                                sku = 'SN-SUNSET'
                            if sku == 'STR-ELCAPISTANM2':
                                sku = 'SN-EL-CAPISTAN-2'
                            if sku == 'STR-COMPADRE':
                                sku = 'SN-COMPADRE'
                            if sku == 'STR-DIGMK2':
                                sku = 'SN-DIG-2'
                            if sku == 'STR-ELCAPISTAN':
                                sku = 'SN-EL-CAPISTAN'
                            if sku == 'STR-RIVERSIDE':
                                sku = 'SN-RIVERSIDE'
                            if sku == 'STR-LEXMK2':
                                sku = 'SN-LEX-2'
                            if sku == 'STR-MAGNETO':
                                sku = 'SN-MAGNETO'
                            if sku == 'STR-OJAIR30EXKIT':
                                sku = 'SN-OJAI-R30-EXP'
                            if sku == 'STR-DIG':
                                sku = 'SN-DIG'
                            if sku == 'STR-ZELZAH':
                                sku = 'SN-ZELZAH'
                            if sku == 'STR-DC185':
                                sku = 'SN-DC185'
                            if sku == 'STR-BRKTZUMA':
                                sku = 'SN-ZUMA-BRACKET'
                            if sku == 'STR-MULTISWITCHP':
                                sku = 'SN-MULTI-SWITCH-PLUS'
                            if sku == 'STR-LEX':
                                sku = 'SN-LEX'
                            if sku == 'STR-CONDUIT':
                                sku = 'SN-CONDUIT'
                            if sku == 'STR-AA1':
                                sku = 'SN-AA.1'
                            if sku == 'STR-MINISWITCH':
                                sku = 'SN-MINI-SWITCH'
                            if sku == 'STR-DAISY':
                                sku = 'SN-DAISY'
                            if sku == 'STR-PR25':
                                sku = 'SN-PR-25'
                            if sku == 'STR-VDC':
                                sku = 'SN-VDC'
                            if sku == 'STR-EIAJ9':
                                sku = 'SN-EIAJ9'
                            if sku == 'STR-PR21':
                                sku = 'SN-PR-21'
                            if sku == 'STR-MIDIRMRT':
                                sku = 'SN-MIDI-RMRT'
                            if sku == 'STR-MIDISMRT':
                                sku = 'SN-MIDI-SMRT'
                            if sku == 'STR-MIDISMST':
                                sku = 'SN-MIDI-SMST'
                            if sku == 'STR-MIDIRMST':
                                sku = 'SN-MIDI-RMST'
                            if sku == 'STR-ORBIT':
                                sku = 'SN-ORBIT'
                            if sku == 'STR-OLA':
                                sku = 'SN-OLA'
                            if sku == 'STR-MULTISWITCH':
                                sku = 'SN-MULTI-SWITCH'
                            if sku == 'STR-BRIGADIER':
                                sku = 'SN-BRIGADIER'
                            if sku == 'STR-EIAJ18':
                                sku = 'SN-EIAJ18'
                            if sku == 'STR-EIAJ36':
                                sku = 'SN-EIAJ36'
            
                        if brand.lower() == 'emg':
            
                            sku = sku.replace('EMG-', '')
            
                        if brand.lower() == 'remo':
            
                            sku = sku.replace('REM-', '')
                            sku = sku[:2] + '-' + sku[2:6] + '-' + sku[6:]
            
                        if brand.lower() == 'mapex':
            
                            sku = sku.replace('MAP-H', '90H-')
                            sku = f'{sku}EF'
            
                        if 'alto' in brand.lower():
            
                            sku = sku.replace('ALT-', '57')
                            sku = f'{sku}EF'
            
                        if brand.lower() == 'udg':
            
                            sku = sku.replace('UDG-', '63')
                            sku = f'{sku}EF'
            
            
            
                        if brand.lower() == 'esp':
            
                            if sku == 'ESP-30EC':
                                sku = 'ESP-30ECCMI'
                            if sku == 'ESP-30HZ':
                                sku = 'ESP-30HZCMI'
                            if sku == 'ESP-30HZB':
                                sku = 'ESP-30HZBCMI'
                            if sku == 'ESP-30V':
                                sku = 'ESP-30VCMI'
                            if sku == 'ESP-30VG':
                                sku = 'ESP-30VGCMI'
                            if sku == 'ESP-LEC1000TCSTB':
                                sku = 'LEC-1000TCTSBSCMI'
                            if sku == 'ESP-LEC1000TCTBC':
                                sku = 'LEC-1000TCTSTBCCMI'
                            if sku == 'ESP-LEC1000VB':
                                sku = 'LEC-1000VBCMI'
                            if sku == 'ESP-LEC1000VBSD':
                                sku = 'LEC-1000VBSDCMI'
                            if sku == 'ESP-LEC256BLK':
                                sku = 'LEC-256BLKCMI'
                            if sku == 'ESP-LEC256BLKS':
                                sku = 'LEC-256BLKSCMI'
                            if sku == 'ESP-LEC256CB':
                                sku = 'LEC-256CBCMI'
                            if sku == 'ESP-LEC256CBLH':
                                sku = 'LEC-256CBLHCMI'
                            if sku == 'ESP-LEC256FMDBSB':
                                sku = 'LEC-256FMDBSBCMI'
                            if sku == 'ESP-LEC256STPB':
                                sku = 'LEC-256STPBCMI'
                            if sku == 'ESP-LEC256SW':
                                sku = 'LEC-256SWCMI'
                            if sku == 'ESP-LH200FMDBSB':
                                sku = 'LH-200FMDBSBCMI'
                            if sku == 'ESP-LH200FMSTP':
                                sku = 'LH-200FMSTPCMI'
                            if sku == 'ESP-LJMIIQMBLKSB':
                                sku = 'LJ-MIIQMBLKSHBCMI'
                            if sku == 'ESP-LKH602':
                                sku = 'LKH-602CMI'
                            if sku == 'ESP-LMHTARMSWS':
                                sku = 'LM-HTARMSWSCMI'
                            if sku == 'ESP-LMHTBKMBLKS':
                                sku = 'LM-HTBKMBLKSCMI'
                            if sku == 'ESP-SNAKEBYTEBS':
                                sku = 'SNAKEBYTE-BLKSCMI'
                            if sku == 'ESP-LALEXIRIPPED':
                                sku = 'LALEXI-RIPPEDCMI'
                            if sku == 'ESP-LAR1000QMCH':
                                sku = 'LARROW-1000QMCHCMI'
                            if sku == 'ESP-LEC1000BCHMS':
                                sku = 'LEC-1000BCHMSCMI'
                            if sku == 'ESP-LEC1000TCCB':
                                sku = 'LEC-1000TCTMCHBCMI'
                            if sku == 'ESP-LEC1000TCTVS':
                                sku = 'LEC-1000TCTVSHCMI'
                            if sku == 'ESP-LEC1000TCVGS':
                                sku = 'LEC-1000TCTMVGSCMI'
                            if sku == 'ESP-LH31007BFSBS':
                                sku = 'LH3-1007BFMSTBSCMI'
                            if sku == 'ESP-LM1001NTQMCB':
                                sku = 'LM-1001NTQMCHBCMI'
                            if sku == 'ESP-LSN1000HTFB':
                                sku = 'LSN-1000HTFBLSTCMI'
                            if sku == 'ESP-LSN200HTDMPS':
                                sku = 'LSN-200HTMDMPSCMI'
                            if sku == 'ESP-LTE200MNBK':
                                sku = 'LTE-200MNBKCMI'
                            if sku == 'ESP-LTE200RWSW':
                                sku = 'LTE-200RWSWCMI'
                            if sku == 'ESP-LTE200TSBST':
                                sku = 'LTE-200TSBSTCMI'
                            if sku == 'ESP-30AL':
                                sku = 'ESP-30ALCMI'
                            if sku == 'ESP-LM200FMSTBLK':
                                sku = 'LM-200FMSTBLKCMI'
                            if sku == 'ESP-LVP256DBSB':
                                sku = 'LVP-256DBSBCMI'
                            if sku == 'ESP-LEX200BLK':
                                sku = 'LEX-200BLKCMI'
            
                        if brand.lower() == 'digitech':
            
                            sku = sku.replace('DIG-', '')
                            if sku == 'WHAMMYDT':
                                sku = 'WHAMMY-DT'
                            if sku == 'WHAMMYBASS':
                                sku = 'WHAMMY-BASS'
                            if sku == 'TRIOPLUS':
                                sku = 'TRIO-PLUS'
                            if sku == 'RUBBERNECK':
                                sku = 'DOD-RUBBERNECK'
                            if sku == 'MINIEXP':
                                sku = 'DOD-MINIEXP'
                            if sku == 'MINIVOL':
                                sku = 'DOD-MINIVOL'
                            if sku == 'GONKULATOR':
                                sku = 'DOD-GONKULATOR'
                            if sku == 'LGLASS':
                                sku = 'DOD-LGLASS'
                            if sku == 'FS3X':
                                sku = 'FS-3X'
                            sku = f'{sku}CMI'
            
                        if brand.lower() == 'casio':
                            sku = sku.replace('CAS-', '')
            
                        if brand.lower() == "d'addario":
                            sku = sku.replace('DAD-', '')
                            sku = sku.replace('3D', '-3D')
                            sku = sku.replace('10P', '-10P')
                            sku = sku.replace('B25', '-B25')
            
            
                        if brand.lower() == 'epiphone':
                            sku = sku.replace('EPI-', '')
                            sku = f'{sku}AUSTRALIS'
            
                        if "seymour" in brand.lower():
                            sku = sku.replace('SEY-', '')
                            sku = f'{sku}AUSTRALIS'
            
                        if "valencia" in brand.lower():
                            sku = sku.replace('VAL-', '')
                        if "carson" in brand.lower():
                            sku = sku.replace('CAR-', '')
                        if "mxr" in brand.lower():
                            sku = sku.replace('MXR-', '')
                        if "v-case" in brand.lower():
                            sku = sku.replace('V-C-', '')
            
                        if "vic firth" in brand.lower():
                            sku = sku.replace('VIC-', '')
            
                        if "xtreme" in brand.lower():
                            sku = sku.replace('XTR-', '')
                        if "snark" in brand.lower():
                            sku = sku.replace('SNA-', '')
                        if "dunlop" in brand.lower():
                            sku = sku.replace('DLP-', '')
                        if "mahalo" in brand.lower():
                            sku = sku.replace('MHL-', '')
            
                        if "cnb" in brand.lower():
                            sku = sku.replace('CNB-', '')
            
                        if "dxp" in brand.lower():
                            sku = sku.replace('DXP-', '')
                        if "mano" in brand.lower():
                            sku = sku.replace('MAO-', '')
            
                        if "dimarzio" in brand.lower():
                            sku = sku.replace('DIM-', '')
            
            
                        if "ashton" in brand.lower():
                            sku = sku.replace('ASH-', '')
                            sku = f'{sku}AUSTRALIS'
            
                        if "boss" in brand.lower():
                            sku = sku.replace('BOS-', '')
            
                        if "headrush" in brand.lower():
                            sku = sku.replace('HRP-', '')
                            sku = f'11{sku}EF'
            
                        if "auralex" in brand.lower():
                            sku = sku.replace('HRP-', '')
                            sku = f'11{sku}EF'
            
                        if "hercules" in brand.lower():
                            sku = sku.replace('HER-', '')
                            sku = f'62{sku}EF'
            
                        if "martin" in brand.lower():
                            sku = sku.replace('MAN-', '')
                            sku = f'41{sku}EF'
            
                        if "m-audio" in brand.lower():
                            if sku == 'MAU-KEYSTAT49MK3':
                                sku = '46KEYSTATION49MK3EF'
                            if sku == 'MAU-OXYGENPROMIN':
                                sku = '46OXYGENPROMINIEF'
                            if sku == 'MAU-KEYSTAT61MK3':
                                sku = '46KEYSTATION61MK3EF'
                            if sku == 'MAU-BX5D3':
                                sku = '46BX5D3EF'
                            if sku == 'MAU-OXYGENPRO49':
                                sku = '46OXYGENPRO49EF'
                            if sku == 'MAU-HAMMER88':
                                sku = '46HAMMER88EF'
                            if sku == 'MAU-OXYGENPRO61':
                                sku = '46OXYGENPRO61EF'
                            if sku == 'MAU-OXYGEN49MK5':
                                sku = '46OXYGEN49MKVEF'
                            if sku == 'MAU-KEYSTAT88MK3':
                                sku = '46KEYSTATION88MK3EF'
                            if sku == 'MAU-OXYGEN61MK5':
                                sku = '46OXYGEN61MKVEF'
                            if sku == 'MAU-KSMINI32MK3':
                                sku = '46KEYSTATIONMINI32MK3EF'
                            if sku == 'MAU-OXYGEN25MK5':
                                sku = '46OXYGEN25MKVEF'
                            if sku == 'MAU-BX4D3':
                                sku = '46BX4D3EF'
                            if sku == 'MAU-BX3D4BT':
                                sku = '46BX3D4BTEF'
                            if sku == 'MAU-OXYGENPRO25':
                                sku = '46OXYGENPRO25EF'
                            if sku == 'MAU-BX4D4BT':
                                sku = '46BX4D4BTEF'
                            if sku == 'MAU-SP1':
                                sku = '46SP1EF'
                            if sku == 'MAU-EXP':
                                sku = '46EXPEF'
                            if sku == 'MAU-AIR192X4':
                                sku = '46AIR192X4EF'
                            if sku == 'MAU-AIR192X6':
                                sku = '46AIR192X6EF'
                            if sku == 'MAU-AIRHUB':
                                sku = '46AIRXHUBEF'
                            if sku == 'MAU-AIR192X8':
                                sku = '46AIR192X8EF'
                            if sku == 'MAU-AIR192X4SPRO':
                                sku = '46AIR192X4SPROEF'
                            if sku == 'MAU-HAMMER88PRO':
                                sku = '46HAMMER88PROEF'
                            if sku == 'MAU-BX8D3':
                                sku = '46BX8D3EF'
                            if sku == 'MAU-MTRACKSOLO':
                                sku = '46MTRACKSOLOEF'
                            if sku == 'MAU-MTRACKDUO':
                                sku = '46MTRACKDUOEF'
                            if sku == 'MAU-BX3D3':
                                sku = '46BX3D3EF'
                            if sku == 'MAU-AIR192X14':
                                sku = '46AIR192X14EF'
                            if sku == 'MAU-SP2':
                                sku = '46SP2EF'
                            if sku == 'MAU-BASSTRAV':
                                sku = '46BASSTRAVELEREF'
            
            
            
                        if "ik multimedia" in brand.lower():
                            if sku == 'IK-IRIGHD2':
                                sku = 'IKMT_IP-IRIG-HD2-IN'
                            if sku == 'IK-ILOUDMM':
                                sku = 'IKMT_IP-ILOUD-MM-IN'
                            if sku == 'IK-IRIGSTREAM':
                                sku = 'IKMT_IP-IRIG-STREAM'
                            if sku == 'IK-AXEIOAT5MAXB':
                                sku = 'IKMT_CB-AXEIOAT5-HCD'
                            if sku == 'IK-IRIGPRODUOIO':
                                sku = 'IKMT_IP-IRIG-PRODUOIO'
                            if sku == 'IK-IRIG2':
                                sku = 'IKMT_IP-IRIG2-PLG-IN'
                            if sku == 'IK-IRIGPROIO':
                                sku = 'IKMT_IP-IRIG-PROIO'
                            if sku == 'IK-IRIGSTOMPIO':
                                sku = 'IKMT_IP-IRIG-STOMPIO'
                            if sku == 'IK-IRIGMICHD2':
                                sku = 'IKMT_IP-IRIG-MICHD2'
                            if sku == 'IK-AXEIO':
                                sku = 'IKMT_IP-INT-AXEIO'
                            if sku == 'IK-IRIGMIC':
                                sku = 'IKMT_IP-IRIG-MIC-IN'
                            if sku == 'IK-IRIGPREHD':
                                sku = 'IKMT_IP-IRIG-PREHD'
                            if sku == 'IK-IRIGMIDI2':
                                sku = 'IKMT_IP-IRIG-MIDI2-I'
                            if sku == 'IK-ILOUDMMW':
                                sku = 'IKMT_IP-ILOUD-MMW-IN'
                            if sku == 'IK-IRIGBLUEBOARD':
                                sku = 'IKMT_IP-IRIG-BBRD-IN'
                            if sku == 'IK-AXEIOSAT5B':
                                sku = 'IKMT_CB-AXEIOSAT5-HCD'
                            if sku == 'IK-CABLE8PIN':
                                sku = 'IKMT_IP-CABLE-8PIN-I'
                            if sku == 'IK-UNOPRODT':
                                sku = 'IKMT_IP-UNO-SYNTHPRODT'
                            if sku == 'IK-AXEIOSOLO':
                                sku = 'IKMT_IP-INT-AXEIOSOLO'
                            if sku == 'IK-IPCABLE8PCHR':
                                sku = 'IKMT_IP-CABLE-8PCHR'
                            if sku == 'IK-IRIGMICLAV2':
                                sku = 'IKMT_IP-IRIG-MICLDUA'
                            if sku == 'IK-UNOPRO':
                                sku = 'IKMT_IP-UNO-SYNTHPRO'
                            if sku == 'IK-IRIGMICSXLR':
                                sku = 'IKMT_IP-IRIG-MICSXLR'
                            if sku == 'IK-IRIGMICLAV':
                                sku = 'IKMT_IP-IRIG-MICLAV'
                            if sku == 'IK-ZTONEBB':
                                sku = 'IKMT_IP-ZTONE-BB'
                            if sku == 'IK-ZTONEDI':
                                sku = 'IKMT_IP-ZTONE-DI'
                            if sku == 'IK-IRIGVIDEOCB':
                                sku = 'IKMT_CB-MICLAVGP-HCD'
                            if sku == 'IK-IRIGNANOAMPR':
                                sku = 'IKMT_IP-NANOAMPR-IN'
                            if sku == 'IK-CABLEMD7PEX':
                                sku = 'IKMT_IP-CABLE-MD7PEX'
                            if sku == 'IK-UNODRUM':
                                sku = 'IKMT_IP-UNO-DRUM'
                            if sku == 'IK-IRIGVIDEOCHDB':
                                sku = 'IKMT_CB-MICHD2GP-HCD'
                            if sku == 'IK-IRIGCASTHD':
                                sku = 'IKMT_IP-IRIG-CASTHD'
                            if sku == 'IK-IRIGMICVIDEO':
                                sku = 'IKMT_IP-IRIG-MICVIDEO'
                            if sku == 'IK-IRIGMICVIDEOB':
                                sku = 'IKMT_CB-MICVIDEOGP-HCD'
                            if sku == 'IK-IRIGBLUETURN':
                                sku = 'IKMT_IP-IRIG-BTURN'
                            if sku == 'IK-IKLIP3':
                                sku = 'IKMT_IP-IKLIP-3'
                            if sku == 'IK-IKLIP3DLX':
                                sku = 'IKMT_IP-IKLIP-3DLX'
                            if sku == 'IK-PSU3A':
                                sku = 'IKMT_IP-PSU-CHARGER'
                            if sku == 'IK-IKLIP3VIDEO':
                                sku = 'IKMT_IP-IKLIP-3VIDEO'
                            if sku == 'IK-IKLIPGRIPRO':
                                sku = 'IKMT_IP-IKLIP-GPROB'
                            if sku == 'IK-IRIGKEYS2PRO':
                                sku = 'IKMT_IP-IRIG-KEYS2PRO'
                            if sku == 'IK-IRIGVOICEGRN':
                                sku = 'IKMT_IP-IRIG-MICVOG-'
                            if sku == 'IK-ARCSYSTEM3':
                                sku = 'IKMT_AC-300-HCD'
                            if sku == 'IK-IRIGVOICEBLUE':
                                sku = 'IKMT_IP-IRIG-MICVOB-'
                            if sku == 'IK-IRIGKEYS2':
                                sku = 'IKMT_IP-IRIG-KEYS2'
                            if sku == 'IK-UNOSYNTH':
                                sku = 'IKMT_IP-UNO-SYNTH-IN'
                            if sku == 'IK-IRIGMICROAMP':
                                sku = 'IKMT_IP-IRIG-MICROAMP'
                            if sku == 'IK-IRIGUA':
                                sku = 'IKMT_IP-IRIG-UA-IN'
                            if sku == 'IK-CABLEUSBCI':
                                sku = 'IKMT_IP-CABLE-USBC-I'
                            if sku == 'IK-BAGKEYSIO49':
                                sku = 'IKMT_BAG-IRIGKEYSI49'
                            if sku == 'IK-ILINE':
                                sku = 'IKMT_IP-ILINE-KIT-IN'
                            if sku == 'IK-XGXVIBE':
                                sku = 'IKMT_XG-PEDAL-XVIBE-IN'
                            if sku == 'IK-XGXTIME':
                                sku = 'IKMT_XG-PEDAL-XTIME-IN'
                            if sku == 'IK-IRIGKEYS2MINI':
                                sku = 'IKMT_IP-IRIG-KEYS2MINI'
                            if sku == 'IK-BAGILOUDMTM':
                                sku = 'IKMT_BAG-ILOUDMTM-0001'
                            if sku == 'IK-IRIGVOICEYLW':
                                sku = 'IKMT_IP-IRIG-MICVOY-'
                            if sku == 'IK-IRIGPADS':
                                sku = 'IKMT_IP-IRIG-PADS-IN'
                            if sku == 'IK-IRIGNANOAMPW':
                                sku = 'IKMT_IP-NANOAMPW-IN'
                            if sku == 'IK-IRIGCAST2':
                                sku = 'IKMT_IP-IRIG-CAST2'
                            if sku == 'IK-25CABLEMIDI':
                                sku = 'IKMT_IP-CABLE-MIDI'
                            if sku == 'IK-IKLIPGO':
                                sku = 'IKMT_IP-IKLIP-GO-IN'
                            if sku == 'IK-BAGKEYSIO25':
                                sku = 'IKMT_BAG-IRIGKEYSI25'
                            if sku == 'IK-CABLE30PIN':
                                sku = 'IKMT_IP-CABLE-30PIN'
                            if sku == 'IK-CABLE30PUSB':
                                sku = 'IKMT_IP-CABLE-30PUSB'
                            if sku == 'IK-ILINEDSLR':
                                sku = 'IKMT_IP-ILINE-DSLR-I'
                            if sku == 'IK-IRIGKEYSIOMIC':
                                sku = 'IKMT_IP-MIC-GSNK-IN'
                            if sku == 'IK-IRIGMICSTBL':
                                sku = 'IKMT_IP-IRIG-MICSTBL'
                            if sku == 'IK-IRIGQTRDLX':
                                sku = 'IKMT_IP-IRIG-QTRDLX-IN'
                            if sku == 'IK-IRIGPRE2':
                                sku = 'IKMT_IP-IRIG-PRE2'
                            if sku == 'IK-IRIGKEYIO25':
                                sku = 'IKMT_IP-IRIG-KEYIO25'
                            if sku == 'IK-CABLE8PMUSB':
                                sku = 'IKMT_IP-CABLE-8PMUSB'
                            if sku == 'IK-CABLEUSBCMD':
                                sku = 'IKMT_IP-CABLE-USBCMD'
                            if sku == 'IK-IRIGVOICEWHT':
                                sku = 'IKMT_IP-IRIG-MICVOW-'
                            if sku == 'IK-IRIGVOICEPINK':
                                sku = 'IKMT_IP-IRIG-MICVOP-'
                            if sku == 'IK-IRIGKEYIO49':
                                sku = 'IKMT_IP-IRIG-KEYIO49'
                            if sku == 'IK-XGXSPACE':
                                sku = 'IKMT_XG-PEDAL-XSPACE-IN'
                            if sku == 'IK-BAGILOUDMM':
                                sku = 'IKMT_BAG-ILOUDMM-001'
                            if sku == 'IK-XGXDRIVE':
                                sku = 'IKMT_XG-PEDAL-XDRIVE-IN'
                            if sku == 'IK-IKLIPXPAND':
                                sku = 'IKMT_IP-IKLIP-XPAND-'
                            if sku == 'IK-IKLIPXPANDM':
                                sku = 'IKMT_IP-IKLIP-XPANDM'
                            if sku == 'IK-IRIGQUATTRO':
                                sku = 'IKMT_IP-IRIG-QUATTRO-IN'
                            if sku == 'IK-IRIGSTREAMMP':
                                sku = 'IKMT_IP-IRIG-STRMMICPRO-IN'
                            if sku == 'IK-ILOUDP5':
                                sku = 'IKMT_MON-PRECISION-500-IN'
                            if sku == 'IK-ILOUDP6':
                                sku = 'IKMT_MON-PRECISION-650-IN'
            
            
            
            
                        if "samson" in brand.lower():
                            if sku == 'SAM-PATCHPLUS':
                                sku = '29SPATCH-PLUSEF'
                            if sku == 'SAM-XP106W':
                                sku = '29XP106WEF'
                            if sku == 'SAM-PS01':
                                sku = '29PS01EF'
                            if sku == 'SAM-XP106':
                                sku = '29XP106EF'
                            if sku == 'SAM-XPD2HEADSET':
                                sku = '14XPD2-HEADSETEF'
                            if sku == 'SAM-Q2UPACK':
                                sku = '29Q2U-PACKEF'
                            if sku == 'SAM-XPD2PRES':
                                sku = '14XPD2-PRESEF'
                            if sku == 'SAM-Q9U':
                                sku = '29Q9UEF'
                            if sku == 'SAM-MBA38':
                                sku = '29MBA38EF'
                            if sku == 'SAM-MD5':
                                sku = '29MD5EF'
                            if sku == 'SAM-SP01':
                                sku = '29SP01EF'
                            if sku == 'SAM-GOMIC':
                                sku = '29GOMICEF'
                            if sku == 'SAM-METEOR':
                                sku = '29METEOREF'
                            if sku == 'SAM-LTS50':
                                sku = '29LTS50EF'
                            if sku == 'SAM-SRK12':
                                sku = '29SRK12EF'
                            if sku == 'SAM-SRK16':
                                sku = '29SRK16EF'
                            if sku == 'SAM-SRK8':
                                sku = '29SRK8EF'
                            if sku == 'SAM-SRK21':
                                sku = '29SRK21EF'
                            if sku == 'SAM-DE60X':
                                sku = '14DE60XEF'
                            if sku == 'SAM-XPD2MHS':
                                sku = '14XPDM-HEADSETEF'
                            if sku == 'SAM-MEDIATRACK':
                                sku = '29MEDIATRACKEF'
                            if sku == 'SAM-CON288MPRESD':
                                sku = '14CON288M-PRES-DEF'
                            if sku == 'SAM-XPD2':
                                sku = '14XPD2EF'
                            if sku == 'SAM-MD2PRO':
                                sku = '29MD2PROEF'
                            if sku == 'SAM-XP1000':
                                sku = '29XP1000EF'
                            if sku == 'SAM-CON288MALLD':
                                sku = '14CON288M-ALL-DEF'
                            if sku == 'SAM-CM20P':
                                sku = '29CM20PEF'
                            if sku == 'SAM-GTRACKPRO':
                                sku = '29GTRACKPROEF'
                            if sku == 'SAM-C01UPRO':
                                sku = '29C01UPROEF'
                            if sku == 'SAM-GOMOBILEL':
                                sku = '14GOMOBILE-LEF'
                            if sku == 'SAM-MEDIAONEBT3':
                                sku = '29MEDIAONEBTAEF'
                            if sku == 'SAM-MDA1':
                                sku = '29MDA1EF'
                            if sku == 'SAM-MD1':
                                sku = '29MD1EF'
                            if sku == 'SAM-AWXM':
                                sku = '14AIR99M-WINDEF'
                            if sku == 'SAM-SRKS1':
                                sku = '29SRKS1EF'
                            if sku == 'SAM-CM15P':
                                sku = '29CM15PEF'
                            if sku == 'SAM-DEU1':
                                sku = '29DEU1EF'
                            if sku == 'SAM-GOMOBILEH':
                                sku = '14GOMOBILE-HEF'
                            if sku == 'SAM-SATELLITE':
                                sku = '29SATELLITEEF'
                            if sku == 'SAM-XP208W':
                                sku = '29XP208WEF'
                            if sku == 'SAM-SERVO120':
                                sku = '29SERVO120EF'
                            if sku == 'SAM-CON88PRES':
                                sku = '14CON88-PRESEF'
                            if sku == 'SAM-SZONE':
                                sku = '29SZONEEF'
                            if sku == 'SAM-XPD2MHH':
                                sku = '14XPD2M-HANDHELDEF'
                            if sku == 'SAM-DR2U':
                                sku = '29SRKD2EF'
                            if sku == 'SAM-SRKS2U':
                                sku = '29SRKS2EF'
                            if sku == 'SAM-SRKD4':
                                sku = '29SRKD4EF'
                            if sku == 'SAM-MEDIAONEBT4':
                                sku = '29MEDIAONEBT4EF'
                            if sku == 'SAM-RESOLVSE5':
                                sku = '29RESOLVSEA5EF'
                            if sku == 'SAM-RESOLVSE6':
                                sku = '29RESOLVSEA6EF'
                            if sku == 'SAM-RESOLVSE8':
                                sku = '29RESOLVSEA8EF'
                            if sku == 'SAM-SPHONE':
                                sku = '29/SPHONEEF'
                            if sku == 'SAM-XPDC208':
                                sku = '29XPDC208EF'
            
            
            
            
                        if "evans" in brand.lower():
                            sku = sku.replace('EVA-', '')
            
                        if "crown" in brand.lower():
                            sku = sku.replace('CRO-', 'CROWN-')
                            sku = f'{sku}CMI'
            
                        if "tascam" in brand.lower():
                            sku = sku.replace('TAS-', '')
                            if sku == 'MODEL12':
                                sku = 'MODEL-12'
                            if sku == 'MODEL24':
                                sku = 'MODEL-24'
                            if sku == 'DP006':
                                sku = 'DP-006'
                            if sku == 'DP008EX':
                                sku = 'DP-008EX'
                            if sku == 'TA1VP':
                                sku = 'TA-1VP'
                            if sku == 'SERIES8PDYNA':
                                sku = 'SERIES-8PDYNA'
                            if sku == 'US16X08':
                                sku = 'US-16X08'
                            if sku == 'DR70D':
                                sku = 'DR-70D'
                            if sku == 'SERIES102I':
                                sku = 'SERIES-102I'
                            if sku == 'SERIES208I':
                                sku = 'SERIES-208I'
                            if sku == 'DR10CH':
                                sku = 'DR-10CH'
                            if sku == 'RC3F':
                                sku = 'RC-3F'
                            if sku == 'MODEL16':
                                sku = 'MODEL-16'
                            if sku == 'DR44WL':
                                sku = 'DR-44WL'
                            if sku == 'DP32SD':
                                sku = 'DP-32SD'
                            if sku == 'WS11':
                                sku = 'WS-11'
                            if sku == 'DR701D':
                                sku = 'DR-701D'
                            if sku == 'DR60DMK2':
                                sku = 'DR-60DMK2'
                            if sku == 'DR680MK2':
                                sku = 'DR-680MK2'
                            if sku == 'DR10L':
                                sku = 'DR-10L'
                            if sku == 'HS20':
                                sku = 'HS-20'
                            if sku == 'DR22WL':
                                sku = 'DR-22WL'
                            if sku == 'RC1F':
                                sku = 'RC-1F'
                            if sku == 'DR10LW':
                                sku = 'DR-10LW'
                            if sku == 'CD6010':
                                sku = 'CD-6010'
                            if sku == 'MX8A':
                                sku = 'MX-8A'
                            if sku == 'LM8ST':
                                sku = 'LM-8ST'
                            if sku == 'MZ123BT':
                                sku = 'MZ-123BT'
                            if sku == 'DA6400':
                                sku = 'DA-6400'
                            if sku == 'BO32DE':
                                sku = 'BO-32DE'
                            if sku == 'AKDR1':
                                sku = 'AK-DR1'
                            if sku == 'RC10':
                                sku = 'RC-10'
                            if sku == 'DR10SG':
                                sku = 'DR-10SG'
                            if sku == 'US20X20':
                                sku = 'US-20X20'
                            if sku == 'ML32D':
                                sku = 'ML-32D'
                            if sku == 'MH8':
                                sku = 'MH-8'
                            if sku == 'TG7':
                                sku = 'TG-7'
                            if sku == 'CSMODEL12':
                                sku = 'CSMODEL-12'
                            if sku == 'CSDR2':
                                sku = 'CSDR-2'
                            if sku == 'DR40X':
                                sku = 'DR-40X'
                            if sku == 'DR05X':
                                sku = 'DR-05X'
                            if sku == 'CDA580':
                                sku = 'CDA-580'
                            if sku == 'DP24SD':
                                sku = 'DP-24SD'
                            if sku == 'DP03SD':
                                sku = 'DP-03SD'
                            if sku == 'DR07X':
                                sku = 'DR-07X'
                            if sku == 'AKDR70C':
                                sku = 'AK-DR70C'
                            if sku == 'DR10X':
                                sku = 'DR-10X'
                            if sku == 'CD400U':
                                sku = 'CD-400U'
                            if sku == 'AKDR11C':
                                sku = 'AK-DR11C'
                            if sku == 'TM2X':
                                sku = 'TM-2X'
                            if sku == 'DR10CS':
                                sku = 'DR-10CS'
                            if sku == 'SSCDR250N':
                                sku = 'SSCDR-250N'
                            if sku == 'TMAR1':
                                sku = 'TMAR-1'
                            if sku == 'CSDR680':
                                sku = 'CSDR-680'
            
            
                            sku = f'{sku}CMI'
            
                        if "beale" in brand.lower():
            
                            if sku == 'BEA-DP300':
                                sku = '830510AUSTRALIS'
                            if sku == 'BEA-DPSTAND':
                                sku = '830516AUSTRALIS'
                            if sku == 'BEA-AK280':
                                sku = '841024AUSTRALIS'
            
                        if "ghs" in brand.lower():
            
                            if sku == 'GHS-FASTFRET':
                                sku = '751008AUSTRALIS'
                            if sku == 'GHS-M3045':
                                sku = '751156AUSTRALIS'
                            if sku == 'GHS-GBL':
                                sku = '751080AUSTRALIS'
                            if sku == 'GHS-GBM':
                                sku = '751085AUSTRALIS'
                            if sku == 'GHS-GBXL':
                                sku = '751073AUSTRALIS'
                            if sku == 'GHS-ML3045':
                                sku = '751155AUSTRALIS'
                            if sku == 'GHS-S315':
                                sku = '751255AUSTRALIS'
                            if sku == 'GHS-GBCL':
                                sku = '751078AUSTRALIS'
                            if sku == 'GHS-GBL8':
                                sku = '752950AUSTRALIS'
                            if sku == 'GHS-GB7L':
                                sku = '751095AUSTRALIS'
                            if sku == 'GHS-DYL':
                                sku = '751090AUSTRALIS'
                            if sku == 'GHS-GBH':
                                sku = '751088AUSTRALIS'
                            if sku == 'GHS-6MLDYB':
                                sku = '751169AUSTRALIS'
                            if sku == 'GHS-S335':
                                sku = '751259AUSTRALIS'
                            if sku == 'GHS-GBUL':
                                sku = '751071AUSTRALIS'
                            if sku == 'GHS-S325':
                                sku = '751256AUSTRALIS'
                            if sku == 'GHS-M30505':
                                sku = '751224AUSTRALIS'
                            if sku == 'GHS-M72005':
                                sku = '751209AUSTRALIS'
                            if sku == 'GHS-M7200':
                                sku = '751208AUSTRALIS'
                            if sku == 'GHS-ML7200':
                                sku = '751207AUSTRALIS'
                            if sku == 'GHS-710':
                                sku = '751142AUSTRALIS'
                            if sku == 'GHS-5MDYB':
                                sku = '751168AUSTRALIS'
                            if sku == 'GHS-5MLDYB':
                                sku = '751167AUSTRALIS'
                            if sku == 'GHS-L7200':
                                sku = '751206AUSTRALIS'
            
            
            
                        if "x-vive" in brand.lower():
            
                            if sku == 'XV-U2WOOD':
                                sku = '352445AUSTRALIS'
                            if sku == 'XV-U2CARBON':
                                sku = '352444AUSTRALIS'
                            if sku == 'XV-P1':
                                sku = '352446AUSTRALIS'
                            if sku == 'XV-MD1':
                                sku = '352447AUSTRALIS'
                            if sku == 'XV-U2TBK':
                                sku = '352337AUSTRALIS'
                            if sku == 'XV-U4':
                                sku = '352565AUSTRALIS'
                            if sku == 'XV-U3':
                                sku = '352555AUSTRALIS'
                            if sku == 'XV-U2BLACK':
                                sku = '352333AUSTRALIS'
                            if sku == 'XV-U4R2':
                                sku = '352568AUSTRALIS'
                            if sku == 'XV-U4R4':
                                sku = '352569AUSTRALIS'
                            if sku == 'XV-U3C':
                                sku = '352559AUSTRALIS'
                            if sku == 'XV-U4T':
                                sku = '352566AUSTRALIS'
                            if sku == 'XV-U2SUNBURST':
                                sku = '352335AUSTRALIS'
                            if sku == 'XV-U2RBK':
                                sku = '352339AUSTRALIS'
                            if sku == 'XV-U5T2':
                                sku = '352572AUSTRALIS'
                            if sku == 'XV-V21':
                                sku = '352563AUSTRALIS'
                            if sku == 'XV-U3R':
                                sku = '352558AUSTRALIS'
                            if sku == 'XV-U3T':
                                sku = '352556AUSTRALIS'
                            if sku == 'XV-U5C':
                                sku = '352573AUSTRALIS'
                            if sku == 'XV-U5':
                                sku = '352571AUSTRALIS'
                            if sku == 'XV-H2':
                                sku = '352583AUSTRALIS'
                            if sku == 'XV-U5T':
                                sku = '352574AUSTRALIS'
                            if sku == 'XV-U6':
                                sku = '352581AUSTRALIS'
                            if sku == 'XV-LV1':
                                sku = '352576AUSTRALIS'
                            if sku == 'XV-LV2':
                                sku = '352577AUSTRALIS'
                            if sku == 'XV-U5R':
                                sku = '352575AUSTRALIS'
            
            
                        if "armour" in brand.lower():
            
                            if sku == 'ARM-ARMUNOW':
                                sku = '604215'
                            if sku == 'ARM-KS75':
                                sku = '208105'
                            if sku == 'ARM-ARMUNOB':
                                sku = '604212'
                            if sku == 'ARM-KSD98D':
                                sku = '208100'
                            if sku == 'ARM-KBBL':
                                sku = '604197'
                            if sku == 'ARM-ARMUNOC':
                                sku = '604217'
                            if sku == 'ARM-KBBS':
                                sku = '604191'
                            if sku == 'ARM-APCTWD':
                                sku = '701245'
                            if sku == 'ARM-KBBXL':
                                sku = '604199'
                            if sku == 'ARM-KBBM':
                                sku = '604193'
                            if sku == 'ARM-APCW12':
                                sku = '701205'
                            if sku == 'ARM-UWM1':
                                sku = '208025'
                            if sku == 'ARM-ARM2000G':
                                sku = '604153'
                            if sku == 'ARM-APCES':
                                sku = '701235'
                            if sku == 'ARM-KBBMW':
                                sku = '604195'
                            if sku == 'ARM-APUCC':
                                sku = '701275'
                            if sku == 'ARM-240C':
                                sku = '604188'
                            if sku == 'ARM-200S':
                                sku = '604186'
                            if sku == 'ARM-GWM5':
                                sku = '208015'
                            if sku == 'ARM-180T':
                                sku = '604184'
                            if sku == 'ARM-ARM350W':
                                sku = '604102'
                            if sku == 'ARM-APUCS':
                                sku = '701280'
                            if sku == 'ARM-MS100SA':
                                sku = '208155'
                            if sku == 'ARM-MSB150B':
                                sku = '208175'
                            if sku == 'ARM-CCP10':
                                sku = '813225'
                            if sku == 'ARM-CCP3':
                                sku = '813220'
                            if sku == 'ARM-MSB250':
                                sku = '208170'
                            if sku == 'ARM-CCP20':
                                sku = '813230'
                            if sku == 'ARM-CCP30':
                                sku = '813235'
                            if sku == 'ARM-ARMUNOG':
                                sku = '604210'
                            if sku == 'ARM-ARM2000W':
                                sku = '604157'
                            if sku == 'ARM-ARM350JNR':
                                sku = '604106'
                            if sku == 'ARM-ARM350JJR':
                                sku = '604107'
                            if sku == 'ARM-NXXP10':
                                sku = '813515'
                            if sku == 'ARM-NXXP20':
                                sku = '813520'
            
                            sku = sku.replace('ARM-', '')
            
                            sku = f'{sku}AUSTRALIS'
            
                        if "gator" in brand.lower():
            
                            if sku == 'GAT-KC1648':
                                sku = '488228AUSTRALIS'
                            if sku == 'GAT-KC1540':
                                sku = '488227AUSTRALIS'
                            if sku == 'GAT-GKB61SLIM':
                                sku = '488217AUSTRALIS'
                            if sku == 'GAT-GPG88SLIMXL':
                                sku = '488237AUSTRALIS'
                            if sku == 'GAT-GLROADCAST4':
                                sku = '488919AUSTRALIS'
                            if sku == 'GAT-GPATOTE12':
                                sku = '488329AUSTRALIS'
                            if sku == 'GAT-GFWGTR2000':
                                sku = '488398AUSTRALIS'
                            if sku == 'GAT-GTSAKEY76':
                                sku = '488245AUSTRALIS'
                            if sku == 'GAT-GTSAKEY88D':
                                sku = '488248AUSTRALIS'
                            if sku == 'GAT-GMULTIFX2411':
                                sku = '488108AUSTRALIS'
                            if sku == 'GAT-GTSAGTRLPS':
                                sku = '488143AUSTRALIS'
                            if sku == 'GAT-GINEAR':
                                sku = '488339AUSTRALIS'
                            if sku == 'GAT-GKB61':
                                sku = '488216AUSTRALIS'
                            if sku == 'GAT-GTSAGTRSG':
                                sku = '488144AUSTRALIS'
                            if sku == 'GAT-GK76SLIM':
                                sku = '488210AUSTRALIS'
                            if sku == 'GAT-GTRFRETMUTES':
                                sku = '488940AUSTRALIS'
                            if sku == 'GAT-HPHANGERDESK':
                                sku = '488912AUSTRALIS'
                            if sku == 'GAT-GCELECADLX':
                                sku = '488088AUSTRALIS'
                            if sku == 'GAT-GTRFRETMUTEM':
                                sku = '488939AUSTRALIS'
                            if sku == 'GAT-GTRFRETMUTEL':
                                sku = '488938AUSTRALIS'
                            if sku == 'GAT-GTRFRETMUTEX':
                                sku = '488941AUSTRALIS'
                            if sku == 'GAT-GFWELIDESKBR':
                                sku = '488933AUSTRALIS'
                            if sku == 'GAT-MICBCBM3000':
                                sku = '488944AUSTRALIS'
                            if sku == 'GAT-GLCDTOTESM':
                                sku = '488901AUSTRALIS'
                            if sku == 'GAT-SPKSTMNDSK':
                                sku = '488907AUSTRALIS'
                            if sku == 'GAT-GGR6L':
                                sku = '488501AUSTRALIS'
                            if sku == 'GAT-MICBCBM4000':
                                sku = '488943AUSTRALIS'
                            if sku == 'GAT-GRSTUDIO4U':
                                sku = '488513AUSTRALIS'
                            if sku == 'GAT-GFWMIC0501':
                                sku = '488946AUSTRALIS'
                            if sku == 'GAT-LAPTOP2500':
                                sku = '488952AUSTRALIS'
                            if sku == 'GAT-ESPKSTMNMPL':
                                sku = '488951AUSTRALIS'
                            if sku == 'GAT-ESIDECARMPL':
                                sku = '488976AUSTRALIS'
                            if sku == 'GAT-ESIDECARBRN':
                                sku = '488975AUSTRALIS'
                            if sku == 'GAT-GR6L':
                                sku = '488478AUSTRALIS'
                            if sku == 'GAT-GMIXB2020':
                                sku = '488272AUSTRALIS'
                            if sku == 'GAT-GRRACKBAG3UW':
                                sku = '488508AUSTRALIS'
                            if sku == 'GAT-GFWEDCRNRBR':
                                sku = '488934AUSTRALIS'
                            if sku == 'GAT-ESPKSTMNGRY':
                                sku = '488950AUSTRALIS'
                            if sku == 'GAT-GFWIDCTVEA':
                                sku = '488972AUSTRALIS'
                            if sku == 'GAT-GFWIDCT31T':
                                sku = '488965AUSTRALIS'
                            if sku == 'GAT-MICACCTRAYXL':
                                sku = '488868AUSTRALIS'
                            if sku == 'GAT-MIXERBAG1306':
                                sku = '488268AUSTRALIS'
                            if sku == 'GAT-MICCAMERAMT':
                                sku = '488945AUSTRALIS'
                            if sku == 'GAT-GFWMICSM1855':
                                sku = '488947AUSTRALIS'
                            if sku == 'GAT-GMIXB3621':
                                sku = '488766AUSTRALIS'
                            if sku == 'GAT-GFWIDCTLD15A':
                                sku = '488970AUSTRALIS'
                            if sku == 'GAT-ESIDECARGRY':
                                sku = '488979AUSTRALIS'
                            if sku == 'GAT-GLRODECAST2':
                                sku = '488918AUSTRALIS'
                            if sku == 'GAT-GFWIDCT':
                                sku = '488963AUSTRALIS'
                            if sku == 'GAT-GFWEDCNRMP':
                                sku = '488931AUSTRALIS'
                            if sku == 'GAT-GFWIDCT41CB':
                                sku = '488966AUSTRALIS'
                            if sku == 'GAT-LAPTOP1000':
                                sku = '488953AUSTRALIS'
                            if sku == 'GAT-MICBCBM1000':
                                sku = '488942AUSTRALIS'
                            if sku == 'GAT-MICBCBM2000':
                                sku = '488906AUSTRALIS'
                            if sku == 'GAT-GPATRNSPRTLG':
                                sku = '488304AUSTRALIS'
                            if sku == 'GAT-GFWIDCTCW6PK':
                                sku = '488967AUSTRALIS'
                            if sku == 'GAT-GMIXB1818':
                                sku = '488271AUSTRALIS'
                            if sku == 'GAT-ESPKSTMNBLK':
                                sku = '488948AUSTRALIS'
                            if sku == 'GAT-ESPKSTMNBRN':
                                sku = '488949AUSTRALIS'
                            if sku == 'GAT-GFWDESKCRN':
                                sku = '488925AUSTRALIS'
                            if sku == 'GAT-GFWIDCT26T':
                                sku = '488964AUSTRALIS'
                            if sku == 'GAT-GFWIDCTCM':
                                sku = '488968AUSTRALIS'
                            if sku == 'GAT-GFWIDCTDM':
                                sku = '488969AUSTRALIS'
                            if sku == 'GAT-GFWIDCTRL':
                                sku = '488971AUSTRALIS'
                            if sku == 'GAT-GFWIDCTVM':
                                sku = '488973AUSTRALIS'
                            if sku == 'GAT-GMIX19X21':
                                sku = '488260AUSTRALIS'
                            if sku == 'GAT-GMIX20X30':
                                sku = '488262AUSTRALIS'
                            if sku == 'GAT-GMIXB3121':
                                sku = '488765AUSTRALIS'
                            if sku == 'GAT-GPG49':
                                sku = '488230AUSTRALIS'
                            if sku == 'GAT-GTOUR12U':
                                sku = '488594AUSTRALIS'
                            if sku == 'GAT-GTOURM32W':
                                sku = '488286AUSTRALIS'
                            if sku == 'GAT-MIX222506':
                                sku = '488302AUSTRALIS'
                            if sku == 'GAT-GK2110':
                                sku = '488205AUSTRALIS'
                            if sku == 'GAT-GCPK88TSA':
                                sku = '488247AUSTRALIS'
                            if sku == 'GAT-GCPK61TSA':
                                sku = '488244AUSTRALIS'
                            if sku == 'GAT-TSA88KEYSLXL':
                                sku = '488250AUSTRALIS'
                            if sku == 'GAT-GCPK88SLIMTS':
                                sku = '488249AUSTRALIS'
                            if sku == 'GAT-GK88SLIM':
                                sku = '488221AUSTRALIS'
                            if sku == 'GAT-GTOURAMP112':
                                sku = '488126AUSTRALIS'
                            if sku == 'GAT-GKB88SLIM':
                                sku = '488221AUSTRALIS'
                            if sku == 'GAT-GWEELECWIDE':
                                sku = '488156AUSTRALIS'
                            if sku == 'GAT-GCGK49':
                                sku = '488206AUSTRALIS'
                            if sku == 'GAT-GPG76SLIM':
                                sku = '488234AUSTRALIS'
                            if sku == 'GAT-GKB76':
                                sku = '488218AUSTRALIS'
                            if sku == 'GAT-GPG76':
                                sku = '488233AUSTRALIS'
                            if sku == 'GAT-GKB88SLXL':
                                sku = '488222AUSTRALIS'
                            if sku == 'GAT-GTSAKEY76D':
                                sku = '488246AUSTRALIS'
                            if sku == 'GAT-GCELECXL':
                                sku = '488089AUSTRALIS'
                            if sku == 'GAT-RETRORACK3SG':
                                sku = '488924AUSTRALIS'
                            if sku == 'GAT-GCGKB49':
                                sku = '488215AUSTRALIS'
                            if sku == 'GAT-GCP-K49-TSA':
                                sku = '488243AUSTRALIS'
                            if sku == 'GAT-GMULTIFX1510':
                                sku = '488107AUSTRALIS'
                            if sku == 'GAT-GWSGBROWN':
                                sku = '488180AUSTRALIS'
                            if sku == 'GAT-GK88XL':
                                sku = '488214AUSTRALIS'
                            if sku == 'GAT-GWETBIRD':
                                sku = '488162AUSTRALIS'
                            if sku == 'GAT-GFWCOSMS':
                                sku = '488908AUSTRALIS'
                            if sku == 'GAT-GFWEDESKMP':
                                sku = '488930AUSTRALIS'
                            if sku == 'GAT-GPATOTE8':
                                sku = '488331AUSTRALIS'
                            if sku == 'GAT-GFWDKMAIN':
                                sku = '488926AUSTRALIS'
                            if sku == 'GAT-GPATOTE15':
                                sku = '488330AUSTRALIS'
                            if sku == 'GAT-GRR8L':
                                sku = '488503AUSTRALIS'
                            if sku == 'GAT-GRR10L':
                                sku = '488497AUSTRALIS'
                            if sku == 'GAT-GPATOTE10':
                                sku = '488328AUSTRALIS'
                            if sku == 'GAT-GLCDTOTEMD':
                                sku = '488628AUSTRALIS'
                            if sku == 'GAT-GFWELEDRKMP':
                                sku = '488932AUSTRALIS'
                            if sku == 'GAT-GR4S':
                                sku = '488477AUSTRALIS'
                            if sku == 'GAT-GFWEEDESKRBR':
                                sku = '488935AUSTRALIS'
                            if sku == 'GAT-GR4L':
                                sku = '488476AUSTRALIS'
                            if sku == 'GAT-GMIXB1515':
                                sku = '488269AUSTRALIS'
                            if sku == 'GAT-GLCDTOTELGX2':
                                sku = '488864AUSTRALIS'
                            if sku == 'GAT-GFWSHELF1115':
                                sku = '488917AUSTRALIS'
                            if sku == 'GAT-GCGPA712SM':
                                sku = '488308AUSTRALIS'
                            if sku == 'GAT-GMIXB2118':
                                sku = '488273AUSTRALIS'
                            if sku == 'GAT-GCGPA715':
                                sku = '488309AUSTRALIS'
                            if sku == 'GAT-GR2S':
                                sku = '488474AUSTRALIS'
                            if sku == 'GAT-GPG61':
                                sku = '488231AUSTRALIS'
                            if sku == 'GAT-GRCBASE14':
                                sku = '488494AUSTRALIS'
                            if sku == 'GAT-GMIX12':
                                sku = '488265AUSTRALIS'
                            if sku == 'GAT-GCPM15TSA':
                                sku = '488354AUSTRALIS'
                            if sku == 'GAT-GUEVA28164':
                                sku = '488365AUSTRALIS'
                            if sku == 'GAT-GMIXB1815':
                                sku = '488270AUSTRALIS'
                            if sku == 'GAT-GMIXB1212':
                                sku = '488267AUSTRALIS'
                            if sku == 'GAT-GR6S':
                                sku = '488479AUSTRALIS'
                            if sku == 'GAT-GFWSHELF0909':
                                sku = '488916AUSTRALIS'
                            if sku == 'GAT-GCLUBC27BP':
                                sku = '488376AUSTRALIS'
                            if sku == 'GAT-GCGPA712LG':
                                sku = '488307AUSTRALIS'
                            if sku == 'GAT-GRSTUDIO8U':
                                sku = '488514AUSTRALIS'
                            if sku == 'GAT-GMIXL1618A':
                                sku = '488276AUSTRALIS'
                            if sku == 'GAT-MICQRTOP':
                                sku = '488903AUSTRALIS'
                            if sku == 'GAT-GMIXB2621':
                                sku = '488764AUSTRALIS'
                            if sku == 'GAT-GRB2U':
                                sku = '488481AUSTRALIS'
                            if sku == 'GAT-GRRACKBAG4UW':
                                sku = '488510AUSTRALIS'
                            if sku == 'GAT-MIX192108':
                                sku = '488299AUSTRALIS'
                            if sku == 'GAT-GBAM12B':
                                sku = '488340AUSTRALIS'
                            if sku == 'GAT-GCPM30TSA':
                                sku = '488355AUSTRALIS'
                            if sku == 'GAT-GLCDTOTELG':
                                sku = '488627AUSTRALIS'
                            if sku == 'GAT-GPA777':
                                sku = '488310AUSTRALIS'
                            if sku == 'GAT-GMIX20X25':
                                sku = '488261AUSTRALIS'
                            if sku == 'GAT-488157':
                                sku = '488157AUSTRALIS'
                            if sku == 'GAT-GK88SLXL':
                                sku = '488213AUSTRALIS'
                            if sku == 'GAT-GKBE49':
                                sku = '488223AUSTRALIS'
                            if sku == 'GAT-GKBE76':
                                sku = '488225AUSTRALIS'
                            if sku == 'GAT-GMDUALW':
                                sku = '488922AUSTRALIS'
                            if sku == 'GAT-GMIX24X36':
                                sku = '488264AUSTRALIS'
                            if sku == 'GAT-GMIXL':
                                sku = '488278AUSTRALIS'
                            if sku == 'GAT-GRRACKBAG2UW':
                                sku = '488506AUSTRALIS'
                            if sku == 'GAT-GTOUREFX4':
                                sku = '488604AUSTRALIS'
                            if sku == 'GAT-GTOURM32RNDH':
                                sku = '488895AUSTRALIS'
                            if sku == 'GAT-GTRX32CMPCTW':
                                sku = '488288AUSTRALIS'
            
            
            
                        if "ibanez" in brand.lower():
            
                            if sku == 'IBA-PIA3761SLW':
                                sku = '6043130AUSTRALIS'
                            if sku == 'IBA-IGC10':
                                sku = '4716006AUSTRALIS'
                            if sku == 'IBA-PIA3761XB':
                                sku = '6043295AUSTRALIS'
                            if sku == 'IBA-RGR131EXBKF':
                                sku = '6043226AUSTRALIS'
                            if sku == 'IBA-TS9':
                                sku = '47046AUSTRALIS'
                            if sku == 'IBA-AW54CE':
                                sku = '1000406AUSTRALIS'
                            if sku == 'IBA-RG370AHMZ':
                                sku = '9300266AUSTRALIS'
                            if sku == 'IBA-ICHI10VWM':
                                sku = '6043338AUSTRALIS'
                            if sku == 'IBA-M300C':
                                sku = '9300229AUSTRALIS'
                            if sku == 'IBA-RG631ALFBCM':
                                sku = '6043197AUSTRALIS'
                            if sku == 'IBA-AZ2204HRM':
                                sku = '6043007AUSTRALIS'
                            if sku == 'IBA-RG5320CDFM':
                                sku = '6043189AUSTRALIS'
                            if sku == 'IBA-RGR221PAAQB':
                                sku = '6043228AUSTRALIS'
                            if sku == 'IBA-RGA742FMTGF':
                                sku = '6043200AUSTRALIS'
                            if sku == 'IBA-RGMS7':
                                sku = '6042750AUSTRALIS'
                            if sku == 'IBA-TSMINI':
                                sku = '4600275AUSTRALIS'
                            if sku == 'IBA-GA5TCE':
                                sku = '4950120AUSTRALIS'
                            if sku == 'IBA-QX52BKF':
                                sku = '6043312AUSTRALIS'
                            if sku == 'IBA-XPTB720BKF':
                                sku = '6043303AUSTRALIS'
                            if sku == 'IBA-PF12MHCEOPN':
                                sku = '6042654AUSTRALIS'
                            if sku == 'IBA-ICGC10W':
                                sku = '6043065AUSTRALIS'
                            if sku == 'IBA-JIVA10DSB':
                                sku = '6042769AUSTRALIS'
                            if sku == 'IBA-XPTB620BKF':
                                sku = '6043302AUSTRALIS'
                            if sku == 'IBA-RG131DXBKF':
                                sku = '6042902AUSTRALIS'
                            if sku == 'IBA-ICC10':
                                sku = '9300234AUSTRALIS'
                            if sku == 'IBA-Q54BKF':
                                sku = '6043308AUSTRALIS'
                            if sku == 'IBA-RG5170BBK':
                                sku = '6043238AUSTRALIS'
                            if sku == 'IBA-TMB100MGR':
                                sku = '6042577AUSTRALIS'
                            if sku == 'IBA-RG421HPAHBWB':
                                sku = '6043037AUSTRALIS'
                            if sku == 'IBA-RG170DXLBKN':
                                sku = '6043071AUSTRALIS'
                            if sku == 'IBA-AZES40MGR':
                                sku = '6043341AUSTRALIS'
                            if sku == 'IBA-JEMJRWH':
                                sku = '4600224AUSTRALIS'
                            if sku == 'IBA-RGA42FMBLF':
                                sku = '9300253AUSTRALIS'
                            if sku == 'IBA-BIGMINI':
                                sku = '9300223AUSTRALIS'
                            if sku == 'IBA-AZES40PRB':
                                sku = '6043339AUSTRALIS'
                            if sku == 'IBA-SR300EBWK':
                                sku = '6042859AUSTRALIS'
                            if sku == 'IBA-AEG50BK':
                                sku = '6043094AUSTRALIS'
                            if sku == 'IBA-RG121DXLWNF':
                                sku = '6043227AUSTRALIS'
                            if sku == 'IBA-RG121DXBKF':
                                sku = '6042903AUSTRALIS'
                            if sku == 'IBA-RGA42FM':
                                sku = '9300254AUSTRALIS'
                            if sku == 'IBA-RG7221QATKS':
                                sku = '6043073AUSTRALIS'
                            if sku == 'IBA-RGMS8BK':
                                sku = '6042751AUSTRALIS'
                            if sku == 'IBA-TMB30IV':
                                sku = '6042869AUSTRALIS'
                            if sku == 'IBA-RG80FIPT':
                                sku = '6043257AUSTRALIS'
                            if sku == 'IBA-RG8570ZBRE':
                                sku = '6043452AUSTRALIS'
                            if sku == 'IBA-RGRT421WK':
                                sku = '6042682AUSTRALIS'
                            if sku == 'IBA-GB10SEFMSRR':
                                sku = '6043400AUSTRALIS'
                            if sku == 'IBA-GA6CE':
                                sku = '4900400AUSTRALIS'
                            if sku == 'IBA-AW54JR':
                                sku = '6042724AUSTRALIS'
                            if sku == 'IBA-WH10V3':
                                sku = '6043102AUSTRALIS'
                            if sku == 'IBA-AW8412CEWK':
                                sku = '6043285AUSTRALIS'
                            if sku == 'IBA-RGA42FMTGF':
                                sku = '6043041AUSTRALIS'
                            if sku == 'IBA-AS7312TCD':
                                sku = '6043219AUSTRALIS'
                            if sku == 'IBA-SRGB305BKF':
                                sku = '6043263AUSTRALIS'
                            if sku == 'IBA-RG8WH':
                                sku = '6042831AUSTRALIS'
                            if sku == 'IBA-RGM21MBLT':
                                sku = '6043236AUSTRALIS'
                            if sku == 'IBA-SR200PW':
                                sku = '604232AUSTRALIS'
                            if sku == 'IBA-QX54QMBSM':
                                sku = '6043311AUSTRALIS'
                            if sku == 'IBA-Q54SFM':
                                sku = '6043309AUSTRALIS'
                            if sku == 'IBA-AW65ECE':
                                sku = '1000401AUSTRALIS'
                            if sku == 'IBA-RG550LDY':
                                sku = '6043398AUSTRALIS'
                            if sku == 'IBA-MB300C':
                                sku = '9300222AUSTRALIS'
                            if sku == 'IBA-RGR652AHBFWK':
                                sku = '6042668AUSTRALIS'
                            if sku == 'IBA-TMB30':
                                sku = '6042552AUSTRALIS'
                            if sku == 'IBA-IGB724BK':
                                sku = '6043103AUSTRALIS'
                            if sku == 'IBA-RG121DXWNF':
                                sku = '6043072AUSTRALIS'
                            if sku == 'IBA-SR200BK':
                                sku = '610222AUSTRALIS'
                            if sku == 'IBA-SRMS625EXBKF':
                                sku = '6043306AUSTRALIS'
                            if sku == 'IBA-AEG50NNT':
                                sku = '6043020AUSTRALIS'
                            if sku == 'IBA-SR600EAST':
                                sku = '6043273AUSTRALIS'
                            if sku == 'IBA-SR500EBM':
                                sku = '6042850AUSTRALIS'
                            if sku == 'IBA-SRGB300BKF':
                                sku = '6043253AUSTRALIS'
                            if sku == 'IBA-SR300ESVM':
                                sku = '6043206AUSTRALIS'
                            if sku == 'IBA-PF15ECENT':
                                sku = '6042444AUSTRALIS'
                            if sku == 'IBA-RG421MOL':
                                sku = '1001221AUSTRALIS'
                            if sku == 'IBA-RG5320CPW':
                                sku = '6043457AUSTRALIS'
                            if sku == 'IBA-AC340OPN':
                                sku = '6042915AUSTRALIS'
                            if sku == 'IBA-SR5CMDXBIL':
                                sku = '6043406AUSTRALIS'
                            if sku == 'IBA-TMB30MGR':
                                sku = '6042870AUSTRALIS'
                            if sku == 'IBA-RG652AHMFXRP':
                                sku = '6043192AUSTRALIS'
                            if sku == 'IBA-AEGB24EBKH':
                                sku = '6043391AUSTRALIS'
                            if sku == 'IBA-RG140WH':
                                sku = '6042901AUSTRALIS'
                            if sku == 'IBA-PNB14EOPN':
                                sku = '6042932AUSTRALIS'
                            if sku == 'IBA-RG550DY':
                                sku = '6042669AUSTRALIS'
                            if sku == 'IBA-RG565LB':
                                sku = '6043394AUSTRALIS'
                            if sku == 'IBA-AW54':
                                sku = '6042613AUSTRALIS'
                            if sku == 'IBA-SR200JB':
                                sku = '6043231AUSTRALIS'
                            if sku == 'IBA-SR200BWNF':
                                sku = '6042894AUSTRALIS'
                            if sku == 'IBA-RGDR4327NTF':
                                sku = '6043005AUSTRALIS'
                            if sku == 'IBA-EHB1005MSSFG':
                                sku = '6043046AUSTRALIS'
                            if sku == 'IBA-Q52LBM':
                                sku = '6043310AUSTRALIS'
                            if sku == 'IBA-AF55':
                                sku = '4600220AUSTRALIS'
                            if sku == 'IBA-AS113BS':
                                sku = '6043378AUSTRALIS'
                            if sku == 'IBA-SRMD200DPW':
                                sku = '6043252AUSTRALIS'
                            if sku == 'IBA-PC12MH':
                                sku = '4600216AUSTRALIS'
                            if sku == 'IBA-PF15BK':
                                sku = '4800121AUSTRALIS'
                            if sku == 'IBA-PF15ECEBK':
                                sku = '6042443AUSTRALIS'
                            if sku == 'IBA-AS73GBKF':
                                sku = '6043218AUSTRALIS'
                            if sku == 'IBA-IBB724BK':
                                sku = '6043104AUSTRALIS'
                            if sku == 'IBA-AW70ECE':
                                sku = '1000273AUSTRALIS'
                            if sku == 'IBA-RG7421':
                                sku = '9300249AUSTRALIS'
                            if sku == 'IBA-AAD140OPN':
                                sku = '6043269AUSTRALIS'
                            if sku == 'IBA-TMB100MMWF':
                                sku = '6043061AUSTRALIS'
                            if sku == 'IBA-RG350DXZWH':
                                sku = '1000183AUSTRALIS'
                            if sku == 'IBA-MTZ11':
                                sku = '9300106AUSTRALIS'
                            if sku == 'IBA-SR200SM':
                                sku = '6042522AUSTRALIS'
                            if sku == 'IBA-SR300EPW':
                                sku = '6042546AUSTRALIS'
                            if sku == 'IBA-AEGB24EMHS':
                                sku = '6043392AUSTRALIS'
                            if sku == 'IBA-JEMJRSPPK':
                                sku = '6042662AUSTRALIS'
                            if sku == 'IBA-RG5120MFCN':
                                sku = '6042812AUSTRALIS'
                            if sku == 'IBA-PF15NT':
                                sku = '4800120AUSTRALIS'
                            if sku == 'IBA-AEG5012BKH':
                                sku = '6043284AUSTRALIS'
                            if sku == 'IBA-PF10CEOPN':
                                sku = '6042999AUSTRALIS'
                            if sku == 'IBA-IUC10':
                                sku = '4716007AUSTRALIS'
                            if sku == 'IBA-RGM21MJB':
                                sku = '6043421AUSTRALIS'
                            if sku == 'IBA-ATZ10PSTM':
                                sku = '6043399AUSTRALIS'
                            if sku == 'IBA-AZ2204ICM':
                                sku = '6042709AUSTRALIS'
                            if sku == 'IBA-SR300ECUB':
                                sku = '6043056AUSTRALIS'
                            if sku == 'IBA-AW5412CE':
                                sku = '6042725AUSTRALIS'
                            if sku == 'IBA-RGM21MCA':
                                sku = '6043422AUSTRALIS'
                            if sku == 'IBA-IAB724BK':
                                sku = '6043105AUSTRALIS'
                            if sku == 'IBA-AZ24047BK':
                                sku = '6043188AUSTRALIS'
                            if sku == 'IBA-ADMINI':
                                sku = '6042553AUSTRALIS'
                            if sku == 'IBA-AS53':
                                sku = '6042885AUSTRALIS'
                            if sku == 'IBA-T15II':
                                sku = '6042645AUSTRALIS'
                            if sku == 'IBA-MS100C':
                                sku = '6042945AUSTRALIS'
                            if sku == 'IBA-SRGB300SDM':
                                sku = '6043262AUSTRALIS'
                            if sku == 'IBA-SRF705BBF':
                                sku = '6091341AUSTRALIS'
                            if sku == 'IBA-AS53TF':
                                sku = '6042884AUSTRALIS'
                            if sku == 'IBA-AZ24027TFF':
                                sku = '6043187AUSTRALIS'
                            if sku == 'IBA-RGM21MWNS':
                                sku = '6043235AUSTRALIS'
                            if sku == 'IBA-RX40MGN':
                                sku = '6043068AUSTRALIS'
                            if sku == 'IBA-PCBE12OPN':
                                sku = '6043096AUSTRALIS'
                            if sku == 'IBA-RG5121BCF':
                                sku = '6043190AUSTRALIS'
                            if sku == 'IBA-AZ2204BBK':
                                sku = '6043288AUSTRALIS'
                            if sku == 'IBA-AZS2209HTFB':
                                sku = '6043290AUSTRALIS'
                            if sku == 'IBA-AZS2200QRBS':
                                sku = '6043293AUSTRALIS'
                            if sku == 'IBA-SR180BS':
                                sku = '6043110AUSTRALIS'
                            if sku == 'IBA-PGMM11JB':
                                sku = '6043245AUSTRALIS'
                            if sku == 'IBA-AZES31VM':
                                sku = '6043342AUSTRALIS'
                            if sku == 'IBA-AZS2200BK':
                                sku = '6043291AUSTRALIS'
                            if sku == 'IBA-PGMM21MGN':
                                sku = '6042897AUSTRALIS'
                            if sku == 'IBA-RGM21MWNS':
                                sku = '6043235AUSTRALIS'
                            if sku == 'IBA-RX40MGN':
                                sku = '6043068AUSTRALIS'
                            if sku == 'IBA-PCBE12OPN':
                                sku = '6043096AUSTRALIS'
                            if sku == 'IBA-SR180BS':
                                sku = '6043110AUSTRALIS'
                            if sku == 'IBA-RG5121BCF':
                                sku = '6043190AUSTRALIS'
                            if sku == 'IBA-AZ2204BBK':
                                sku = '6043008AUSTRALIS'
                            if sku == 'IBA-AZS2209HTFB':
                                sku = '6043289AUSTRALIS'
                            if sku == 'IBA-AZS2200QRBS':
                                sku = '6043293AUSTRALIS'
                            if sku == 'IBA-PGMM11JB':
                                sku = '6043245AUSTRALIS'
                            if sku == 'IBA-AZES31VM':
                                sku = '6043342AUSTRALIS'
                            if sku == 'IBA-AZS2200BK':
                                sku = '6043291AUSTRALIS'
                            if sku == 'IBA-AEG50IBH':
                                sku = '6043016AUSTRALIS'
                            if sku == 'IBA-RX40CA':
                                sku = '6043070AUSTRALIS'
                            if sku == 'IBA-AG75GBS':
                                sku = '6043381AUSTRALIS'
                            if sku == 'IBA-SEW761FMNTF':
                                sku = '6043251AUSTRALIS'
                            if sku == 'IBA-LGB30VYS':
                                sku = '1003180AUSTRALIS'
                            if sku == 'IBA-MF100C':
                                sku = '6042944AUSTRALIS'
                            if sku == 'IBA-ISW10':
                                sku = '4600258AUSTRALIS'
                            if sku == 'IBA-FLMINI':
                                sku = '6043115AUSTRALIS'
                            if sku == 'IBA-YY10SGS':
                                sku = '6043141AUSTRALIS'
                            if sku == 'IBA-YY20OCS':
                                sku = '6043366AUSTRALIS'
                            if sku == 'IBA-JEM77BFP':
                                sku = '4600234AUSTRALIS'
                            if sku == 'IBA-RX40MLB':
                                sku = '6043069AUSTRALIS'
                            if sku == 'IBA-RG550RF':
                                sku = '6042670AUSTRALIS'
                            if sku == 'IBA-T30II':
                                sku = '6042646AUSTRALIS'
                            if sku == 'IBA-FZMINI':
                                sku = '9300287AUSTRALIS'
                            if sku == 'IBA-FRM300PR':
                                sku = '6043248AUSTRALIS'
                            if sku == 'IBA-PHMINIPHASER':
                                sku = '6043242AUSTRALIS'
                            if sku == 'IBA-TRMINI':
                                sku = '6043114AUSTRALIS'
                            if sku == 'IBA-MGB100C':
                                sku = '6042946AUSTRALIS'
                            if sku == 'IBA-PTPRE':
                                sku = '6043529AUSTRALIS'
                            if sku == 'IBA-MM100C':
                                sku = '6042995AUSTRALIS'
                            if sku == 'IBA-UKS100OPN':
                                sku = '6043404AUSTRALIS'
                            if sku == 'IBA-SMMINI':
                                sku = '6042555AUSTRALIS'
                            if sku == 'IBA-RG5120MPRT':
                                sku = '6043363AUSTRALIS'
                            if sku == 'IBA-SI10CCT':
                                sku = '6091477AUSTRALIS'
                            if sku == 'IBA-SI10BW':
                                sku = '6091480AUSTRALIS'
                            if sku == 'IBA-SI10BG':
                                sku = '6091479AUSTRALIS'
                            if sku == 'IBA-SI10CGR':
                                sku = '6091478AUSTRALIS'
                            if sku == 'IBA-SI20BW':
                                sku = '6091484AUSTRALIS'
                            if sku == 'IBA-SI20CGR':
                                sku = '6091482AUSTRALIS'
                            if sku == 'IBA-SI20CCT':
                                sku = '6091481AUSTRALIS'
                            if sku == 'IBA-SI20BG':
                                sku = '6091483AUSTRALIS'
                            if sku == 'IBA-RG421EXBKF':
                                sku = '4600236AUSTRALIS'
                            if sku == 'IBA-RG8570ZRBS':
                                sku = '6042958AUSTRALIS'
                            if sku == 'IBA-IGC10W':
                                sku = '6043066AUSTRALIS'
                            if sku == 'IBA-TS808':
                                sku = '4952470AUSTRALIS'
                            if sku == 'IBA-BTB805MSTGF':
                                sku = '6043386AUSTRALIS'
                            if sku == 'IBA-RG320EXZBKF':
                                sku = '6043199AUSTRALIS'
                            if sku == 'IBA-RG170DXBKN':
                                sku = '509034AUSTRALIS'
                            if sku == 'IBA-RGT1270PBDTF':
                                sku = '6043372AUSTRALIS'
                            if sku == 'IBA-SR180BEM':
                                sku = '6043099AUSTRALIS'
                            if sku == 'IBA-RGRTB621BKF':
                                sku = '6043374AUSTRALIS'
                            if sku == 'IBA-BTB605MSCEM':
                                sku = '6043388AUSTRALIS'
                            if sku == 'IBA-GSRM20BWMF':
                                sku = '6042941AUSTRALIS'
                            if sku == 'IBA-SRM20BWK':
                                sku = '6043230AUSTRALIS'
                            if sku == 'IBA-RG652AHMFX':
                                sku = '6042606AUSTRALIS'
                            if sku == 'IBA-SR305ECUB':
                                sku = '6043058AUSTRALIS'
                            if sku == 'IBA-SR4FMDXEGL':
                                sku = '6043384AUSTRALIS'
                            if sku == 'IBA-RGT1221PBDTF':
                                sku = '6043371AUSTRALIS'
                            if sku == 'IBA-IMC50FS':
                                sku = '4716020AUSTRALIS'
                            if sku == 'IBA-AZ2204NWMGR':
                                sku = '6043362AUSTRALIS'
                            if sku == 'IBA-AZ47P1QMBIB':
                                sku = '6043367AUSTRALIS'
                            if sku == 'IBA-AAD50CELG':
                                sku = '6043402AUSTRALIS'
                            if sku == 'IBA-RGT1220PBABS':
                                sku = '6043370AUSTRALIS'
                            if sku == 'IBA-SR5FMDXEGL':
                                sku = '6043385AUSTRALIS'
                            if sku == 'IBA-RG421AHMBMT':
                                sku = '6042651AUSTRALIS'
                            if sku == 'IBA-ICTB721BKF':
                                sku = '6043304AUSTRALIS'
                            if sku == 'IBA-SR305EBWK':
                                sku = '6042860AUSTRALIS'
                            if sku == 'IBA-AEG50NBKH':
                                sku = '6043019AUSTRALIS'
                            if sku == 'IBA-RX70QATRB':
                                sku = '1000256AUSTRALIS'
                            if sku == 'IBA-RGD7521PBDSF':
                                sku = '6043250AUSTRALIS'
                            if sku == 'IBA-AEG7MH':
                                sku = '6043075AUSTRALIS'
                            if sku == 'IBA-RG421EXLBKF':
                                sku = '6043375AUSTRALIS'
                            if sku == 'IBA-SR300EPGM':
                                sku = '6043207AUSTRALIS'
                            if sku == 'IBA-RG60ALSBAM':
                                sku = '6043146AUSTRALIS'
                            if sku == 'IBA-AEG70VVH':
                                sku = '6043223AUSTRALIS'
                            if sku == 'IBA-SR206BWNF':
                                sku = '6042896AUSTRALIS'
                            if sku == 'IBA-AZES31IV':
                                sku = '6042896AUSTRALIS'
                            if sku == 'IBA-AZ2204NAWD':
                                sku = '6043287AUSTRALIS'
                            if sku == 'IBA-MR500C':
                                sku = '9300230AUSTRALIS'
                            if sku == 'IBA-EHB1005SMSEM':
                                sku = '6043499AUSTRALIS'
                            if sku == 'IBA-BTB625EXBKF':
                                sku = '6043305AUSTRALIS'
                            if sku == 'IBA-AF95BS':
                                sku = '6043215AUSTRALIS'
                            if sku == 'IBA-EHB1006MSMGM':
                                sku = '6043390AUSTRALIS'
                            if sku == 'IBA-SR2605CBB':
                                sku = '6042694AUSTRALIS'
                            if sku == 'IBA-EHB1000PWM':
                                sku = '6043134AUSTRALIS'
                            if sku == 'IBA-RG652AHMNGB':
                                sku = '6042488AUSTRALIS'
                            if sku == 'IBA-SR300EBCA':
                                sku = '6042858AUSTRALIS'
                            if sku == 'IBA-AZ42P1BK':
                                sku = '6043368AUSTRALIS'
                            if sku == 'IBA-BTB806MSTGF':
                                sku = '6043387AUSTRALIS'
                            if sku == 'IBA-AEWC400TKS':
                                sku = '6042891AUSTRALIS'
                            if sku == 'IBA-PS60SSL':
                                sku = '6042787AUSTRALIS'
                            if sku == 'IBA-RG421HPFMBRG':
                                sku = '6043036AUSTRALIS'
                            if sku == 'IBA-SR375ESPB':
                                sku = '6043205AUSTRALIS'
                            if sku == 'IBA-EHB1005MSBKF':
                                sku = '6043045AUSTRALIS'
                            if sku == 'IBA-AAD100EOPN':
                                sku = '6043267AUSTRALIS'
                            if sku == 'IBA-AAD300CELGS':
                                sku = '6043265AUSTRALIS'
                            if sku == 'IBA-EHB1005BKF':
                                sku = '6043135AUSTRALIS'
                            if sku == 'IBA-S6570SK':
                                sku = '6042609AUSTRALIS'
                            if sku == 'IBA-SRMD205SPN':
                                sku = '6043059AUSTRALIS'
                            if sku == 'IBA-AMH90PBM':
                                sku = '6043380AUSTRALIS'
                            if sku == 'IBA-AEG70TCH':
                                sku = '6043222AUSTRALIS'
                            if sku == 'IBA-SR605EBKT':
                                sku = '6043274AUSTRALIS'
                            if sku == 'IBA-AAD170CELGS':
                                sku = '6043266AUSTRALIS'
                            if sku == 'IBA-AS93FMAYS':
                                sku = '6043379AUSTRALIS'
                            if sku == 'IBA-AS93FMVLS':
                                sku = '6042737AUSTRALIS'
                            if sku == 'IBA-AAD50LG':
                                sku = '6043401AUSTRALIS'
                            if sku == 'IBA-PCBE14MHWK':
                                sku = '6043255AUSTRALIS'
                            if sku == 'IBA-RGA42HPQMBIG':
                                sku = '6043249AUSTRALIS'
                            if sku == 'IBA-RG140SB':
                                sku = '6042900AUSTRALIS'
                            if sku == 'IBA-AS53SRF':
                                sku = '6043383AUSTRALIS'
                            if sku == 'IBA-SA360NQMBMG':
                                sku = '6043093AUSTRALIS'
                            if sku == 'IBA-AS93FML':
                                sku = '6042921AUSTRALIS'
                            if sku == 'IBA-SA460MBWSUB':
                                sku = '6043108AUSTRALIS'
                            if sku == 'IBA-AM53':
                                sku = '9300242AUSTRALIS'
                            if sku == 'IBA-AAD100OPN':
                                sku = '6043268AUSTRALIS'
                            if sku == 'IBA-RGD71ALPACKF':
                                sku = '6043202AUSTRALIS'
                            if sku == 'IBA-SR600ECTF':
                                sku = '6043272AUSTRALIS'
                            if sku == 'IBA-RX70QASB':
                                sku = '6043233AUSTRALIS'
                            if sku == 'IBA-RGD61ALAMTR':
                                sku = '6043201AUSTRALIS'
                            if sku == 'IBA-AS73GPBM':
                                sku = '6043382AUSTRALIS'
                            if sku == 'IBA-AS73TCD':
                                sku = '6043247AUSTRALIS'
                            if sku == 'IBA-AEWC11DVS':
                                sku = '6043224AUSTRALIS'
                            if sku == 'IBA-AFB200TKS':
                                sku = '6042794AUSTRALIS'
                            if sku == 'IBA-S520WK':
                                sku = '6042841AUSTRALIS'
                            if sku == 'IBA-RG421HPAMABL':
                                sku = '6043035AUSTRALIS'
                            if sku == 'IBA-SA360NQMSPB':
                                sku = '6043092AUSTRALIS'
                            if sku == 'IBA-AZES40PPK':
                                sku = '6043478AUSTRALIS'
                            if sku == 'IBA-AM53TF':
                                sku = '6043221AUSTRALIS'
                            if sku == 'IBA-PSM10':
                                sku = '6042628AUSTRALIS'
                            if sku == 'IBA-MRB500C':
                                sku = '6042660AUSTRALIS'
                            if sku == 'IBA-AMH90CRF':
                                sku = '6043217AUSTRALIS'
                            if sku == 'IBA-AF55TKF':
                                sku = '6042873AUSTRALIS'
                            if sku == 'IBA-AF95FM':
                                sku = '6042733AUSTRALIS'
                            if sku == 'IBA-AG95QADBS':
                                sku = '6042736AUSTRALIS'
                            if sku == 'IBA-AM93MENT':
                                sku = '6042886AUSTRALIS'
                            if sku == 'IBA-AMH90BK':
                                sku = '6043216AUSTRALIS'
                            if sku == 'IBA-AR520HBK':
                                sku = '6043186AUSTRALIS'
                            if sku == 'IBA-AR520HFMVLS':
                                sku = '6043185AUSTRALIS'
                            if sku == 'IBA-AS73OLM':
                                sku = '6042882AUSTRALIS'
                            if sku == 'IBA-AS73TBC':
                                sku = '9300243AUSTRALIS'
                            if sku == 'IBA-AS93FMTCD':
                                sku = '6042876AUSTRALIS'
                            if sku == 'IBA-AZ2204NBK':
                                sku = '6043288AUSTRALIS'
                            if sku == 'IBA-AZ427P1PBCKB':
                                sku = '6043369AUSTRALIS'
                            if sku == 'IBA-AZS2200FSTB':
                                sku = '6043292AUSTRALIS'
                            if sku == 'IBA-FLATV1BK':
                                sku = '6043297AUSTRALIS'
                            if sku == 'IBA-JS140MSDL':
                                sku = '6043123AUSTRALIS'
                            if sku == 'IBA-JS240PSCA':
                                sku = '6043122AUSTRALIS'
                            if sku == 'IBA-JS2410SYB':
                                sku = '6043296AUSTRALIS'
                            if sku == 'IBA-MM1TAB':
                                sku = '6042761AUSTRALIS'
                            if sku == 'IBA-RG5121DBF':
                                sku = '6042811AUSTRALIS'
                            if sku == 'IBA-RG8570CSTNT':
                                sku = '6043410AUSTRALIS'
                            if sku == 'IBA-RG8570ZLBSR':
                                sku = '6043397AUSTRALIS'
                            if sku == 'IBA-SA460QMWTQB':
                                sku = '6043109AUSTRALIS'
                            if sku == 'IBA-SR1305SBMGL':
                                sku = '6043271AUSTRALIS'
                            if sku == 'IBA-T80IISM':
                                sku = '6042647AUSTRALIS'
                            if sku == 'IBA-TQM1NT':
                                sku = '6042762AUSTRALIS'
                            if sku == 'IBA-TQMS1CTB':
                                sku = '6043411AUSTRALIS'
                            if sku == 'IBA-AAD190CEOPN':
                                sku = '6043414AUSTRALIS'
                            if sku == 'IBA-AAD190CEWKH':
                                sku = '6043415AUSTRALIS'
                            if sku == 'IBA-AAD50CELBS':
                                sku = '6043521AUSTRALIS'
                            if sku == 'IBA-AAD50CETCB':
                                sku = '6043520AUSTRALIS'
                            if sku == 'IBA-AEG70LTIH':
                                sku = '6043508AUSTRALIS'
                            if sku == 'IBA-AEG70PIH':
                                sku = '6043507AUSTRALIS'
                            if sku == 'IBA-AEG7MHWK':
                                sku = '6043523AUSTRALIS'
                            if sku == 'IBA-AEGB30ENTG':
                                sku = '6043533AUSTRALIS'
                            if sku == 'IBA-AEWC400AMS':
                                sku = '6043509AUSTRALIS'
                            if sku == 'IBA-AW1040CEOPN':
                                sku = '6043412AUSTRALIS'
                            if sku == 'IBA-AW1040CEWK':
                                sku = '6043413AUSTRALIS'
                            if sku == 'IBA-AZ2402LTFF':
                                sku = '6043010AUSTRALIS'
                            if sku == 'IBA-AZES31PRB':
                                sku = '6043479AUSTRALIS'
                            if sku == 'IBA-JIVA10LDSB':
                                sku = '6043475AUSTRALIS'
                            if sku == 'IBA-KIKOSP3TEB':
                                sku = '6043514AUSTRALIS'
                            if sku == 'IBA-PA230ENSL':
                                sku = '6043280AUSTRALIS'
                            if sku == 'IBA-PA300ENSL':
                                sku = '6043279AUSTRALIS'
                            if sku == 'IBA-Q547BMM':
                                sku = '6043476AUSTRALIS'
                            if sku == 'IBA-RG121SPBKN':
                                sku = '6043461AUSTRALIS'
                            if sku == 'IBA-RG121SPBMC':
                                sku = '6043462AUSTRALIS'
                            if sku == 'IBA-SR1355BDUF':
                                sku = '6043490AUSTRALIS'
                            if sku == 'IBA-SR5FMDX2NTL':
                                sku = '6043488AUSTRALIS'
                            if sku == 'IBA-SRC6MSBLL':
                                sku = '6043501AUSTRALIS'
                            if sku == 'IBA-SRMS805TSR':
                                sku = '6043502AUSTRALIS'
                            if sku == 'IBA-AEG50LBKH':
                                sku = '6043018AUSTRALIS'
                            if sku == 'IBA-TOD10NTKF':
                                sku = '6043535AUSTRALIS'
                            if sku == 'IBA-JS2480MCR':
                                sku = '6042641AUSTRALIS'
                            if sku == 'IBA-RGIXL7BKF':
                                sku = '6043034AUSTRALIS'
                            if sku == 'IBA-RGR652AHBWK':
                                sku = '6042795AUSTRALIS'
                            if sku == 'IBA-SR300EDXRGC':
                                sku = '6043430AUSTRALIS'
                            if sku == 'IBA-RG550PN':
                                sku = '6042778AUSTRALIS'
                            if sku == 'IBA-JS1CR':
                                sku = '6042758AUSTRALIS'
                            if sku == 'IBA-JIVAJRDSE':
                                sku = '6043142AUSTRALIS'
                            if sku == 'IBA-JSM100':
                                sku = '604880AUSTRALIS'
                            if sku == 'IBA-QX527PBABS':
                                sku = '6043313AUSTRALIS'
                            if sku == 'IBA-RGM21BKN':
                                sku = '6042792AUSTRALIS'
                            if sku == 'IBA-SA260FMTGB':
                                sku = '6042741AUSTRALIS'
                            if sku == 'IBA-TS9DX':
                                sku = '47051AUSTRALIS'
                            if sku == 'IBA-SR300EBLWK':
                                sku = '6043208AUSTRALIS'
                            if sku == 'IBA-RGIB21BK':
                                sku = '6043033AUSTRALIS'
                            if sku == 'IBA-AZES40BK':
                                sku = '6043340AUSTRALIS'
                            if sku == 'IBA-GB10BS':
                                sku = '4600306AUSTRALIS'
                            if sku == 'IBA-PC14MHCEWK':
                                sku = '6043254AUSTRALIS'
                            if sku == 'IBA-TCY10ESFH':
                                sku = '6043261AUSTRALIS'
                            if sku == 'IBA-CSMINI':
                                sku = '6042554AUSTRALIS'
                            if sku == 'IBA-JEMJRWHLH':
                                sku = '6042584AUSTRALIS'
                            if sku == 'IBA-AZ2204NPBM':
                                sku = '6043286AUSTRALIS'
                            if sku == 'IBA-PS120':
                                sku = '4600267AUSTRALIS'
                            if sku == 'IBA-TCY10EBLK':
                                sku = '470914AUSTRALIS'
                            if sku == 'IBA-RX40BKN':
                                sku = '6043100AUSTRALIS'
                            if sku == 'IBA-TS808HWB':
                                sku = '4852477AUSTRALIS'
                            if sku == 'IBA-SR605ECTF':
                                sku = '6043275AUSTRALIS'
                            if sku == 'IBA-S521BBS':
                                sku = '6042842AUSTRALIS'
                            if sku == 'IBA-S521BBS':
                                sku = '6042842AUSTRALIS'
                            if sku == 'IBA-LB1VL':
                                sku = '6043298AUSTRALIS'
                            if sku == 'IBA-PGMM31':
                                sku = '9300231AUSTRALIS'
                            if sku == 'IBA-TS808DX':
                                sku = '4952478AUSTRALIS'
                            if sku == 'IBA-UB804MOB':
                                sku = '6042756AUSTRALIS'
                            if sku == 'IBA-PF15ECETBS':
                                sku = '6042445AUSTRALIS'
                            if sku == 'IBA-M510EBS':
                                sku = '495059AUSTRALIS'
                            if sku == 'IBA-FS40CL':
                                sku = '6043118AUSTRALIS'
                            if sku == 'IBA-AR420VLS':
                                sku = '1003151AUSTRALIS'
                            if sku == 'IBA-FS40DA':
                                sku = '6043119AUSTRALIS'
                            if sku == 'IBA-ESPR2003':
                                sku = '6091474AUSTRALIS'
                            if sku == 'IBA-AF75BS':
                                sku = '603114AUSTRALIS'
                            if sku == 'IBA-AS2000BS':
                                sku = '6043282AUSTRALIS'
                            if sku == 'IBA-BTB747NTL':
                                sku = '6042658AUSTRALIS'
                            if sku == 'IBA-ESPR1003':
                                sku = '6091473AUSTRALIS'
                            if sku == 'IBA-JS2GD':
                                sku = '6043438AUSTRALIS'
                            if sku == 'IBA-PIA3761CBLP':
                                sku = '6043437AUSTRALIS'
                            if sku == 'IBA-RGR5221TFR':
                                sku = '6043002AUSTRALIS'
                            if sku == 'IBA-S671ALBBCM':
                                sku = '6043042AUSTRALIS'
                            if sku == 'IBA-SA260FMVLS':
                                sku = '6042741AUSTRALIS'
                            if sku == 'IBA-SR606ECTF':
                                sku = '6043276AUSTRALIS'
                            if sku == 'IBA-WB250C':
                                sku = '6043112AUSTRALIS'
                            if sku == 'IBA-AAD50TCB':
                                sku = '6043522AUSTRALIS'
                            if sku == 'IBA-AC340CEOPN':
                                sku = '6043510AUSTRALIS'
                            if sku == 'IBA-AC340LOPN':
                                sku = '6043512AUSTRALIS'
                            if sku == 'IBA-AEG200LGS':
                                sku = '6043474AUSTRALIS'
                            if sku == 'IBA-AEG220LGS':
                                sku = '6043473AUSTRALIS'
                            if sku == 'IBA-AF95DA':
                                sku = '6043484AUSTRALIS'
                            if sku == 'IBA-AGB200BKF':
                                sku = '6043496AUSTRALIS'
                            if sku == 'IBA-AMH90IV':
                                sku = '6043485AUSTRALIS'
                            if sku == 'IBA-AS73GMPF':
                                sku = '6043487AUSTRALIS'
                            if sku == 'IBA-ATZ100SBT':
                                sku = '6042947AUSTRALIS'
                            if sku == 'IBA-AW247CEOPN':
                                sku = '6043470AUSTRALIS'
                            if sku == 'IBA-AW84WK':
                                sku = '6043511AUSTRALIS'
                            if sku == 'IBA-AZ2203NATQ':
                                sku = '6043446AUSTRALIS'
                            if sku == 'IBA-AZ2203NBK':
                                sku = '6043447AUSTRALIS'
                            if sku == 'IBA-AZ2204NWDTB':
                                sku = '6043445AUSTRALIS'
                            if sku == 'IBA-AZ2402BKF':
                                sku = '6043006AUSTRALIS'
                            if sku == 'IBA-AZ2402PWF':
                                sku = '6042972AUSTRALIS'
                            if sku == 'IBA-AZ2402TFF':
                                sku = '6042706AUSTRALIS'
                            if sku == 'IBA-AZ2407FBSR':
                                sku = '6043443AUSTRALIS'
                            if sku == 'IBA-AZ2407FSDE':
                                sku = '6043444AUSTRALIS'
                            if sku == 'IBA-AZS2209ATQ':
                                sku = '6043449AUSTRALIS'
                            if sku == 'IBA-EHB1005FAOM':
                                sku = '6043498AUSTRALIS'
                            if sku == 'IBA-JBBM30BKF':
                                sku = '6043299AUSTRALIS'
                            if sku == 'IBA-JBM9999AMM':
                                sku = '6043442AUSTRALIS'
                            if sku == 'IBA-JIVAX2GH':
                                sku = '6043440AUSTRALIS'
                            if sku == 'IBA-KIKO100TRR':
                                sku = '6043439AUSTRALIS'
                            if sku == 'IBA-KRYS10':
                                sku = '6043536AUSTRALIS'
                            if sku == 'IBA-M510EDVS':
                                sku = '6043528AUSTRALIS'
                            if sku == 'IBA-MRC10NT':
                                sku = '6043463AUSTRALIS'
                            if sku == 'IBA-Q52PBABS':
                                sku = '6043477AUSTRALIS'
                            if sku == 'IBA-RG120QASPBGD':
                                sku = '6043516AUSTRALIS'
                            if sku == 'IBA-RG220PA1BKB':
                                sku = '6043515AUSTRALIS'
                            if sku == 'IBA-RG5170GSVF':
                                sku = '6043004AUSTRALIS'
                            if sku == 'IBA-RG7320EXBKF':
                                sku = '6043481AUSTRALIS'
                            if sku == 'IBA-RG8570BRE':
                                sku = '6043452AUSTRALIS'
                            if sku == 'IBA-RG8570RBS':
                                sku = '6043453AUSTRALIS'
                            if sku == 'IBA-RG8870BRE':
                                sku = '6043451AUSTRALIS'
                            if sku == 'IBA-RG9PBTGF':
                                sku = '6043373AUSTRALIS'
                            if sku == 'IBA-RGA622XHBK':
                                sku = '6043364AUSTRALIS'
                            if sku == 'IBA-RGA622XHWH':
                                sku = '6043365AUSTRALIS'
                            if sku == 'IBA-RGD3121PRF':
                                sku = '6043459AUSTRALIS'
                            if sku == 'IBA-RGDMS8CSM':
                                sku = '6043376AUSTRALIS'
                            if sku == 'IBA-RX120SPMLM':
                                sku = '6043518AUSTRALIS'
                            if sku == 'IBA-SML721RGC':
                                sku = '6043377AUSTRALIS'
                            if sku == 'IBA-SR1350BDUF':
                                sku = '6043489AUSTRALIS'
                            if sku == 'IBA-SR200BWK':
                                sku = '6043519AUSTRALIS'
                            if sku == 'IBA-SR300EMGB':
                                sku = '6043494AUSTRALIS'
                            if sku == 'IBA-SR305EMGB':
                                sku = '6043495AUSTRALIS'
                            if sku == 'IBA-SR500EBAB':
                                sku = '6043492AUSTRALIS'
                            if sku == 'IBA-SR505EBAB':
                                sku = '6043493AUSTRALIS'
                            if sku == 'IBA-SRAS7CBS':
                                sku = '6043500AUSTRALIS'
                            if sku == 'IBA-TOD10':
                                sku = '6043535AUSTRALIS'
                            if sku == 'IBA-UTA20':
                                sku = '9300105AUSTRALIS'
            
            
                            if 'iba-' in sku.lower():
                                sku = sku.replace('IBA-', '')
                                sku = fr'{sku}AUSTRALIS'
            
                        if "alesis" in brand.lower():
            
                            if sku == 'ALE-CRIMSONSE':
                                sku = 'CRIMSON-SE'
                            if sku == 'ALE-SURGESE':
                                sku = 'SURGE-SE'
                            if sku == 'ALE-STRIKEPROSE':
                                sku = 'STRIKEPRO-SE'
                            if sku == 'ALE-STRIKEMP':
                                sku = 'STRIKEMULTIPAD'
                            if sku == 'ALE-COMMANDMESHX':
                                sku = 'COMMANDMESH-X'
                            if sku == 'ALE-COMMAMESHSE':
                                sku = 'COMMANDMESH-SE'
                            if sku == 'ALE-PRESTIGEART':
                                sku = 'PRESTIGEARTIST'
                            if sku == 'ALE-DRUMESS':
                                sku = 'DRUMESSENTIALS'
                            if sku == 'ALE-V49MK2':
                                sku = 'V49MKII'
                            if sku == 'ALE-V61MK2':
                                sku = 'V61MKII'
                            if sku == 'ALE-MPCLAMP':
                                sku = 'MULTIPADCLAMP'
                            if sku == 'ALE-VIRTUEK':
                                sku = 'VIRTUEBLACK'
                            if sku == 'ALE-AHB1':
                                sku = 'AHB-1'
                            if sku == 'ALE-V25MK2':
                                sku = 'V25MKII'
                            if sku == 'ALE-VORTEXW2':
                                sku = 'VORTEX-W2'
            
            
            
                            sku = sku.replace('ALE-', '')
            
                            sku = fr'16{sku}EF'
            
                        if "nord" in brand.lower():
            
                            if sku == 'NOR-PIANO588':
                                sku = '25NORDPIANO588EF'
                            if sku == 'NOR-PIANO573':
                                sku = '25NORDPIANO573EF'
                            if sku == 'NOR-NE673D':
                                sku = '25NE673DEF'
                            if sku == 'NOR-NE673HP':
                                sku = '25NE673HPEF'
                            if sku == 'NOR-GRAND':
                                sku = '25NORDGRANDEF'
                            if sku == 'NOR-NE6D':
                                sku = '25NE6DEF'
                            if sku == 'NOR-ND3P':
                                sku = '25ND3PEF'
                            if sku == 'NOR-NW2':
                                sku = '25NORDWAVE2EF'
                            if sku == 'NOR-PIANOMON':
                                sku = '25PIANOMONITORSEF'
                            if sku == 'NOR-SP1':
                                sku = '25SP1EF'
                            if sku == 'NOR-TRIPLEPEDAL':
                                sku = '25TRIPLEPEDALEF'
                            if sku == 'NOR-NSC88':
                                sku = '25NSC-88EF'
                            if sku == 'NOR-SCHP':
                                sku = '25NSC-HPEF'
                            if sku == 'NOR-KBSTAND':
                                sku = '25KEYBOARDSTANDEF'
                            if sku == 'NOR-NSC73':
                                sku = '25NSC-73EF'
                            if sku == 'NOR-MUSICSTAND':
                                sku = '25MUSICSTANDEF'
                            if sku == 'NOR-NSC61':
                                sku = '25NSC-61EF'
                            if sku == 'NOR-NSC76':
                                sku = '25NSC-76EF'
                            if sku == 'NOR-DC88':
                                sku = '25DC88EF'
                            if sku == 'NOR-DC73':
                                sku = '25EC73EF'
                            if sku == 'NOR-NSCPIANO73':
                                sku = '25NSC-PIANO73EF'
                            if sku == 'NOR-NSCGRAND':
                                sku = '25NSC-GRANDEF'
                            if sku == 'NOR-HALFMOON':
                                sku = '25HALFMOONEF'
                            if sku == 'NOR-NSCPM':
                                sku = '25NSC-PMEF'
                            if sku == 'NOR-DCHP':
                                sku = '25DCHPEF'
                            if sku == 'NOR-NSCWAVE2':
                                sku = '25NSC-WAVE2EF'
                            if sku == 'NOR-DCNG':
                                sku = '25DC-GRANDEF'
                            if sku == 'NOR-NLA1':
                                sku = '25NLA1EF'
                            if sku == 'NOR-NSC-C1':
                                sku = '25EF'
                            if sku == 'NOR-STAGE3COMP':
                                sku = '25NORDSTAGE3COMPACTEF'
                            if sku == 'NOR-STAGE376HP':
                                sku = '25NORDSTAGE376HPEF'
                            if sku == 'NOR-STAGE388':
                                sku = '25NORDSTAGE388EF'
                            if sku == 'NOR-DC76':
                                sku = '25DC76EF'
                            if sku == 'NOR-KBSW':
                                sku = '25KEYBOARDSTANDWOODEF'
                            if sku == 'NOR-KEYSTANDC2':
                                sku = '25KEYBOARDSTANDC2EF'
                            if sku == 'NOR-NSCA1':
                                sku = '25NSC-A1EF'
            
                        if "akai" in brand.lower():
            
                            if sku == 'AKA-MPCONE':
                                sku = '69MPC-OEF'
                            if sku == 'AKA-MPCLIVE2':
                                sku = '69MPC-L2EF'
                            if sku == 'AKA-MPKMINI3':
                                sku = '69MPKMINI3EF'
                            if sku == 'AKA-MPCX':
                                sku = '69MPC-XEF'
                            if sku == 'AKA-MPKMINI3BK':
                                sku = '69MPKMINI3-BKEF'
                            if sku == 'AKA-MPKMINIPLUS':
                                sku = '69MPKMINIPLUSEF'
                            if sku == 'AKA-FORCE':
                                sku = '69FORCEEF'
                            if sku == 'AKA-MPKMINIPLAY3':
                                sku = '69MPKMINIPLAY3EF'
                            if sku == 'AKA-MPKMINI3WH':
                                sku = '69MPKMINI3-WHEF'
                            if sku == 'AKA-MPCSTUDIO2':
                                sku = '69MPC-BSEF'
                            if sku == 'AKA-APCMINIMK2':
                                sku = '69APCMINIEF'
                            if sku == 'AKA-MPK249':
                                sku = '69MPK249EF'
                            if sku == 'AKA-MPK261':
                                sku = '69MPK261EF'
                            if sku == 'AKA-APCKEY25MK2':
                                sku = '69APCKEY25EF'
                            if sku == 'AKA-MPD226':
                                sku = '69MPD226EF'
                            if sku == 'AKA-FIRENS':
                                sku = '69FIRENSEF'
                            if sku == 'AKA-MPK249BK':
                                sku = '69MPK249-BKEF'
                            if sku == 'AKA-MPK225':
                                sku = '69MPK225EF'
                            if sku == 'AKA-FIRE':
                                sku = '69FIREEF'
                            if sku == 'AKA-MPD218':
                                sku = '69MPD218EF'
                            if sku == 'AKA-EWI5000':
                                sku = '69EWI5000EF'
                            if sku == 'AKA-EWISOLOWH':
                                sku = '69EWI-SOLO-WHEF'
                            if sku == 'AKA-MPCKEY61':
                                sku = '69MPC-KEY61EF'
                            if sku == 'AKA-APC40MK2':
                                sku = '69APC40MK2EF'
                            if sku == 'AKA-MPX8':
                                sku = '69MPX8EF'
            
                        if "marshall" in brand.lower():
            
                            if sku == 'MAR-SV20H':
                                sku = '70SV20HEF'
                            if sku == 'MAR-MG10G':
                                sku = '71MG10GEF'
                            if sku == 'MAR-SC20C':
                                sku = '70SC20CEF'
                            if sku == 'MAR-SC20H':
                                sku = '70SC20HEF'
                            if sku == 'MAR-SV20C':
                                sku = '70SV20CEF'
                            if sku == 'MAR-MG15GR':
                                sku = '71MG15GREF'
                            if sku == 'MAR-MS2':
                                sku = '71MS-2EF'
                            if sku == 'MAR-ORI20C':
                                sku = '76ORI20CEF'
                            if sku == 'MAR-CODE50':
                                sku = '71CODE50EF'
                            if sku == 'MAR-MC1960A':
                                sku = '71MC-1960AEF'
                            if sku == 'MAR-MLH2245':
                                sku = '70MLH-2245EF'
                            if sku == 'MAR-CODE25':
                                sku = '71CODE25EF'
                            if sku == 'MAR-MC1960AV':
                                sku = '70MC-1960AVEF'
                            if sku == 'MAR-MX112':
                                sku = '76MX112EF'
                            if sku == 'MAR-MX212':
                                sku = '76MX212EF'
                            if sku == 'MAR-SC212':
                                sku = '70SC212EF'
                            if sku == 'MAR-MC1960AX':
                                sku = '70MC-1960AXEF'
                            if sku == 'MAR-SV112':
                                sku = '70SV112EF'
                            if sku == 'MAR-SC112':
                                sku = '70SC112EF'
                            if sku == 'MAR-PEDL91009':
                                sku = '73PEDL-91009EF'
                            if sku == 'MAR-MC1936':
                                sku = '70MC-1936EF'
                            if sku == 'MAR-MS4':
                                sku = '73ms-4EF'
                            if sku == 'MAR-MHW1960BHW':
                                sku = '70MHW-1960BHWEF'
                            if sku == 'MAR-MHW1960AHW':
                                sku = '70MHW-1960AHWEF'
                            if sku == 'MAR-ORI212A':
                                sku = '76ORI212AEF'
                            if sku == 'MAR-MC2536':
                                sku = '70MC-2536EF'
                            if sku == 'MAR-PEDL91006':
                                sku = '73PEDL-91006EF'
                            if sku == 'MAR-FRIDGEMF32V2':
                                sku = '77FRIDGE-MF32EF'
                            if sku == 'MAR-MG50GFX':
                                sku = '71MG50GFXEF'
                            if sku == 'MAR-DSL1H':
                                sku = '76DSL1HEF'
                            if sku == 'MAR-MX412A':
                                sku = '76MX412AEF'
                            if sku == 'MAR-MC1960B':
                                sku = '70MC-1960BEF'
                            if sku == 'MAR-PEDL90003':
                                sku = '73PEDL-90003EF'
                            if sku == 'MAR-COVR00008':
                                sku = '73COVR-00008EF'
                            if sku == 'MAR-COVR00022':
                                sku = '73COVR-00022EF'
                            if sku == 'MAR-COVR00053':
                                sku = '73COVR-00053EF'
                            if sku == 'MAR-COVR00054':
                                sku = '73COVR-00054EF'
                            if sku == 'MAR-JVM205C':
                                sku = '70JVM205CEF'
                            if sku == 'MAR-MC2512':
                                sku = '70MC-2512EF'
                            if sku == 'MAR-MVC2525C':
                                sku = '70MVC-2525CEF'
                            if sku == 'MAR-ORI212':
                                sku = '76ORI212EF'
                            if sku == 'MAR-PEDL10001':
                                sku = '73PEDL-10001EF'
                            if sku == 'MAR-DSL40C':
                                sku = '76DSL40CEF'
                            if sku == 'MAR-DSL20H':
                                sku = '76DSL20HEF'
                            if sku == 'MAR-MG30GFX':
                                sku = '71MG30GFXEF'
                            if sku == 'MAR-DSL100H':
                                sku = '76DSL100HEF'
                            if sku == 'MAR-DSL20C':
                                sku = '76DSL20CEF'
                            if sku == 'MAR-MG15G':
                                sku = '71MG15GEF'
                            if sku == 'MAR-MLH2525H':
                                sku = '70MLH-2525HEF'
                            if sku == 'MAR-ORI50C':
                                sku = '76ORI50CEF'
                            if sku == 'MAR-ORI50H':
                                sku = '71ORI50HEF'
                            if sku == 'MAR-MHW1959HW':
                                sku = '70MHW-1959HWEF'
                            if sku == 'MAR-ORI20H':
                                sku = '76ORI20HEF'
                            if sku == 'MAR-MLH1987X':
                                sku = '70MLK-1987XEF'
                            if sku == 'MAR-MLH2555X':
                                sku = '70MLH-2555XEF'
                            if sku == 'MAR-MG15GFX':
                                sku = '71MG15GFXEF'
                            if sku == 'MAR-DSL5C':
                                sku = '76DSL5CEF'
                            if sku == 'MAR-JVM410H':
                                sku = '70JVM410HEF'
                            if sku == 'MAR-MVC1962':
                                sku = '70MVC-1962EF'
                            if sku == 'MAR-MC2551AV':
                                sku = '70MC-2551AVEF'
                            if sku == 'MAR-MX412B':
                                sku = '76MX412BEF'
                            if sku == 'MAR-MC1960BX':
                                sku = '70MC-1960BXEF'
                            if sku == 'MAR-MC1960BV':
                                sku = '70MC-1960BVEF'
                            if sku == 'MAR-MLH2203':
                                sku = '70MLH-2203EF'
                            if sku == 'MAR-JVM410C':
                                sku = '70JVM410CEF'
                            if sku == 'MAR-MS2R':
                                sku = '73MS-2REF'
                            if sku == 'MAR-MC2536A':
                                sku = '70MC-2536AEF'
                            if sku == 'MAR-PEDL91016':
                                sku = '73PEDL-91016EF'
                            if sku == 'MAR-DSL1C':
                                sku = '76DSL1CEF'
                            if sku == 'MAR-MC1936VL':
                                sku = '70MC-1936VLEF'
                            if sku == 'MAR-MC1960TV':
                                sku = '70MC-1960TVEF'
                            if sku == 'MAR-MC2551BV':
                                sku = '70MC-2551BVEF'
                            if sku == 'MAR-PACK00050':
                                sku = '73PACK-00050EF'
                            if sku == 'MAR-PACK-00005':
                                sku = '73PACK-00005EF'
                            if sku == 'MAR-CONTROLLER4':
                                sku = '71CONTROLLER-4EF'
                            if sku == 'MAR-PEDL90016':
                                sku = '73PEDL-90016EF'
                            if sku == 'MAR-MS2C':
                                sku = '73MS-2CEF'
                            if sku == 'MAR-CONTROLLER2':
                                sku = '71CONTROLLER-2EF'
                            if sku == 'MAR-COVR00055':
                                sku = '73COVR-00055EF'
                            if sku == 'MAR-JCM4100':
                                sku = '70JCM-4100EF'
                            if sku == 'MAR-JVM205H':
                                sku = '70JVM205HEF'
                            if sku == 'MAR-JVM210C':
                                sku = '70JVM210CEF'
                            if sku == 'MAR-JVM210H':
                                sku = '70JVM210HEF'
                            if sku == 'MAR-MHW1974X':
                                sku = '70MHW-1974EF'
            
            
            
                        if "gruv" in brand.lower():
            
                            brand = 'Gruv Gear'
            
                            if sku == 'GRU-FW1PKSM':
                                sku = 'FW1-PK-SMCMC'
                            if sku == 'GRU-FW1PKMD':
                                sku = 'FW1-PK-MDCMC'
                            if sku == 'GRU-FW1PKLG':
                                sku = 'FW1-PK-LGCMC'
            
            
                        if "kyser" in brand.lower():
                            sku = sku.replace('KYS-', '')
                            split_sku = list(sku)
                            if split_sku[-1] != 'A':
                                sku = f'{sku}A'
                            sku = f'{sku}CMC'
            
                        if 'gibson' in brand.lower():
                            sku = sku.replace('GIB-', '')
                            sku = f'{sku}AUSTRALIS'
            
                        if brand.lower() == 'jbl':
                            sku = sku.replace('MK2', 'MKII')
                            sku = f'{sku}CMI'
            
                        if brand.lower() == 'lr baggs':
                            sku = sku.replace('LRB-', '')
            
                        if brand.lower() == "aguilar":
                            sku = sku.replace('AGU', '')
                            sku = f'{sku}CMI'
            
                        if 'helicon' in brand.lower():
                            if sku == 'TCH-GOXLR':
                                sku = '455104AUSTRALIS'
                            if sku == 'TCH-GOXLRMINI':
                                sku = '455106AUSTRALIS'
                            if sku == 'TCH-HARMSINGER2':
                                sku = '455107AUSTRALIS'
                            if sku == 'TCH-MICMECH2':
                                sku = '455111AUSTRALIS'
                            if sku == 'TCH-PERFORMVE':
                                sku = '455113AUSTRALIS'
                            if sku == 'TCH-PERFORMV':
                                sku = '455112AUSTRALIS'
                            if sku == 'TCE-TALKBOXSYNTH':
                                sku = '455120AUSTRALIS'
                            if sku == 'TCH-GOSOLO':
                                sku = '455101AUSTRALIS'
                            if sku == 'TCH-GOXLRMICB':
                                sku = '455142AUSTRALIS'
                            if sku == 'TCH-GOTWIN':
                                sku = '455102AUSTRALIS'
                            if sku == 'TCH-CRITICALMASS':
                                sku = '455094AUSTRALIS'
                            if sku == 'TCH-VTE1':
                                sku = '455125AUSTRALIS'
                            if sku == 'TCH-PERFORMVK':
                                sku = '455115AUSTRALIS'
                            if sku == 'TCH-HARMV100':
                                sku = '455108AUSTRALIS'
                            if sku == 'TCH-SWITCH6':
                                sku = '455119AUSTRALIS'
                            if sku == 'TCH-PERFORMVG':
                                sku = '455114AUSTRALIS'
                            if sku == 'TCH-GOVOCAL':
                                sku = '455103AUSTRALIS'
                            if sku == 'TCH-GOXLRMICW':
                                sku = '455141AUSTRALIS'
                            if sku == 'TCH-VLGIGBAG':
                                sku = '455098AUSTRALIS'
                            if sku == 'TCH-FX150BAG':
                                sku = '455097AUSTRALIS'
                            if sku == 'TCH-VTT1':
                                sku = '455128AUSTRALIS'
                            if sku == 'TCH-VLPLAYACSTC':
                                sku = '455116AUSTRALIS'
                            if sku == 'TCH-VL3EXTREME':
                                sku = '455121AUSTRALIS'
                            if sku == 'TCH-VLPLAY':
                                sku = '455122AUSTRALIS'
                            if sku == 'TCH-VTC1':
                                sku = '455123AUSTRALIS'
                            if sku == 'TCH-VTR1':
                                sku = '455127AUSTRALIS'
                            if sku == 'TCH-VTX1':
                                sku = '455129AUSTRALIS'
                            if sku == 'TCH-BLENDER':
                                sku = '455093AUSTRALIS'
                            if sku == 'TCH-SWITCH3':
                                sku = '455118AUSTRALIS'
                            if sku == 'TCH-DITTOMIC':
                                sku = '455095AUSTRALIS'
                            if sku == 'TCH-GTRHEADCA':
                                sku = '455143AUSTRALIS'
                            if sku == 'TCH-HARM-V60':
                                sku = '455109AUSTRALIS'
            
            
                        if brand.lower() == 'tech 21':
                            sku = sku.replace('T21-', '')
            
                        if brand.lower() == 'soundcraft':
                            sku = sku.replace('SOU-', 'SCF-')
                            sku = f'{sku}CMI'
            
                        if brand.lower() == 'universal audio':
                            sku = f'{sku}CMI'
            
            
                        sku = sku.replace('ORA-', '')
                        sku = sku.replace('ERN-E', '')
                        sku = sku.replace('KOR-', 'KO-')
            
            
            
                        if sku == 'PW-EGMK01':
                            sku = 'PW-EGMK-01'
                        if sku == 'PW-VG01':
                            sku = 'PW-VG-01'
                        if sku == 'PW-XLR801':
                            sku = 'PW-XLR8-01'
                        if sku == 'PW-CMIC10':
                            sku = 'PW-CMIC-10'
                        if sku == 'PW-CGT10':
                            sku = 'PW-CGT-10'
                        if sku == 'PW-AMSG10':
                            sku = 'PW-AMSG-10'
                        if sku == 'PW-SPL200':
                            sku = 'PWSPL200'
                        if sku == 'PW-ECK01':
                            sku = 'PW-ECK-01'
                        if sku == 'PW-CP07':
                            sku = 'PW-CP-07'
                        if sku == 'PW-S100':
                            sku = 'PWS100'
                        if sku == 'PW-DBPW01':
                            sku = 'PW-DBPW-01'
                        if sku == 'PW-CP02':
                            sku = 'PW-CP-02'
                        if sku == 'PW-CGTRA20':
                            sku = 'PW-CGTRA-20'
                        if sku == 'PW-CGTRA10':
                            sku = 'PW-CGTRA-10'
                        if sku == 'PW-25BL01':
                            sku = '25BL01'
                        if sku == 'PW-EBMK01':
                            sku = 'PW-EBMK-01'
                        if sku == 'PW-PL01':
                            sku = 'PW-PL-01'
                        if sku == 'PW-CMIC25':
                            sku = 'PW-CMIC-25'
                        if sku == 'PW-PL03':
                            sku = 'PW-PL-03'
                        if sku == 'PW-25BL00':
                            sku = '25BL00'
                        if sku == 'PW-S102':
                            sku = 'PWS102'
                        if sku == 'PW-25L00DX':
                            sku = '25L00DX'
                        if sku == 'PW-CGT20':
                            sku = 'PW-CGT-20'
                        if sku == 'PW-S101':
                            sku = 'PWS101'
                        if sku == 'PW-CMIC50':
                            sku = 'PW-CMIC-50'
                        if sku == 'PW-AMSG20':
                            sku = 'PW-AMSG-20'
                        if sku == 'PW-S105':
                            sku = 'PWS105'
                        if sku == 'PW-PL02':
                            sku = 'PW-PL-02'
                        if sku == 'PW-PWRKIT20':
                            sku = 'PW-PWRKIT-20'
                        if sku == 'PW-S108':
                            sku = 'PWS108'
                        if sku == 'PW-PC2':
                            sku = 'PWPC2'
                        if sku == 'PW-PC1':
                            sku = 'PWPC1'
                        if sku == 'PW-PW1':
                            sku = 'PWPW1'
                        if sku == 'PW-CT20':
                            sku = 'PW-CT-20'
                        if sku == 'PW-PW1B':
                            sku = 'PWPW1B'
            
            
            #########vvvvvvTC ELECTRONIC SKU SUBSTITUTEvvvvvvv################
                        if sku == 'TCE-SKYSURFMINI':
                            sku = '455133AUSTRALIS'
                        if sku == 'TCE-THEPROPHET':
                            sku = '455085AUSTRALIS'
                        if sku == 'TCE-TPDARKMATT':
                            sku = '455019AUSTRALIS'
                        if sku == 'TCE-PLETHORAX5':
                            sku = '455061AUSTRALIS'
                        if sku == 'TCE-SKYSURFER':
                            sku = '455074AUSTRALIS'
                        if sku == 'TCE-TPSPARK':
                            sku = '455075AUSTRALIS'
                        if sku == 'TCE-3RDDIMENSION':
                            sku = '455000AUSTRALIS'
                        if sku == 'TCE-TPSPARKMINI':
                            sku = '455076AUSTRALIS'
                        if sku == 'TCE-PLETHORAX3':
                            sku = '455150AUSTRALIS'
                        if sku == 'TCE-TUBEPILOT':
                            sku = '455087AUSTRALIS'
                        if sku == 'TCE-EYEMASTER':
                            sku = '455029AUSTRALIS'
                        if sku == 'TCE-TPSUBNUP':
                            sku = '455079AUSTRALIS'
                        if sku == 'TCE-ECHOBRAIN':
                            sku = '455027AUSTRALIS'
                        if sku == 'TCE-BRAINWAVES':
                            sku = '455010AUSTRALIS'
                        if sku == 'TCE-NETHER':
                            sku = '455059AUSTRALIS'
                        if sku == 'TCE-BLOODMOON':
                            sku = '455005AUSTRALIS'
                        if sku == 'TCE-AFTERGLOW':
                            sku = '455001AUSTRALIS'
                        if sku == 'TCE-MAGUSPRO':
                            sku = '455134AUSTRALIS'
                        if sku == 'TCE-CLARITYMSTE':
                            sku = '455015AUSTRALIS'
                        if sku == 'TCE-TPCORONA':
                            sku = '455016AUSTRALIS'
                        if sku == 'TCE-HONEYPOT':
                            sku = '455045AUSTRALIS'
                        if sku == 'TCE-IMPULSEIRLO':
                            sku = '455145AUSTRALIS'
                        if sku == 'TCE-FORCEFIELD':
                            sku = '455036AUSTRALIS'
                        if sku == 'TCE-RUSHBOOSTER':
                            sku = '455069AUSTRALIS'
                        if sku == 'TCE-ZEUSDRIVE':
                            sku = '455137AUSTRALIS'
                        if sku == 'TCE-VISCOUS':
                            sku = '455090AUSTRALIS'
                        if sku == 'TCE-TC8210DT':
                            sku = '455083AUSTRALIS'
                        if sku == 'TCE-RUSTYFUZZ':
                            sku = '455070AUSTRALIS'
                        if sku == 'TCE-TC2290DT':
                            sku = '455082AUSTRALIS'
                        if sku == 'TCE-MIMIQ':
                            sku = '455056AUSTRALIS'
                        if sku == 'TCE-SCFGOLD':
                            sku = '455148AUSTRALIS'
                        if sku == 'TCE-CLARITYM':
                            sku = '455014AUSTRALIS'
                        if sku == 'TCE-SUBNUPMINI':
                            sku = '455078AUSTRALIS'
                        if sku == 'TCE-ICONDOCK':
                            sku = '455131AUSTRALIS'
                        if sku == 'TCE-DRIPSPRING':
                            sku = '455024AUSTRALIS'
                        if sku == 'TCE-MOJOMOJOPG':
                            sku = '455138AUSTRALIS'
                        if sku == 'TCE-IRONCURTAIN':
                            sku = '455048AUSTRALIS'
                        if sku == 'TCE-DVR250DT':
                            sku = '455025AUSTRALIS'
                        if sku == 'TCE-BUCKETBRIG':
                            sku = '455146AUSTRALIS'
                        if sku == 'TCE-FANGS':
                            sku = '455030AUSTRALIS'
                        if sku == 'TCE-BAM200':
                            sku = '455022AUSTRALIS'
                        if sku == 'TCE-MASTERXHDDT':
                            sku = '455055AUSTRALIS'
                        if sku == 'TCE-CHOKA':
                            sku = '455012AUSTRALIS'
                        if sku == 'TCE-GRANDMAGUS':
                            sku = '455040AUSTRALIS'
                        if sku == 'TCE-CINDERS':
                            sku = '455013AUSTRALIS'
                        if sku == 'TCE-THUNDERSTORM':
                            sku = '455086AUSTRALIS'
                        if sku == 'TCE-DYN3000DT':
                            sku = '455026AUSTRALIS'
                        if sku == 'TCE-HELIX':
                            sku = '455044AUSTRALIS'
                        if sku == 'TCE-CRESCENDO':
                            sku = '455018AUSTRALIS'
                        if sku == 'TCE-ELMOCAMBO':
                            sku = '455028AUSTRALIS'
                        if sku == 'TCE-TC1210DT':
                            sku = '455081AUSTRALIS'
                        if sku == 'TCE-MONITORPILOT':
                            sku = '455149AUSTRALIS'
                        if sku == 'TCE-PEQ3000DT':
                            sku = '455144AUSTRALIS'
                        if sku == 'TCE-BRICKWLHDDT':
                            sku = '455011AUSTRALIS'
                        if sku == 'TCE-TAILSPIN':
                            sku = '455080AUSTRALIS'
                        if sku == 'TCE-CORONAM':
                            sku = '455017AUSTRALIS'
                        if sku == 'TCE-POLYTUNE3':
                            sku = '455062AUSTRALIS'
                        if sku == 'TCE-DITTOX4':
                            sku = '455023AUSTRALIS'
                        if sku == 'TCE-DITTOLOOPER':
                            sku = '455020AUSTRALIS'
                        if sku == 'TCE-PT3MINI':
                            sku = '455063AUSTRALIS'
                        if sku == 'TCE-TPHOF2':
                            sku = '455042AUSTRALIS'
                        if sku == 'TCE-TPFLASHBACK2':
                            sku = '455031AUSTRALIS'
                        if sku == 'TCE-INFINITESAMP':
                            sku = '455147AUSTRALIS'
                        if sku == 'TCE-PT3NOIRMINI':
                            sku = '455064AUSTRALIS'
                        if sku == 'TCE-DITTOJAMX2':
                            sku = '455139AUSTRALIS'
                        if sku == 'TCE-TPHOF2X4':
                            sku = '455043AUSTRALIS'
                        if sku == 'TCE-DITTOX2':
                            sku = '455022AUSTRALIS'
                        if sku == 'TCE-DITTOPLUS':
                            sku = '455130AUSTRALIS'
                        if sku == 'TCE-TPMOJO':
                            sku = '455058AUSTRALIS'
                        if sku == 'TCE-FLASHBACK2X4':
                            sku = '455033AUSTRALIS'
                        if sku == 'TCE-TPFB2MINI':
                            sku = '455032AUSTRALIS'
                        if sku == 'TCE-JUNE60V2':
                            sku = '455140AUSTRALIS'
                        if sku == 'TCE-TPHOF2MINI':
                            sku = '455041AUSTRALIS'
                        if sku == 'TCE-DITTOSTEREO':
                            sku = '455021AUSTRALIS'
                        if sku == 'TCE-HYPERGMINI':
                            sku = '455047AUSTRALIS'
                        if sku == 'TCE-QHARMONIZER':
                            sku = '455068AUSTRALIS'
                        if sku == 'TCE-FBTRIPLE':
                            sku = '455034AUSTRALIS'
                        if sku == 'TCE-HYPERG':
                            sku = '455046AUSTRALIS'
                        if sku == 'TCE-TALKBOXSYNTH':
                            sku = '455120AUSTRALIS'
            
                        #####vvvvvvvv ORANGE SKU SUBSTITUTES
                        if sku == 'CRUSH35RT':
                            sku = '8900042AUSTRALIS'
                        if sku == 'CRUSH12':
                            sku = '8900036AUSTRALIS'
                        if sku == 'CRUSH20':
                            sku = '2900038AUSTRALIS'
                        if sku == 'CRUSH20RT':
                            sku = '8900040AUSTRALIS'
                        if sku == 'CRUSHBASS25':
                            sku = '8900044AUSTRALIS'
                        if sku == 'ROCKER15':
                            sku = '8900030AUSTRALIS'
                        if sku == 'CRUSHBASS50':
                            sku = '8900045AUSTRALIS'
                        if sku == 'RK15T':
                            sku = '8900028AUSTRALIS'
                        if sku == 'PEDALBABY':
                            sku = '8900074AUSTRALIS'
                        if sku == 'SUPERCR100CM':
                            sku = '8900128AUSTRALIS'
                        if sku == 'PPC112':
                            sku = '8900054AUSTRALIS'
                        if sku == 'SUPERCR100':
                            sku = '8900126AUSTRALIS'
                        if sku == 'CRUSH20RTBK':
                            sku = '8900041AUSTRALIS'
                        if sku == 'MT20':
                            sku = '8900023AUSTRALIS'
                        if sku == 'CRUSH35RTBK':
                            sku = '8900043AUSTRALIS'
                        if sku == 'OR15':
                            sku = '8900019AUSTRALIS'
                        if sku == 'CRUSHMINI':
                            sku = '8900035AUSTRALIS'
                        if sku == 'DUALTERROR':
                            sku = '8900027AUSTRALIS'
                        if sku == 'PPC108':
                            sku = '8900053AUSTRALIS'
                        if sku == 'OBC112':
                            sku = '8900058AUSTRALIS'
                        if sku == 'CRUSH12BK':
                            sku = '8900037AUSTRALIS'
                        if sku == 'MDHEAD':
                            sku = '8900024AUSTRALIS'
                        if sku == 'CRUSH20BK':
                            sku = '8900039AUSTRALIS'
                        if sku == 'DA15H':
                            sku = '8900025AUSTRALIS'
                        if sku == 'PPC212OB':
                            sku = '8900056AUSTRALIS'
                        if sku == 'FURCOAT':
                            sku = '8900060AUSTRALIS'
                        if sku == 'SUPERCR100BK':
                            sku = '8900127AUSTRALIS'
                        if sku == '8900101':
                            sku = '8900101AUSTRALIS'
                        if sku == 'CRUSHBASSGH':
                            sku = '8900130AUSTRALIS'
                        if sku == 'AMPDETONATOR':
                            sku = '8900063AUSTRALIS'
                        if sku == '8900154':
                            sku = '8900154AUSTRALIS'
                        if sku == 'ACOUSTPEDAL':
                            sku = 'AUSTRALIS'
                        if sku == 'TERRORSTAMP':
                            sku = '8900107AUSTRALIS'
                        if sku == '8900155':
                            sku = '8900155AUSTRALIS'
                        if sku == '8900156':
                            sku = '8900156AUSTRALIS'
                        if sku == 'SUPERCR100CB':
                            sku = '8900129AUSTRALIS'
                        if sku == 'GETAWAY':
                            sku = '8900061AUSTRALIS'
                        if sku == 'FS2':
                            sku = '8900082AUSTRALIS'
                        if sku == 'TREMLORD30B':
                            sku = '8900076AUSTRALIS'
                        if sku == 'TREMLORD30':
                            sku = '8900075AUSTRALIS'
                        if sku == 'FS1MINI':
                            sku = '8900110AUSTRALIS'
                        if sku == 'CRUSHBASS100':
                            sku = '8900046AUSTRALIS'
                        if sku == 'OMECTELEPORT':
                            sku = '8900064AUSTRALIS'
                        if sku == '8900098':
                            sku = '8900098AUSTRALIS'
                        if sku == 'GUITARBUTLER':
                            sku = '8900143AUSTRALIS'
                        if sku == 'LITTLEBASST':
                            sku = '8900105AUSTRALIS'
                        if sku == 'TH30H':
                            sku = '8900020AUSTRALIS'
                        if sku == 'TERRORBASS':
                            sku = '8900047AUSTRALIS'
                        if sku == 'KONGPRESSOR':
                            sku = '8900059AUSTRALIS'
                        if sku == 'ROCKER32':
                            sku = '8900031AUSTRALIS'
                        if sku == 'FS1':
                            sku = '8900081AUSTRALIS'
                        if sku == 'OB1500':
                            sku = '8900051AUSTRALIS'
                        if sku == '4STROKE300':
                            sku = '8900048AUSTRALIS'
                        if sku == '4STROKE500':
                            sku = '8900049AUSTRALIS'
                        if sku == '8900102':
                            sku = '8900102AUSTRALIS'
                        if sku == 'CRPRO412':
                            sku = '8900057AUSTRALIS'
            
                        if brand.lower() == 'ernie ball':
                            sku = f'{sku}CMC'
                        if brand.lower() == 'korg':
                            sku = f'{sku}CMI'
                        
                        title = t.find(class_='product-title').text if t.find(class_='product-title') else "N/A"
                        price = "N/A"
                        
                        # Try to get price from listing page
                        price_element = t.find(class_='figures')
                        if price_element:
                            price = price_element.text.strip()
                            price = price.replace('\n', '')
                            price = price.replace('$', '')
                            price = price.replace(',', '')
                            
                        print(f'\nScraping Item {str(item_number)}\nSKU: {sku}\nTitle: {title}\nPrice: {price}\n')
                        
                        # Visit product page to get more details
                        max_retries = 3
                        for retry in range(max_retries):
                            try:
                                r = driver.get(url)
                                time.sleep(3)  # Wait for page load
                                break
                            except Exception as e:
                                if retry == max_retries - 1:
                                    raise
                                print(f"Retry {retry+1}/{max_retries} for {url}: {str(e)}")
                                time.sleep(5)
                                
                        html = driver.page_source
                        soup2 = BeautifulSoup(html, 'html.parser')
                        
                        # Extract stock availability 
                        stock_avaliable = 'n'
                        try:
                            stock_elements = soup2.find_all(class_=lambda c: c and 'stock' in c.lower())
                            for elem in stock_elements:
                                if elem.text and ('In Stock' in elem.text or 'Low Stock' in elem.text):
                                    stock_avaliable = 'y'
                                    break
                        except Exception as e:
                            print(f"Error checking stock: {str(e)}")
                            
                        # Get image URL
                        image = 'Not yet scraped'
                        try:
                            image_element = soup2.find(class_='gallery-cell is-selected')
                            if image_element:
                                image_link = image_element.find('a')
                                if image_link and 'href' in image_link.attrs:
                                    image = image_link['href']
                        except Exception as e:
                            print(f"Error getting image: {str(e)}")
                            
                        # Get product description
                        description = 'Not yet scraped'
                        try:
                            description = soup2.find(class_='station-tabs-content-inner').text
                        except:
                            description = 'N/A'
                            
                        # Get current date
                        today = datetime.now()
                        date = today.strftime('%m %d %Y')
                        
                        # Add to spreadsheet
                        sheet.append([sku, brand, title, price, url, image, description, date, stock_avaliable])
                        url_list.append(url)  # Add to our list to avoid duplicates
                        
                        print(f'Item {str(item_number)} scraped successfully')
                        
                        # Save periodically
                        if int(items_scrapped) % 5 == 0:
                            print(f'Saving Sheet... Please wait....')
                            try:
                                wb.save(file_path)
                                print("Sheet saved successfully")
                            except Exception as e:
                                print(f"Error occurred while saving the Excel file: {str(e)}")
                                
                        # Add a pause to be gentle with the server
                        time.sleep(3)
                        
                    except Exception as product_error:
                        print(f"Error processing product {item_number}: {str(product_error)}")
                        print(traceback.format_exc())
                        # Continue with next product even if this one fails
                
            except Exception as brand_error:
                print(f"Error processing brand {brand}: {str(brand_error)}")
                print(traceback.format_exc())
                # Continue with next brand even if this one fails
    
    # Final save
    wb.save(file_path)
    print(f"Scraping completed successfully. Added {items_scrapped} new items.")
    send_email_notification(True, items_scrapped)
    
except Exception as e:
    error_message = str(e)
    full_traceback = traceback.format_exc()
    print(f"Error in scraping: {error_message}")
    print(f"Traceback:\n{full_traceback}")
    
    try:
        wb.save(file_path)
        print("Saved progress before error")
    except Exception as save_error:
        print(f"Could not save progress after error: {str(save_error)}")
    
    send_email_notification(False, error_msg=f"{error_message}\n\nFull traceback:\n{full_traceback}")
    sys.exit(1)  # Exit with error code
finally:
    # Always close the driver
    try:
        driver.quit()
    except:
        pass
