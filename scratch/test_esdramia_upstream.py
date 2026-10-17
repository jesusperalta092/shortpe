import requests
import re
import json

UPSTREAM = 'https://esdramia.com'
slug = 'un-beso-me-volvio-invencible'
ep_i = 1
h = '335e7cacd401bb7b2a8a1bc714577020'

ep_ref = f'{UPSTREAM}/dramas/{slug}/{ep_i}'
hdrs = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Referer': ep_ref,
    'Accept': '*/*'
}

url = UPSTREAM + '/api/stream/' + h
print('Requesting stream API:', url)
try:
    r = requests.get(url, headers=hdrs, verify=False, timeout=10)
    print('Status:', r.status_code)
    print('Body:', r.text[:400])
except Exception as e:
    print('Error:', e)

print('\nTesting page ref:', ep_ref)
try:
    rp = requests.get(ep_ref, headers=hdrs, verify=False, timeout=10)
    print('Page status:', rp.status_code)
    m = re.findall(r'"hash":"([0-9a-f]{32})"', rp.text)
    print('Found hashes on page:', len(m), m[:3])
except Exception as e:
    print('Page error:', e)
