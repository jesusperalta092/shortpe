import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

line87 = None
for line in html.split('\n'):
    if '__sveltekit_spkrjw.resolve(1' in line:
        line87 = line
        break

if not line87:
    print("Could not find line87")
    sys.exit(0)

print(f"Line 87 length: {len(line87)}")

# Extract all book_id or ids
all_book_ids = set(re.findall(r'book_id:\s*["\']([a-f0-9]{24})["\']', line87))
print(f"Found {len(all_book_ids)} book_ids in line 87 banners/data")

# Extract all hex ids from hrefs
href_ids = set(re.findall(r'([a-f0-9]{24})', line87))
print(f"Total hex 24 IDs in line 87: {len(href_ids)}")

# Extract all titles
titles = re.findall(r'\.title\s*=\s*["\']([^"\']+)["\']', line87)
print(f"Total .title assignments in line 87: {len(titles)}")

# Also extract banner titles
banner_titles = re.findall(r'book_title:\s*["\']([^"\']+)["\']', line87)
print(f"Total banner book_titles: {len(banner_titles)}")
for bt in banner_titles:
    print("  Banner:", bt)
