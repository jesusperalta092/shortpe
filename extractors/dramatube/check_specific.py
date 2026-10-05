import json, os, sys, requests

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

d = json.load(open('data/dramatube.json', encoding='utf-8'))
print(f"Total dramas in data/dramatube.json right now: {len(d)}")

# Check 5 broken examples from user screenshot:
# "30-Day Bride", "30 Days to Love the Mafia Queen", "7 Days to Erase", "99 Weddings to Leave Him"
check_titles = ["30-Day Bride", "30 Days to Love the Mafia Queen", "7 Days to Erase", "99 Weddings to Leave Him", "$5 Million Toyboy: The Heir's Revenge"]

for item in d:
    for t in check_titles:
        if t.lower() in item.get('title','').lower():
            print(f"Title: {item.get('title')}")
            print(f"  Slug: {item.get('slug')}")
            print(f"  Poster: {item.get('poster')}")
            print(f"  Episodes count: {item.get('total_episodes')}")
