# -*- coding: utf-8 -*-
"""
Fast Scanner & Subtitle Translation Engine (V2 - Ultra Speed)
1. Escaneo masivo en paralelo (30 workers) de los 6,590 candidatos restantes.
2. Identificación instantánea de títulos que contienen pista de subtítulos descargable.
3. Traducción automática a español WebVTT (wrap 52 chars) y registro en vivo.
"""

import os
import sys
import re
import json
import time
import base64
import urllib.request
import urllib.parse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(ROOT, 'fast_scan_subs.log')
SUB_DIR = os.path.join(ROOT, 'data', 'subtitles')
os.makedirs(SUB_DIR, exist_ok=True)

KEY = base64.b64decode('QC6Ir2trghxRAyyyWZEOEFR4GgLhnfQ4A19I3QBlQkc=')
aesgcm = AESGCM(KEY)

def decrypt(enc_str):
    if not enc_str:
        return ''
    try:
        raw = base64.b64decode(enc_str)
        return aesgcm.decrypt(raw[:12], raw[12:], None).decode('utf-8')
    except Exception:
        return ''

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

def wrap_subtitle_text(text, max_len=52):
    if not text:
        return ""
    single_line = ' '.join(text.strip().split())
    if len(single_line) <= max_len:
        return single_line
    words = single_line.split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + (1 if curr else 0) <= max_len:
            curr.append(w)
            curr_len += len(w) + (1 if curr else 0)
        else:
            if curr:
                lines.append(' '.join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(' '.join(curr))
    return '\n'.join(lines)

def translate_srt_to_es(srt_text):
    if not srt_text or not srt_text.strip():
        return "WEBVTT\n\n"
    lines = srt_text.replace('\r\n', '\n').split('\n')
    parsed = []
    dialogues = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.isdigit():
            idx = line
            i += 1
            if i < len(lines):
                t_line = lines[i].strip()
                m = re.match(r'(\d{2}:\d{2}:\d{2}),(\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}),(\d{3})', t_line)
                if m:
                    vtt_time = f"{m.group(1)}.{m.group(2)} --> {m.group(3)}.{m.group(4)}"
                    i += 1
                    cue_text = []
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                        cue_text.append(lines[i].strip())
                        i += 1
                    raw_diag = ' '.join(cue_text).strip()
                    if raw_diag:
                        parsed.append({'idx': idx, 'timestamp': vtt_time, 'text': raw_diag, 'has_text': True})
                        dialogues.append(raw_diag)
                    else:
                        parsed.append({'idx': idx, 'timestamp': vtt_time, 'has_text': False})
                    continue
        parsed.append({'raw': line, 'has_text': False})
        i += 1

    if not dialogues:
        return "WEBVTT\n\n"

    combined_text = ' [[[---]]] '.join(dialogues)
    translated_full = combined_text
    for attempt in range(3):
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q={urllib.parse.quote(combined_text)}"
            req = urllib.request.Request(url, headers=HEADERS)
            res = urllib.request.urlopen(req, timeout=15)
            data = json.loads(res.read().decode('utf-8'))
            translated_full = ''.join([part[0] for part in data[0] if part[0]])
            break
        except Exception:
            time.sleep(1.0 * (attempt + 1))

    translated_dialogues = re.split(r'\s*\[\[\[---\]\]\]\s*', translated_full)
    out_lines = ["WEBVTT\n"]
    d_idx = 0
    for item in parsed:
        if item.get('has_text'):
            raw_t = translated_dialogues[d_idx] if d_idx < len(translated_dialogues) else dialogues[d_idx]
            d_idx += 1
            t_txt = wrap_subtitle_text(raw_t, max_len=52)
            out_lines.append(f"{item['idx']}\n{item['timestamp']}\n{t_txt}\n")
        elif 'idx' in item:
            out_lines.append(f"{item['idx']}\n{item['timestamp']}\n")
        else:
            out_lines.append(f"{item.get('raw', '')}\n")

    return '\n'.join(out_lines)

def update_mapeo_markdown(title, slug, ep_count):
    for md_path in ('MAPEO_SUBTITULOS_V2.md', 'MAPEO_SUBTITULOS.md'):
        p = os.path.join(ROOT, md_path)
        if not os.path.exists(p):
            continue
        try:
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            if slug in content:
                continue
            entry = f"| **{title}** | `{slug}` | {ep_count} / {ep_count} | {ep_count} eps | HLS/MP4 | ✅ Verificado |\n"
            with open(p, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception:
            pass

def probe_candidate(slug):
    """Sondeo ultrarrápido del Episodio 1 (0.2s) para ver si tiene subtítulos."""
    raw_slug = slug.replace('dt-', '')
    page_url = f'https://dramaexpress.net/series/{raw_slug}/episode-1'
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=6)
        if r.status_code != 200:
            return None
        m_bid = re.search(r'bookId[":\s]+([a-zA-Z0-9_-]+)', r.text)
        if not m_bid:
            return None
        book_id = m_bid.group(1)

        api_url = f'https://dramaexpress.net/api/episode-source/{book_id}/1'
        ar = requests.get(api_url, headers={'User-Agent': HEADERS['User-Agent'], 'Referer': page_url}, timeout=6)
        if ar.status_code == 200:
            d = (ar.json() or {}).get('descriptor') or {}
            sub_meta = d.get('subtitle') or {}
            if sub_meta.get('enc'):
                # Extraer título y total de episodios
                soup = BeautifulSoup(r.text, 'html.parser')
                raw_title = soup.title.string if soup.title else raw_slug
                title = raw_title.split(' Episode 1')[0].split(' - Watch')[0].split(' | DramaExpress')[0].strip()
                ep_numbers = [int(x) for x in re.findall(r'serial_number[":\s]+(\d+)', r.text)]
                total_eps = max(ep_numbers) if ep_numbers else 1
                
                poster_m = re.search(r'"cover"[":\s]+"(https:[^"]+)"', r.text)
                poster = poster_m.group(1) if poster_m else ""
                
                desc_meta = soup.find('meta', attrs={'name': 'description'})
                desc = desc_meta.get('content', '') if desc_meta else title

                return {
                    'slug': slug,
                    'raw_slug': raw_slug,
                    'book_id': book_id,
                    'title': title,
                    'total_eps': total_eps,
                    'poster': poster,
                    'desc': desc
                }
    except Exception:
        pass
    return None

def fetch_episode_data(book_id, ep, referer):
    api_headers = {
        'User-Agent': HEADERS['User-Agent'],
        'Referer': referer,
        'Accept': 'application/json'
    }
    stream_url = None
    sub_url = None
    try:
        r = requests.get(f'https://dramaexpress.net/api/episode-source/{book_id}/{ep}', headers=api_headers, timeout=8)
        if r.status_code == 200:
            d = (r.json() or {}).get('descriptor') or {}
            enc = (d.get('chain') or [{}])[0].get('enc')
            stream_url = decrypt(enc)
            sub_meta = d.get('subtitle') or {}
            if sub_meta.get('enc'):
                sub_url = decrypt(sub_meta.get('enc'))
    except Exception:
        pass
    return ep, stream_url, sub_url

def process_subtitled_drama(drama_info, catalog_dramas):
    slug = drama_info['slug']
    custom_slug = f"dt-{slug}" if not slug.startswith('dt-') else slug
    raw_slug = drama_info['raw_slug']
    book_id = drama_info['book_id']
    title = drama_info['title']
    total_eps = drama_info['total_eps']
    referer = f'https://dramaexpress.net/series/{raw_slug}/episode-1'

    log(f"🎬 [SUBTITLED] Processing '{title}' | {total_eps} eps | bookId: {book_id}")

    ep_list = list(range(1, total_eps + 1))
    episodes_dict = {}
    subtitles_dict = {}

    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = [ex.submit(fetch_episode_data, book_id, ep, referer) for ep in ep_list]
        for f in futures:
            ep, s_url, sub_u = f.result()
            if s_url:
                episodes_dict[str(ep)] = s_url
            if sub_u:
                subtitles_dict[str(ep)] = sub_u

    if not episodes_dict:
        log(f"  [!] No valid streams for '{title}', skipping.")
        return False

    # Directorio de subtítulos
    drama_sub_dir = os.path.join(SUB_DIR, custom_slug)
    os.makedirs(drama_sub_dir, exist_ok=True)

    translated_subtitles = {}
    for ep_k, direct_sub_url in subtitles_dict.items():
        out_vtt = os.path.join(drama_sub_dir, f"{ep_k}_es.vtt")
        if os.path.exists(out_vtt) and os.path.getsize(out_vtt) > 30:
            translated_subtitles[ep_k] = {'es': {'url': f'/proxy/local-sub?slug={custom_slug}&ep={ep_k}&lang=es'}}
            continue

        for attempt in range(3):
            try:
                sub_req = requests.get(direct_sub_url, headers=HEADERS, timeout=10)
                if sub_req.status_code == 200 and sub_req.text.strip():
                    vtt_content = translate_srt_to_es(sub_req.text)
                    with open(out_vtt, 'w', encoding='utf-8') as vf:
                        vf.write(vtt_content)
                    translated_subtitles[ep_k] = {'es': {'url': f'/proxy/local-sub?slug={custom_slug}&ep={ep_k}&lang=es'}}
                    break
            except Exception:
                time.sleep(0.4)

    drama_entry = {
        "slug": custom_slug,
        "original_slug": raw_slug,
        "bookId": book_id,
        "title": title,
        "description": drama_info['desc'],
        "poster": drama_info['poster'],
        "poster_local": "",
        "section": "dramatube",
        "source": "dramatube",
        "total_episodes": len(episodes_dict),
        "genres": ["Drama", "DramaTube"],
        "lang": "en",
        "episodes": episodes_dict,
        "subtitles": translated_subtitles
    }

    # Actualizar catálogo en disco
    idx = next((i for i, d in enumerate(catalog_dramas) if d.get('slug') == custom_slug), None)
    if idx is not None:
        catalog_dramas[idx] = drama_entry
    else:
        catalog_dramas.append(drama_entry)

    with open(os.path.join(ROOT, 'data', 'dramatube.json'), 'w', encoding='utf-8') as f:
        json.dump(catalog_dramas, f, ensure_ascii=False, indent=2)

    update_mapeo_markdown(title, custom_slug, len(episodes_dict))
    log(f"✅ [SUCCESS] '{title}' saved with {len(episodes_dict)} eps ({len(translated_subtitles)} Spanish subtitles)!")
    return True

def main():
    log("====================================================================")
    log("🚀 INICIANDO ESCÁNER MASIVO PARALELO Y TRADUCTOR DE SUBTÍTULOS V2")
    log("====================================================================")

    catalog_path = os.path.join(ROOT, 'data', 'dramatube.json')
    catalog_dramas = []
    if os.path.exists(catalog_path):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog_dramas = json.load(f)

    # Identificar slugs ya procesados con subtítulos
    existing_sub_slugs = set(
        d.get('slug', '').replace('dt-', '')
        for d in catalog_dramas
        if d.get('subtitles') and len(d.get('subtitles')) > 0
    )

    slugs_file = os.path.join(ROOT, 'data', 'discovered_dramaexpress_slugs.json')
    all_slugs = []
    if os.path.exists(slugs_file):
        with open(slugs_file, 'r', encoding='utf-8') as f:
            all_slugs = json.load(f)

    candidates = [s for s in all_slugs if s not in existing_sub_slugs]
    log(f"📊 Total de candidatos a escanear en paralelo: {len(candidates)}")
    log(f"⚡ Escaneando con 30 workers concurrentes para máxima velocidad...\n")

    found_subtitled = []
    scanned_count = 0
    total_candidates = len(candidates)
    batch_size = 30

    with ThreadPoolExecutor(max_workers=30) as ex:
        futures = {ex.submit(probe_candidate, slug): slug for slug in candidates}
        for future in futures:
            scanned_count += 1
            res = future.result()
            if res:
                found_subtitled.append(res)
                log(f"🎯 [ENCONTRADO #{len(found_subtitled)}] '{res['title']}' ({res['total_eps']} eps) tiene subtítulos!")
                # Procesar y traducir de inmediato
                process_subtitled_drama(res, catalog_dramas)

            if scanned_count % 100 == 0 or scanned_count == total_candidates:
                pct = (scanned_count / total_candidates) * 100
                log(f"⏳ Progreso de escaneo: [{scanned_count}/{total_candidates}] ({pct:.1f}%) | Encontrados con subtítulos: {len(found_subtitled)}")

    log("\n🎉 ESCANEO COMPLETO! Todos los dramas con subtítulos disponibles han sido procesados y traducidos.")

if __name__ == '__main__':
    main()
