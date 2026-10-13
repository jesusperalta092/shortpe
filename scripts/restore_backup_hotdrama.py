import json, os, requests, concurrent.futures

backup_path = r'C:\Users\USER\Documents\Proyecto_Netflix_Dramas(backup)\data\hotdrama.json'
print("Cargando backup de:", backup_path)
backup_data = json.load(open(backup_path, encoding='utf-8'))

# Obtener los 31 slugs en español
out = __import__('subprocess').check_output(['git', 'show', '2feb1f7:data/hotdrama.json'], cwd='.')
c_2feb = json.loads(out.decode('utf-8'))
slugs_2feb = {d['slug'] for d in c_2feb}

spanish_items = [d for d in backup_data if d['slug'] in slugs_2feb]
print(f"Recuperados {len(spanish_items)} títulos en español de HotDrama")

os.makedirs('posters', exist_ok=True)
os.makedirs('web-next/public/posters', exist_ok=True)

def download_poster(item):
    slug = item['slug']
    poster_url = item.get('poster')
    local_rel = f"posters/{slug}.jpg"
    p1 = os.path.join('posters', f"{slug}.jpg")
    p2 = os.path.join('web-next', 'public', 'posters', f"{slug}.jpg")
    
    if poster_url and (not os.path.exists(p1) or os.path.getsize(p1) == 0):
        try:
            r = requests.get(poster_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(p1, 'wb') as f: f.write(r.content)
                with open(p2, 'wb') as f: f.write(r.content)
        except Exception as e:
            print(f"Error descargando poster de {slug}: {e}")
            
    if os.path.exists(p1) and os.path.getsize(p1) > 0:
        item['poster_local'] = local_rel
    return item

print("Descargando carátulas en paralelo...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    spanish_items = list(executor.map(download_poster, spanish_items))

# Guardar en data/hotdrama.json
with open('data/hotdrama.json', 'w', encoding='utf-8') as f:
    json.dump(spanish_items, f, ensure_ascii=False, indent=2)
print(f"Guardados {len(spanish_items)} items en data/hotdrama.json")

# Sincronizar en catalog_full.json
cat = json.load(open('catalog_full.json', encoding='utf-8'))
# Evitar duplicados por slug
cat_slugs = {d['slug'] for d in cat}
added = 0
for d in spanish_items:
    if d['slug'] not in cat_slugs:
        cat.append(d)
        cat_slugs.add(d['slug'])
        added += 1

with open('catalog_full.json', 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=2)
print(f"Sincronizados en catalog_full.json: +{added} items (total: {len(cat)})")
