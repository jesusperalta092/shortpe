import requests
import re
import json
import os
import sys
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

BASE_URL = 'https://dramaexpress.net'

def get_page_links(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            links = set(a.get('href') for a in soup.find_all('a') if a.get('href'))
            return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return set()

def crawl_all():
    print("=== Crawling DramaExpress for Series Slugs ===")
    root_links = get_page_links(BASE_URL)
    
    # Identify all source and category paths
    sources = set()
    categories = set()
    all_series_slugs = set()
    
    for link in root_links:
        if link.startswith('/source/'):
            sources.add(link)
        elif link.startswith('/category/'):
            categories.add(link)
        elif link.startswith('/series/'):
            slug = link.replace('/series/', '').split('/')[0].split('?')[0]
            if slug:
                all_series_slugs.add(slug)
                
    print(f"Found {len(sources)} source hubs and {len(categories)} category hubs.")
    
    hub_urls = []
    # Add base sources & categories, and paginations (pages 1 to 10 for each)
    for s in sources:
        hub_urls.append(f"{BASE_URL}{s}")
        for p in range(2, 6):
            hub_urls.append(f"{BASE_URL}{s}/page/{p}")
            
    for c in categories:
        hub_urls.append(f"{BASE_URL}{c}")
        for p in range(2, 6):
            hub_urls.append(f"{BASE_URL}{c}/page/{p}")
            
    print(f"Total hubs to crawl: {len(hub_urls)}. Starting parallel crawl...")
    
    def process_hub(url):
        found = set()
        links = get_page_links(url)
        for l in links:
            if l.startswith('/series/'):
                slug = l.replace('/series/', '').split('/')[0].split('?')[0]
                if slug:
                    found.add(slug)
        return found

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_hub, hub_urls)
        for r_set in results:
            all_series_slugs.update(r_set)
            
    slug_list = sorted(list(all_series_slugs))
    print(f"\n[DONE] Discovered {len(slug_list)} UNIQUE series slugs on DramaExpress!")
    
    out_file = os.path.join('data', 'discovered_dramaexpress_slugs.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(slug_list, f, indent=2)
        
    print(f"Saved list to {out_file}")

if __name__ == '__main__':
    crawl_all()
