import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("1. Checking /api/stats:")
r = requests.get('http://127.0.0.1:8090/api/stats', timeout=5)
print("Stats:", r.json())

print("\n2. Checking /api/dramatube/shelves:")
r_sh = requests.get('http://127.0.0.1:8090/api/dramatube/shelves', timeout=5)
sh_data = r_sh.json()
print("Shelves count:", len(sh_data.get('shelves', [])))
for s in sh_data.get('shelves', []):
    print(f"  {s.get('icon')} {s.get('name')}: {s.get('count')} items")

print("\n3. Checking target drama item:")
target_slug = 'dt-unida-al-alfa-y-su-beta-6a433648a0263ac457025610'
r_item = requests.get(f'http://127.0.0.1:8090/api/dramatube/item?slug={target_slug}', timeout=5)
item_data = r_item.json()
print("Target title:", item_data.get('title'), "total_episodes:", item_data.get('total_episodes'), "episodeKeys len:", len(item_data.get('episodeKeys', [])))

print("\n4. Checking episode 1 proxy resolution:")
r_ep = requests.get(f'http://127.0.0.1:8090/proxy/episode?slug={target_slug}&ep=1', timeout=8)
print("Episode 1 proxy response:", r_ep.status_code, r_ep.json())

print("\n5. Checking episode 10 proxy resolution (on-demand):")
r_ep10 = requests.get(f'http://127.0.0.1:8090/proxy/episode?slug={target_slug}&ep=10', timeout=8)
print("Episode 10 proxy response:", r_ep10.status_code, r_ep10.json())
