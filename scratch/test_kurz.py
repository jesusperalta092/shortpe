import requests
import json
import re

hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}

# 1. Home
r = requests.get('https://www.kurzdrama.com/es', headers=hdrs, timeout=10)
print('Home HTTP:', r.status_code, 'len:', len(r.text))
has_next = '__NEXT_DATA__' in r.text
print('Home has __NEXT_DATA__:', has_next)

# 2. Sample Ep
ep_url = 'https://www.kurzdrama.com/es/episodes/episode-1-unida-al-alfa-y-su-beta-6a433648a0263ac457025610-2az8aku8d1'
r_ep = requests.get(ep_url, headers=hdrs, timeout=10)
print('Ep HTTP:', r_ep.status_code, 'len:', len(r_ep.text))
has_next_ep = '__NEXT_DATA__' in r_ep.text
print('Ep has __NEXT_DATA__:', has_next_ep)

if has_next:
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
    if m:
        d = json.loads(m.group(1))
        with open('scratch/kurz_home.json', 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print('Saved scratch/kurz_home.json')

if has_next_ep:
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r_ep.text)
    if m:
        d_ep = json.loads(m.group(1))
        with open('scratch/kurz_ep.json', 'w', encoding='utf-8') as f:
            json.dump(d_ep, f, ensure_ascii=False, indent=2)
        print('Saved scratch/kurz_ep.json')
with open('scratch/kurz_home_raw.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
print('Saved scratch/kurz_home_raw.html')

# Analyze home
home_titles = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r.text)
print('Home headings:', home_titles[:15])

# Look for links to drama / episodes
drama_links = set(re.findall(r'href="([^"]*(?:drama|episode|detail)[^"]*)"', r.text, re.I))
print('Drama links found in home:', len(drama_links), list(drama_links)[:8])

# Analyze sample episode
with open('scratch/kurz_ep_raw.html', 'r', encoding='utf-8') as f:
    ep_html = f.read()

ep_title = re.findall(r'<title>(.*?)</title>', ep_html, re.I)
print('Episode page title:', ep_title)

# Look for video URLs, m3u8, mp4, cdn
video_urls = set(re.findall(r'https?://[^\s"\'<>]+(?:\.m3u8|\.mp4|[^\s"\'<>]*stream[^\s"\'<>]*)', ep_html, re.I))
print('Video URLs in ep:', list(video_urls))

# Look for all script sources
script_srcs = re.findall(r'<script[^>]+src="([^"]+)"', ep_html)
print('Script srcs in ep:', script_srcs[:5])

# Look for JSON in scripts
inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', ep_html, re.DOTALL)
print('Inline scripts in ep count:', len(inline_scripts))
for i, sc in enumerate(inline_scripts):
    sc_clean = sc.strip()
    if 'video' in sc_clean.lower() or 'episode' in sc_clean.lower() or 'play' in sc_clean.lower() or '{' in sc_clean:
        print(f'Script {i} (len {len(sc_clean)}):', sc_clean[:200])

