import json, requests, re

# Load existing hotdrama
with open('data/hotdrama.json', encoding='utf-8') as f:
    current_items = json.load(f)

# The 13 working items identified
working_slugs = {
    'nt-besare-tus-cicatrices',
    'nt-consentida-del-senor-ferrer',
    'nt-doblada-dos-suenos-un-despertar',
    'nt-doblada-la-duena-del-karma',
    'nt-ecos-de-la-fatalidad',
    'nt-el-es-mas-apasionado-que-mi-ex',
    'nt-el-medico-divino-rodeado-de-siete-bellezas-2',
    'nt-esposa-del-magnate-oculto',
    'nt-mi-hermanastro-es-un-bad-boy',
    'nt-o-cesar-o-nada',
    'nt-playboy-el-verdadero-dios',
    'nt-the-golden-cage',
    'nt-un-pacto-me-unio-al-inmortal-supremo-1'
}

kept_items = [d for d in current_items if d['slug'] in working_slugs]
print(f"Keeping {len(kept_items)} verified working original items.")

# Load fresh verified playable titles
with open('scratch/fresh_playable_narto.json', encoding='utf-8') as f:
    fresh_playable = json.load(f)

headers = {'User-Agent': 'Mozilla/5.0'}

new_added = 0
target_new = 18  # to keep total at 31

for cand in fresh_playable:
    if new_added >= target_new:
        break
    s = cand['slug']
    narto_s = s[3:] if s.startswith('nt-') else s
    url = f"https://narto-drama.com/detail/watch/{narto_s}/1?lang=es-ES"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            continue
        m_raw = re.search(r'episodeItemsRaw\s*=\s*(\[.*?\]);', r.text)
        eps_count = 60
        if m_raw:
            try:
                eps_list = json.loads(m_raw.group(1))
                eps_count = len(eps_list)
            except:
                pass
        
        # Extract clean title
        title = cand['title']
        clean_title = re.sub(r'^\s*[\(\[]\s*doblado\s*[\)\]]\s*', '', title, flags=re.I).strip()
        if not clean_title:
            clean_title = title
        
        item = {
            "slug": s,
            "title": clean_title,
            "description": f"Ver serie completa {clean_title} doblada en español latino en alta definición HD gratis.",
            "poster": cand['poster'],
            "section": "hotdrama",
            "source": "narto",
            "total_episodes": eps_count,
            "genres": ["HotDrama", "Doblado", "Romance", "Drama"]
        }
        kept_items.append(item)
        new_added += 1
        print(f"[ADDED] {clean_title} ({s}) - {eps_count} eps")
    except Exception as e:
        print(f"Err {s}: {e}")

print(f"\nFinal HotDrama items count: {len(kept_items)}")

with open('data/hotdrama.json', 'w', encoding='utf-8') as f:
    json.dump(kept_items, f, indent=2, ensure_ascii=False)

print("data/hotdrama.json successfully updated!")
