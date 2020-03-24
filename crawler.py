# -*- coding: utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import threading


req = requests.get('http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=13&ncvContSeq=&contSeq=&board_id=&gubun=')
req.encoding = 'utf-8'
html = req.text
soup = BeautifulSoup(html, 'html.parser')
div = soup.find('table', {'class': 'num'})
trs = div.find_all('tbody')[0].find_all('tr')
result = []
for tr in trs:
  city = tr.find('th').text
  tds = tr.find_all('td')
  if city == '전남':
    city = '전라남도'
  if city == '강원':
    city = '강원도'
  if city == '경남':
    city = '경상남도'
  if city == '경북':
    city = '경상북도'
  if city == '충북':
    city = '충청북도'
  if city == '충남':
    city = '충청남도'
  if city == '전북':
    city = '전라남도'
  if city == '제주':
    city = '제주도'
  if city == '경기':
    city = '경기도'
  result.append(
    {
      'city': str(city),
      'number': int(tds[1].text.replace(',', '')),
      'die': int(tds[3].text.replace(',', ''))
    }
  )
with open('region.json','w',encoding='utf-8') as f:
    json.dump(result, f)
