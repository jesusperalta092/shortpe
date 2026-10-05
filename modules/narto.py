# -*- coding: utf-8 -*-
"""
Narto Drama - Modulo de logica (seccion DramaShorts)
=====================================================
Narto es un agregador que re-sirve contenido (via m3u8 abierto) de apps
como AnyReel. Extrae una serie con TODOS sus episodios de una sola pagina.

Estructura de datos:
  - Cada episodio: {number, title, play_url (m3u8 master), thumb_url}
  - Un solo fetch devuelve los N episodios

Uso:
  from modules import narto
  data = narto.fetch_serie('owned-by-my-fiance-s-daddy')
"""
import re
import requests

BASE = 'https://narto-drama.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
HEADERS = {'User-Agent': UA, 'Referer': BASE + '/'}


def _clean(html):
    """Des-escapar el JSON embebido en el HTML."""
    return html.replace('\\/', '/').replace('\\"', '"')


def fetch_serie(slug):
    """
    Descarga una serie completa desde Narto.
    slug: parte final de la URL (ej: 'owned-by-my-fiance-s-daddy')
    Devuelve {title, description, poster, episodes: {n: {m3u8, thumb, title}}}
    """
    url = f'{BASE}/detail/watch/{slug}/1?lang=es-ES'
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        return None
    h = _clean(r.text)

    # Titulo
    tm = re.search(r'<title>([^<]+?)(?:\s*(?:Episodio|Episode))', h)
    title = tm.group(1).strip() if tm else slug.replace('-', ' ').title()

    # Poster
    pm = re.search(r'og:image" content="([^"]+)"', h)
    poster = pm.group(1) if pm else ''

    # Descripcion
    dm = re.search(r'og:description" content="([^"]+?)(?:Emma|$)', h)
    desc = ''
    dm2 = re.search(r'"description" content="[^"]*?—\s*([^"]+)"', h)
    if dm2:
        desc = dm2.group(1)[:400]

    # Episodios: route_episode_number, title, play_url
    pairs = re.findall(
        r'"route_episode_number":(\d+),"number":(\d+),"title":"([^"]*)","play_url":"(https://[^"]+?\.m3u8)"',
        h
    )
    episodes = {}
    for route_n, num, ep_title, play_url in pairs:
        episodes[route_n] = {
            'number': int(num),
            'title': ep_title,
            'm3u8': play_url,
        }
    return {
        'slug': slug,
        'title': title,
        'description': desc,
        'poster': poster,
        'total_episodes': len(episodes),
        'episodes': episodes,
    }


def proxy_referer():
    return BASE + '/'
