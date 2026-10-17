from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')
for idx, s in enumerate(scripts):
    print(f"=== SCRIPT {idx} (type: {s.get('type')}) ===")
    content = s.string or s.text or ''
    print(content[:300])
