import requests
import json
import re

url = 'https://www.kurzdrama.com/es'
hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}

r = requests.get(url, headers=hdrs, timeout=15)
with open('scratch/kurzdrama_home.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print('Saved HTML, length:', len(r.text))

# Check for Next.js data, script tags, API endpoints, etc.
if '__NEXT_DATA__' in r.text:
    print('Found __NEXT_DATA__!')
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
    if m:
        data = json.loads(m.group(1))
        with open('scratch/kurzdrama_next_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print('Next data saved. Keys:', data.keys())
        if 'props' in data:
            print('Props keys:', data['props'].keys())
            page_props = data['props'].get('pageProps', {})
            print('pageProps keys:', page_props.keys())

# Check for sample episode URL
sample_ep = 'https://www.kurzdrama.com/es/episodes/episode-1-unida-al-alfa-y-su-beta-6a433648a0263ac457025610-2az8aku8d1'
r_ep = requests.get(sample_ep, headers=hdrs, timeout=15)
with open('scratch/kurzdrama_sample_ep.html', 'w', encoding='utf-8') as f:
    f.write(r_ep.text)
print('Saved Sample Ep HTML, length:', len(r_ep.text))

if '__NEXT_DATA__' in r_ep.text:
    print('Found __NEXT_DATA__ in sample ep!')
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r_ep.text)
    if m:
        ep_data = json.loads(m.group(1))
        with open('scratch/kurzdrama_sample_ep_data.json', 'w', encoding='utf-8') as f:
            json.dump(ep_data, f, indent=2, ensure_ascii=False)
        print('Sample Ep next data saved. Keys:', ep_data.keys())
        if 'props' in ep_data:
            print('Ep Props keys:', ep_data['props'].keys())
            ep_page_props = ep_data['props'].get('pageProps', {})
            print('ep pageProps keys:', ep_page_props.keys())
