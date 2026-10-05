# -*- coding: utf-8 -*-
"""
NetShort (DramaShorts) - Modulo de logica
=========================================
Maneja la extraccion de datos de NetShort: playVoucher (MP4) + subtitulos VTT.

Estructura de datos:
  - playVoucher: URL directa del MP4 (con token que expira)
  - subtitleList: [{url, subtitleLanguage, format}]

Idiomas soportados (5): es_ES, en_US, pt_PT, ko_KR, zh_TW
"""
import re
import requests

# --- Configuracion ---
BASE = 'https://netshort.com'
LANG_PREF = 'es'  # idioma de la interfaz
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
HEADERS = {'User-Agent': UA, 'Referer': BASE + '/'}

# Idiomas de subtitulos que nos interesan
SUPPORTED_SUBS = {
    'es_ES': 'Español',
    'en_US': 'Inglés',
    'pt_PT': 'Portugués',
    'ko_KR': 'Coreano',
    'zh_TW': 'Chino',
}


def _rsc(html):
    """Extrae y une el RSC payload de Next.js."""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html)
    return ''.join(chunks).encode().decode('unicode_escape', errors='ignore')


def _clean_url(u):
    return u.replace('\\u0026', '&').replace('&amp;', '&')


def fetch_episode(slug_id, ep_num):
    """
    Descarga un episodio y devuelve {video_url, subtitles}.
    slug_id: id de la serie (ej: mi-jefa-esta-obsesionada-conmigo-2098613294512787458)
    ep_num: numero de episodio (1..N)
    """
    url = f'{BASE}/es/episode/{slug_id}-ep-{ep_num}'
    r = requests.get(url, headers=HEADERS, timeout=25)
    if r.status_code != 200:
        return None
    rsc = _rsc(r.text)
    # video
    vm = re.search(r'"playVoucher":"([^"]+)"', rsc)
    if not vm:
        return None
    video_url = _clean_url(vm.group(1))
    # subtitulos (solo los 5 idiomas)
    subtitles = {}
    for m in re.finditer(r'"url":"(https://cfcdn[^"]+)","format":"webvtt"[^}]*?"subtitleLanguage":"([a-zA-Z_\-]+)"', rsc):
        lang = m.group(2)
        if lang in SUPPORTED_SUBS:
            subtitles[lang] = _clean_url(m.group(1))
    return {'video_url': video_url, 'subtitles': subtitles}


def fetch_episode_list(slug_id, max_ep=100):
    """Devuelve la lista de numeros de episodios disponibles probando la pagina del ep 1."""
    # La pagina del ep1 contiene todos los episodeNo hasta cierto punto
    url = f'{BASE}/es/episode/{slug_id}-ep-1'
    r = requests.get(url, headers=HEADERS, timeout=25)
    rsc = _rsc(r.text)
    nums = sorted(set(int(n) for _, n in re.findall(r'"episodeId":"(\d+)","episodeNo":(\d+)', rsc)))
    # si no hay lista, asumir secuencial
    if not nums:
        nums = list(range(1, 2))
    return nums


def proxy_referer():
    """Referer necesario para descargar el MP4/VTT."""
    return BASE + '/'
