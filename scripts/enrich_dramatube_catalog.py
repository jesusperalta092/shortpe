import json
import os
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
HEADERS = {'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}

# 1. Load existing dramatube.json
with open(os.path.join(DATA_DIR, 'dramatube.json'), 'r', encoding='utf-8') as f:
    dramas = json.load(f)

dramas_by_slug = {d['slug']: d for d in dramas}
dramas_by_bid = {d['bookId']: d for d in dramas}

print(f"Current dramas count: {len(dramas)}")

# 2. Define the 8 hero banner dramas from line 87
banner_dramas = [
    {
        'title': 'Rechazando a mis cinco compañeras destinadas',
        'bookId': '6aa264b8d2473d18400b0f62',
        'book_slug': 'rechazando-a-mis-cinco-companeras-destinadas-6aa264b8d2473d18400b0f62',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/304201150000006731/e07aa41f-9c2f-47a2-8f74-6a801e1bc598.jpg',
        'total_episodes': 50,
        'first_slug': 'episode-1-rechazando-a-mis-cinco-compañeras-destinadas-6aa264b8d2473d18400b0f62-bx48r7ykrr'
    },
    {
        'title': 'Me acosté con mi cuñado',
        'bookId': '6a97c8228a52aa55360a1640',
        'book_slug': 'me-acoste-con-mi-cunado-6a97c8228a52aa55360a1640',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/304201150000006360/c78bd74e-9fd9-4203-a995-13d3f52cbf11.jpg',
        'total_episodes': 45,
        'first_slug': 'episode-1-me-acosté-con-mi-cuñado-6a97c8228a52aa55360a1640-dxar572zug'
    },
    {
        'title': 'El gran y poderoso genio',
        'bookId': '6a702f0f85d596905908bd4b',
        'book_slug': 'el-gran-y-poderoso-genio-6a702f0f85d596905908bd4b',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/304201150000005664/9178340e-b0a1-4fc1-92f1-df7112395b1b.jpg',
        'total_episodes': 51,
        'first_slug': 'episode-1-el-gran-y-poderoso-genio-6a702f0f85d596905908bd4b-qfp5veeekn'
    },
    {
        'title': 'Reclamada por el príncipe: la nodriza prohibida',
        'bookId': '6ab09f6daa2a106dd40439b4',
        'book_slug': 'reclamada-por-el-principe-la-nodriza-prohibida-6ab09f6daa2a106dd40439b4',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/304201150000005248/3b0b701d-c01d-4b29-a707-2a7dc0699e00.jpg',
        'total_episodes': 50,
        'first_slug': 'episode-1-reclamada-por-el-príncipe-la-nodriza-prohibida-6ab09f6daa2a106dd40439b4-322hkp3wvo'
    },
    {
        'title': 'El Alfa y su niñera Luna',
        'bookId': '6a9e4c6b47fadcb5140bccec',
        'book_slug': 'el-alfa-y-su-ninera-luna-6a9e4c6b47fadcb5140bccec',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/304201150000007497/e50141e5-069d-4fd3-a44e-d4b174476488.jpg',
        'total_episodes': 50,
        'first_slug': 'episode-1-el-alfa-y-su-niñera-luna-6a9e4c6b47fadcb5140bccec-8iz72gfxu0'
    },
    {
        'title': 'Me enamoré del mafioso que salvé',
        'bookId': '6ab0d9d308b46709f40cc867',
        'book_slug': 'me-enamore-del-mafioso-que-salve-6ab0d9d308b46709f40cc867',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/304201150000005411/6feb1015-7b78-4174-9e53-be14fb9d7742.jpg',
        'total_episodes': 54,
        'first_slug': 'episode-1-me-enamoré-del-mafioso-que-salvé-6ab0d9d308b46709f40cc867-h6rw2enq17'
    },
    {
        'title': 'Has sido reemplazado, primer amor',
        'bookId': '6a71c635347ecd322703a8b1',
        'book_slug': 'has-sido-reemplazado-primer-amor-6a71c635347ecd322703a8b1',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/304200150000006093/68a222cc-1b44-47d2-8856-371e0535f90c.jpg',
        'total_episodes': 73,
        'first_slug': 'episode-1-has-sido-reemplazado-primer-amor-6a71c635347ecd322703a8b1-4wz9x38ee1'
    },
    {
        'title': 'La CEO y El Padre Secreto De Su Hija',
        'bookId': '69def15860013c77e9047fdd',
        'book_slug': 'la-ceo-y-el-padre-secreto-de-su-hija-69def15860013c77e9047fdd',
        'poster': 'https://v-img.crazymaplestudios.com/v-images/book_cover_batch/300000000300002502/ce168b03-cbc3-4a7d-a381-eb9adca60729.jpg',
        'total_episodes': 74,
        'first_slug': 'episode-1-la-ceo-y-el-padre-secreto-de-su-hija-69def15860013c77e9047fdd-bi7w1eesuk'
    }
]

# Scrape episodes for any banner drama not yet added
for b in banner_dramas:
    slug = f"dt-{b['book_slug']}"
    if slug not in dramas_by_slug and b['bookId'] not in dramas_by_bid:
        print(f"Adding new banner drama: {b['title']}")
        # Scrape episode list
        eps = {}
        try:
            url = f"https://www.reelshort.com/es/full-episodes/{b['book_slug']}"
            r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    h = a['href']
                    if '/episodes/' in h:
                        ep_slug = h.split('/episodes/')[-1].strip('/')
                        num_m = re.search(r'episode-(\d+)', ep_slug, re.IGNORECASE)
                        num = int(num_m.group(1)) if num_m else 0
                        if num > 0:
                            eps[str(num)] = {
                                'number': num,
                                'slug': ep_slug,
                                'title': a.get_text(strip=True) or f"Episodio {num}",
                                'm3u8': ''
                            }
        except Exception as e:
            print("Error scraping banner drama eps:", e)

        # Fallback if eps empty
        if not eps:
            for i in range(1, b['total_episodes'] + 1):
                eps[str(i)] = {'number': i, 'slug': f"episode-{i}-{b['book_slug']}", 'title': f"Episodio {i}", 'm3u8': ''}

        item = {
            'slug': slug,
            'title': b['title'],
            'original_title': b['title'],
            'bookId': b['bookId'],
            'book_slug': b['book_slug'],
            'first_slug': b['first_slug'],
            'poster': b['poster'],
            'shelf': 'Nuevos Lanzamientos',
            'shelves': ['Nuevos Lanzamientos', 'CLASIFICACIÓN'],
            'source': 'kurzdrama',
            'section': 'dramatube',
            'total_episodes': len(eps) or b['total_episodes'],
            'collect_count': 100000,
            'episodes': eps
        }
        dramas.append(item)
        dramas_by_slug[slug] = item
        dramas_by_bid[b['bookId']] = item

print(f"Total dramas after banner additions: {len(dramas)}")

# 3. Categorization / Thematic tagging for "Ver más +" expansion
# Let's map each drama to all applicable shelves based on title keywords and themes!
THEME_RULES = {
    'Hombre Lobo 🐺 y Vampiro 🧛': ['alfa', 'lobo', 'loba', 'luna', 'licantropo', 'licántropo', 'vampiro', 'dragón', 'dragon', 'omega', 'bruja', 'mago'],
    'Bebés y Embarazos 🍼': ['embaraz', 'embarazada', 'bebe', 'bebé', 'hijo', 'hija', 'trillizos', 'niñera', 'ninera', 'nodriza', 'papá', 'papa', 'padre', 'di a luz', 'genes'],
    'Relación Tabú': ['tabú', 'tabu', 'cuñado', 'cunado', 'hermano', 'hermanastro', 'nodriza', 'prohibid', 'ex', 'exesposa', 'sirvienta', 'amante', 'escándalo', 'escandalo', 'mafia', 'virgen', 'rebelde'],
    'Identidad Oculta 🎭': ['ocult', 'secreto', 'secreta', 'sirvienta', 'duquesa', 'guardaespaldas', 'falso', 'falsa', 'doble', 'indigente', 'pobre', 'disfraz', 'millonario', 'multimillonario', 'ceo', 'magnate', 'jefe', 'don', 'soberano'],
    'Amor a Primera Vista 👄': ['amor', 'vista', 'enamor', 'casad', 'matrimonio', 'esposa', 'esposo', 'novia', 'novio', 'boda', 'votos', 'superestrella', 'corazón', 'corazon'],
    'Género Masculino': ['don', 'rey', 'hombre', 'varón', 'varon', 'piloto', 'superhéroe', 'superheroe', 'simp', 'dante', 'guerrero', 'apocalipsis', 'hechicero', 'dios de la guerra', 'infernal'],
    'Historias de Asia 🌏': ['asia', 'general', 'reina', 'emperador', 'sol', 'destino', 'mentiras', 'todo claro', 'magnates', 'divorcio', 'quiebra']
}

for d in dramas:
    t = d['title'].lower()
    sh_list = d.get('shelves', [d.get('shelf', 'General')])
    
    for theme_name, keywords in THEME_RULES.items():
        if any(kw in t for kw in keywords):
            if theme_name not in sh_list:
                sh_list.append(theme_name)
    
    # All dramas can also be in Más Recomendados if high collect
    if int(d.get('collect_count', 0)) > 50000:
        if 'Más Recomendados' not in sh_list:
            sh_list.append('Más Recomendados')
        if 'CLASIFICACIÓN' not in sh_list:
            sh_list.append('CLASIFICACIÓN')
            
    d['shelves'] = sh_list

# Save enriched dramatube.json
with open(os.path.join(DATA_DIR, 'dramatube.json'), 'w', encoding='utf-8') as f:
    json.dump(dramas, f, ensure_ascii=False, indent=2)

print(f"Saved {len(dramas)} dramas to dramatube.json")

# 4. Build shelves structure with both "featured" (top 10 for carousel) and "all_items" (for Ver más +)
shelves_order = [
    ('Nuevos Lanzamientos', '✨'),
    ('CLASIFICACIÓN', '🏆'),
    ('Serie Doblada 📢', '📢'),
    ('Identidad Oculta 🎭', '🎭'),
    ('Relación Tabú', '💋'),
    ('Bebés y Embarazos 🍼', '🍼'),
    ('Amor a Primera Vista 👄', '👄'),
    ('Género Masculino', '⚡'),
    ('Hombre Lobo 🐺 y Vampiro 🧛', '🐺'),
    ('Historias de Asia 🌏', '🌏'),
    ('Más Recomendados', '🔥')
]

shelves_data = []
for sh_name, icon in shelves_order:
    matched = [d for d in dramas if sh_name in d.get('shelves', [])]
    # If fewer than 10, fill with recommended
    if len(matched) < 10:
        for d in dramas:
            if d not in matched:
                matched.append(d)
            if len(matched) >= 10:
                break
                
    slug = re.sub(r'[^a-z0-9]+', '-', sh_name.lower()).strip('-')
    
    # Featured top 10 items for carousel
    featured_items = [{
        'slug': x['slug'],
        'title': x['title'],
        'poster': x['poster'],
        'total_episodes': x['total_episodes'],
        'shelf': sh_name
    } for x in matched[:10]]
    
    # All items for "Ver más +" expansion
    all_shelf_items = [{
        'slug': x['slug'],
        'title': x['title'],
        'poster': x['poster'],
        'total_episodes': x['total_episodes'],
        'shelf': sh_name
    } for x in matched]
    
    shelves_data.append({
        'name': sh_name,
        'icon': icon,
        'slug': slug,
        'count': len(all_shelf_items),
        'items': featured_items,
        'all_items': all_shelf_items
    })
    print(f"  {icon} {sh_name}: {len(featured_items)} featured in carousel, {len(all_shelf_items)} total for 'Ver más +'")

with open(os.path.join(DATA_DIR, 'dramatube_shelves.json'), 'w', encoding='utf-8') as f:
    json.dump({'shelves': shelves_data, 'total_dramas': len(dramas)}, f, ensure_ascii=False, indent=2)

print("Saved updated dramatube_shelves.json successfully!")
