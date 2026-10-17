import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Let's test a popular English drama slug on kurzdrama.com/en/
en_sample_url = "https://www.kurzdrama.com/en/episodes/episode-1-the-double-life-of-my-billionaire-husband-64b52df3c510c4974900a653-m9y66f7f2b"
try:
    r = requests.get(en_sample_url, headers={'User-Agent': UA}, timeout=10)
    print("EN sample status:", r.status_code, "len:", len(r.text))
    # Check if there is an /es/ equivalent URL or spanish audio/subs
    print("Has /es/ link:", '/es/' in r.text)
    m = re.findall(r'href=["\']([^"\']+)["\']', r.text)
    es_links = [h for h in m if '/es/' in h]
    print("ES links in EN page:", es_links)
    
    # Try replacing /en/ with /es/
    es_try_url = en_sample_url.replace('/en/', '/es/')
    r_es = requests.get(es_try_url, headers={'User-Agent': UA}, timeout=10)
    print("Replacing /en/ with /es/ status:", r_es.status_code)
except Exception as e:
    print("Error:", e)
