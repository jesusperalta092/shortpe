from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
s4 = soup.find_all('script')[-1].text

print("Length of script 4:", len(s4))

# Let's find all URLs or hex IDs or episode links inside s4!
ep_links = re.findall(r'(/es/episodes/[^"\'\s,)]+)', s4)
print(f"Total /es/episodes/ links in Script 4: {len(ep_links)}")

hex_ids = re.findall(r'([a-f0-9]{24})', s4)
print(f"Total 24-hex IDs in Script 4: {len(hex_ids)}, unique: {len(set(hex_ids))}")

# Check banners
banners_m = re.findall(r'banners:\s*\[(.*?)\]\s*,\s*tabs:', s4)
print(f"Banners section found: {len(banners_m)}")

# Check tabs or categories
tabs_m = re.findall(r'tabs:\s*\[(.*?)\]', s4)
print(f"Tabs section found: {len(tabs_m)}")
