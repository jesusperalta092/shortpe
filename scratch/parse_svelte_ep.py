import re
import json

with open('scratch/kurz_ep_raw.html', 'r', encoding='utf-8') as f:
    ep_html = f.read()

print("Length of ep_html:", len(ep_html))

# Search for m3u8 in ep_html
m3u8_links = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', ep_html)
print(f"M3U8 links found: {len(m3u8_links)}")
for l in m3u8_links[:5]:
    print("  ", l)

# Look for chapter / episode lists or numbers
chapter_matches = re.findall(r'chapter[_\s]*\w*[:=]\s*["\']?([^"\'\s,;]+)', ep_html, re.I)
print("Chapter matches sample:", chapter_matches[:10])

# Look for JSON arrays or objects
# Search for script with __sveltekit
svelte_scripts = re.findall(r'<script[^>]*>(.*?__sveltekit.*?)</script>', ep_html, re.DOTALL)
print("Svelte scripts in ep:", len(svelte_scripts))
if svelte_scripts:
    with open('scratch/svelte_ep.js', 'w', encoding='utf-8') as f:
        f.write(svelte_scripts[0])
    print("Saved scratch/svelte_ep.js (len:", len(svelte_scripts[0]), ")")
    
    # Search for all URLs in svelte_ep.js
    urls = re.findall(r'https?://[^\s"\'<>]+', svelte_scripts[0])
    print("URLs in svelte_ep.js:", len(urls))
    for u in set(urls)[:15]:
        print("  -", u)
        
    # Search for episode titles or numbers in svelte_ep.js
    ep_titles = re.findall(r'title["\']?:\s*["\']([^"\']+)["\']', svelte_scripts[0])
    print("Titles in svelte_ep.js:", ep_titles[:10])
    
    # Search for "episode" or "chapter" occurrences
    eps = re.findall(r'href["\']?:\s*["\'](/es/episodes/[^"\']+)["\']', svelte_scripts[0])
    print("Episode hrefs in svelte_ep.js:", len(eps), eps[:5])
