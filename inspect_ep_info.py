import requests, re

js = requests.get('https://netshort.com/_next/static/chunks/app/%5Blocale%5D/episode/%5Bepisode%5D/page-48d757af8be655a9.js', headers={'User-Agent': 'Mozilla/5.0'}).text

idx = js.find('/web/v4/short_play/episode_info')
if idx != -1:
    print(js[max(0, idx-200):min(len(js), idx+400)])
