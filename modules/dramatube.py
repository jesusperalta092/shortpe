# -*- coding: utf-8 -*-
"""
DramaTube Module - DramaExpress HLS & Subtitles Integration
============================================================
Este módulo encapsula toda la lógica de obtención, desencriptado AES-GCM
y gestión de fuentes de video y subtítulos para los títulos de la sección DramaTube.

Estructura de datos:
  - Cada serie: slug, bookId, title, description, poster, episodes {1: m3u8_url}, subtitles {1: {en: {url, lang, format}}}
  - Datos almacenados de forma persistente en: data/dramatube.json

Uso:
  from modules import dramatube
  serie = dramatube.fetch_serie('craving-the-wrong-brother-2')
"""
import base64
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from concurrent.futures import ThreadPoolExecutor

KEY = base64.b64decode('QC6Ir2trghxRAyyyWZEOEFR4GgLhnfQ4A19I3QBlQkc=')
aesgcm = AESGCM(KEY)

BASE_URL = 'https://dramaexpress.net'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
HEADERS = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'dramatube.json')


def decrypt(enc_str):
    """Desencripta la cadena AES-GCM base64 de DramaExpress."""
    if not enc_str:
        return ''
    try:
        raw = base64.b64decode(enc_str)
        return aesgcm.decrypt(raw[:12], raw[12:], None).decode('utf-8')
    except Exception:
        return ''


def fetch_episode_source(book_id, ep_number, referer=None):
    """
    Obtiene la URL directa de video m3u8 y subtitulos de un episodio individual.
    """
    api_headers = {
        'User-Agent': UA,
        'Referer': referer or f'{BASE_URL}/series/',
        'Accept': 'application/json'
    }
    stream_url = None
    subtitles = {}

    # 1. Fetch default (English / Master)
    api_url = f'{BASE_URL}/api/episode-source/{book_id}/{ep_number}'
    try:
        r = requests.get(api_url, headers=api_headers, timeout=10)
        if r.status_code == 200:
            d = (r.json() or {}).get('descriptor') or {}
            enc = (d.get('chain') or [{}])[0].get('enc')
            stream_url = decrypt(enc)
            sub_meta = d.get('subtitle') or {}
            if sub_meta.get('enc'):
                sub_en = decrypt(sub_meta.get('enc'))
                if sub_en:
                    subtitles['en'] = {
                        'url': sub_en,
                        'lang': sub_meta.get('language', 'en-US'),
                        'format': sub_meta.get('format', 'srt'),
                        'label': 'English'
                    }
    except Exception:
        pass

    # 2. Fallback con lang=es si no vino stream
    if not stream_url:
        try:
            r = requests.get(f'{api_url}?lang=es', headers=api_headers, timeout=10)
            if r.status_code == 200:
                d = (r.json() or {}).get('descriptor') or {}
                enc = (d.get('chain') or [{}])[0].get('enc')
                stream_url = decrypt(enc)
        except Exception:
            pass

    return ep_number, stream_url, subtitles


PREFERRED_CDNS = [
    'dramaboxdb.com', 'goodshort.com', 'shorttv.live', 'mydramawave.com',
    'stardusttv.cc', 'farsunpteltd.com', 'crazymaplestudios.com', 'vigoo', 'alphashort'
]

def extract_best_poster(html_text, soup):
    candidates = re.findall(r'(https?:[\\/]+[^"\'\s>]+\.(?:jpg|jpeg|png|webp)[^"\'\s>]*)', html_text)
    cleaned = [c.replace(r'\/', '/').replace('\\', '') for c in candidates]
    
    # 1. Prefer stable CDN images
    for c in cleaned:
        for cdn in PREFERRED_CDNS:
            if cdn in c:
                return c.split('&amp;')[0]
                
    # 2. Cover / Poster regex
    pm = re.search(r'cover[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', html_text) or re.search(r'poster[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', html_text)
    if pm:
        p = pm.group(1).replace(r'\/', '/').replace('\\', '')
        if 'tiktokcdn' not in p:
            return p

    # 3. OG image
    og = soup.find('meta', property='og:image')
    if og and og.get('content') and 'tiktokcdn' not in og['content']:
        return og['content']

    # 4. Any other non-tiktok image
    for c in cleaned:
        if 'tiktokcdn' not in c and ('cover' in c or 'playlet' in c or 'chapter' in c or 'videobook' in c):
            return c.split('&amp;')[0]

    return cleaned[0] if cleaned else ''


def fetch_serie(slug):
    """
    Descarga la metadata completa y todos los episodios con subtítulos de un drama de DramaTube.
    """
    page_url = f'{BASE_URL}/series/{slug}/episode-1'
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        
        soup = BeautifulSoup(r.text, 'html.parser')
        raw_title = soup.title.string if soup.title else slug
        title = raw_title.split(' Episode 1')[0].split(' - Watch')[0].split(' | DramaExpress')[0].strip()

        desc = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content']

        book_id_match = re.search(r'bookId[\\"]*:\s*[\\"]*([a-zA-Z0-9_-]+)[\\"]*', r.text)
        if not book_id_match:
            return None
        book_id = book_id_match.group(1)

        poster = extract_best_poster(r.text, soup)

        ep_numbers = [int(x) for x in re.findall(r'serial_number[\\"]*:\s*(\d+)', r.text)]
        total_episodes = max(ep_numbers) if ep_numbers else 1

        episodes_dict = {}
        subtitles_dict = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_episode_source, book_id, ep, page_url) for ep in range(1, total_episodes + 1)]
            for fut in futures:
                ep_num, stream, subs = fut.result()
                if stream and 'goodbos' not in stream and 'shortdizilab' not in stream:
                    episodes_dict[str(ep_num)] = stream
                if subs:
                    subtitles_dict[str(ep_num)] = subs

        return {
            'slug': f'dt-{slug}',
            'original_slug': slug,
            'bookId': book_id,
            'title': title,
            'description': desc,
            'poster': poster,
            'poster_local': '',
            'section': 'dramatube',
            'source': 'dramatube',
            'total_episodes': len(episodes_dict),
            'genres': ['Drama', 'Romance', 'DramaTube'],
            'lang': 'en',
            'episodes': episodes_dict,
            'subtitles': subtitles_dict
        }
    except Exception as e:
        print(f"Error fetching DramaTube {slug}: {e}")
        return None


def get_catalog():
    """Carga el catálogo local de DramaTube desde data/dramatube.json."""
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []
