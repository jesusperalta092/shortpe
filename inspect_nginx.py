import requests, re

js = requests.get('https://netshort.com/_next/static/chunks/8000-e7b841909b9e1a44.js', headers={'User-Agent': 'Mozilla/5.0'}).text

idx = js.find('nginx-pm2')
if idx != -1:
    print(js[max(0, idx-100):min(len(js), idx+300)])
