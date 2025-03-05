import requests, math, openpyxl
from bs4 import BeautifulSoup
import pprint
from datetime import datetime, timedelta
import pandas as pd
from csv import reader
from openpyxl import Workbook
import csv
import re
CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

wb = Workbook()
ws = wb.active

url = "https://nationalmusic.com.au/export/datafeed/NM%20Web%20Data.csv"

df = pd.read_csv(url)
df.head()

df.to_csv(r'\\SERVER\Python\Pricing\Pricing Spreadsheets\Misc\National_Music.csv')

with open(r'\\SERVER\Python\Pricing\Pricing Spreadsheets\Misc\National_Music.csv', 'r', encoding='utf8') as f:


    for row in csv.reader(f):

        try:
            # if row[21] == 'N':
            #     continue

            sku = row[1]
            name = row[2]
            description = cleanhtml(row[3])
            description = description.replace('	', '\n')
            description = description.strip()
            brand = row[4]
            rrp = row[6]
            image1 = row[12]
            ws.append([sku, brand, name, rrp, '', image1, description])
        except:
            continue

wb.save(r'\\SERVER\Python\Pricing\Pricing Spreadsheets\National_Music.xlsx')

