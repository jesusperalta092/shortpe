import json
import requests

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

item = next((x for x in dramas if 'cutting-ties' in x.get('slug', '')), None)
if item:
    print('Title:', item.get('title'))
    print('Slug:', item.get('slug'))
    print('BookID:', item.get('bookId'))
    eps = item.get('episodes', {})
    print('Total eps in JSON:', len(eps))
    ep1_url = eps.get('1')
    print('Ep 1 Stream URL:', ep1_url)
    
    slug = item.get('slug')
    r_proxy = requests.get(f'http://127.0.0.1:8090/proxy/episode?slug={slug}&ep=1')
    print('Proxy /proxy/episode status:', r_proxy.status_code)
    if r_proxy.status_code == 200:
        p_data = r_proxy.json()
        p_url = p_data.get('player_url')
        print('Player url:', p_url)
        r_man = requests.get('http://127.0.0.1:8090' + p_url)
        print('Manifest status:', r_man.status_code, 'text snippet:', r_man.text[:300])
