import json, re

hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
for i, item in enumerate(hd[:10]):
    desc = item.get('description', '')
    d = re.sub(r'^Episode\s+\d+/\d+\s*[•·\-]\s*[^.]+\.\s*', '', desc, flags=re.I)
    d = re.sub(r'\.?\s*Narto Drama\s*[\-–].*$', '', d, flags=re.I)
    d = d.replace('&quot;', '"').strip()
    if d and not d.endswith(('.', '!', '?')): d += '...'
    print(f"{i+1}. {item['title']}\n   -> {d}\n")
