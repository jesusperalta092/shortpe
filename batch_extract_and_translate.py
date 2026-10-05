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

# Ensure unbuffered UTF-8 output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

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

LOG_FILE = 'dramatube_batch.log'

def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(formatted + '\n')
    except Exception:
        pass

def resolve_url(url):
    if not url:
        return url
    if '/e/s/' in url:
        try:
            jwt_part = url.split('/e/s/')[1].split('.')[0]
            padding = '=' * (-len(jwt_part) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(jwt_part + padding))
            if 'src' in decoded:
                url = decoded['src']
        except Exception:
            pass
    if not url.startswith('http://') and not url.startswith('https://'):
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('nd1/') or 'nsstorage' in url or 'toonshort' in url:
            url = 'https://video.toonshort.com/' + url.lstrip('/')
        else:
            url = 'https://' + url.lstrip('/')
    return url

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
        add_len = len(w) + (1 if curr else 0)
        if curr_len + add_len <= max_len:
            curr.append(w)
            curr_len += add_len
        else:
            if curr:
                lines.append(' '.join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(' '.join(curr))
    return '\n'.join(lines)

def translate_srt_to_es(srt_content):
    blocks = [b.strip() for b in re.split(r'\n\s*\n', srt_content.strip()) if b.strip()]
    parsed = []
    dialogues = []
    
    for b in blocks:
        lines = b.split('\n')
        if len(lines) >= 3 and '-->' in lines[1]:
            idx = lines[0]
            t = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', lines[1])
            txt = ' '.join([l.strip() for l in lines[2:] if l.strip()])
            parsed.append({'idx': idx, 'timestamp': t, 'has_text': True})
            dialogues.append(txt)
        elif len(lines) >= 2 and '-->' in lines[1]:
            idx = lines[0]
            t = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', lines[1])
            parsed.append({'idx': idx, 'timestamp': t, 'has_text': False})
        else:
            parsed.append({'raw': b, 'has_text': False})
            
    if not dialogues:
        return "WEBVTT\n\n"
        
    delimiter = "\n[[[---]]]\n"
    combined_text = delimiter.join(dialogues)
    
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

def update_mapeo_markdown(title, slug, ep_count, source="DramaTube (DramaExpress)"):
    for md_path in ('MAPEO_SUBTITULOS_V2.md', 'MAPEO_SUBTITULOS.md'):
        if not os.path.exists(md_path):
            continue
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if slug in content:
                continue
            entry = f"| **{title}** | `{slug}` | {ep_count} / {ep_count} | {ep_count} eps | HLS/MP4 | ✅ Verificado |\n"
            with open(md_path, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception:
            pass

def fetch_single_episode(book_id, ep, referer):
    api_headers = {
        'User-Agent': HEADERS['User-Agent'],
        'Referer': referer,
        'Accept': 'application/json'
    }
    stream_url = None
    subtitles = {}
    
    api_url_en = f'https://dramaexpress.net/api/episode-source/{book_id}/{ep}'
    try:
        r = requests.get(api_url_en, headers=api_headers, timeout=10)
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
        
    return ep, stream_url, subtitles

def process_drama_slug(slug, catalog_dramas):
    custom_slug = f"dt-{slug}" if not slug.startswith('dt-') else slug
    raw_slug = slug.replace('dt-', '')
    
    page_url = f'https://dramaexpress.net/series/{raw_slug}/episode-1'
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        raw_title = soup.title.string if soup.title else raw_slug
        title = raw_title.split(' Episode 1')[0].split(' - Watch')[0].split(' | DramaExpress')[0].strip()
        
        # Extract bookId
        book_id_match = re.search(r'bookId[\\"]*:\s*[\\"]*([a-zA-Z0-9_-]+)', r.text)
        if not book_id_match:
            return None
        book_id = book_id_match.group(1)
        
        # Extract total episodes
        ep_numbers = [int(x) for x in re.findall(r'serial_number[\\"]*:\s*(\d+)', r.text)]
        total_eps = max(ep_numbers) if ep_numbers else 1
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc = meta_desc.get('content', '') if meta_desc else ''
        
        poster_match = re.search(r'cover[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', r.text) or re.search(r'poster[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', r.text)
        poster = poster_match.group(1).replace(r'\/', '/') if poster_match else ''
        if not poster:
            og_img = soup.find('meta', property='og:image')
            if og_img and og_img.get('content'):
                poster = og_img['content']
                
        raw_genres = [g.text.strip() for g in soup.find_all('a', href=re.compile(r'/category/')) if g.text.strip()]
        genres = list(dict.fromkeys(raw_genres))
        
        log(f"🎬 Processing Drama: '{title}' | bookId: {book_id} | {total_eps} eps | slug: {custom_slug}")
        
        # Parallel fetch episode streams & subtitles
        episodes_dict = {}
        subtitles_dict = {}
        
        def ep_worker(ep_num):
            return fetch_single_episode(book_id, ep_num, page_url)
            
        with ThreadPoolExecutor(max_workers=10) as executor:
            ep_results = list(executor.map(ep_worker, range(1, total_eps + 1)))
            
        for ep_num, stream, subs in ep_results:
            if stream and 'goodbos' not in stream and 'shortdizilab' not in stream:
                episodes_dict[str(ep_num)] = stream
            if subs:
                subtitles_dict[str(ep_num)] = subs
                
        if not episodes_dict:
            log(f"  [!] No valid streams found for '{title}', skipping.")
            return None
            
        # Re-index episodes sequentially
        sorted_ep_keys = sorted(episodes_dict.keys(), key=lambda x: int(x) if x.isdigit() else 999999)
        reindexed_episodes = {}
        reindexed_subtitles = {}
        for new_idx, old_k in enumerate(sorted_ep_keys, start=1):
            s_idx = str(new_idx)
            reindexed_episodes[s_idx] = episodes_dict[old_k]
            if old_k in subtitles_dict:
                reindexed_subtitles[s_idx] = subtitles_dict[old_k]
                
        # Translate subtitles to Spanish
        out_sub_dir = os.path.join('data', 'subtitles', custom_slug)
        os.makedirs(out_sub_dir, exist_ok=True)
        
        def sub_worker(item):
            ep_k, sub_info = item
            out_vtt = os.path.join(out_sub_dir, f"{ep_k}_es.vtt")
            if os.path.exists(out_vtt) and os.path.getsize(out_vtt) > 50:
                return True
                
            raw_url = sub_info.get('en', {}).get('url') if isinstance(sub_info.get('en'), dict) else sub_info.get('en')
            if not raw_url:
                return False
                
            direct_url = resolve_url(raw_url)
            for attempt in range(3):
                try:
                    sub_req = requests.get(direct_url, headers=HEADERS, timeout=12)
                    if sub_req.status_code == 200 and sub_req.text.strip():
                        vtt_text = translate_srt_to_es(sub_req.text)
                        with open(out_vtt, 'w', encoding='utf-8') as sf:
                            sf.write(vtt_text)
                        if int(ep_k) % 10 == 0 or int(ep_k) == len(reindexed_subtitles):
                            log(f"    -> Translated sub Ep {ep_k}/{len(reindexed_subtitles)} for '{title}'")
                        return True
                except Exception as se:
                    if attempt == 2:
                        log(f"  [!] Subtitle translate error on ep {ep_k}: {se}")
                    time.sleep(0.5)
            return False

        with ThreadPoolExecutor(max_workers=8) as sub_exec:
            sub_results = list(sub_exec.map(sub_worker, reindexed_subtitles.items()))
            
        translated_count = sum(1 for r in sub_results if r)
                
        drama_entry = {
            "slug": custom_slug,
            "original_slug": raw_slug,
            "bookId": book_id,
            "title": title,
            "description": desc,
            "poster": poster,
            "poster_local": "",
            "section": "dramatube",
            "source": "dramatube",
            "total_episodes": len(reindexed_episodes),
            "genres": genres if genres else ["Drama", "Romance", "DramaTube"],
            "lang": "en",
            "episodes": reindexed_episodes,
            "subtitles": reindexed_subtitles
        }
        
        existing_idx = next((i for i, d in enumerate(catalog_dramas) if d.get('slug') == custom_slug), None)
        if existing_idx is not None:
            catalog_dramas[existing_idx] = drama_entry
        else:
            catalog_dramas.append(drama_entry)
            
        with open('data/dramatube.json', 'w', encoding='utf-8') as f:
            json.dump(catalog_dramas, f, ensure_ascii=False, indent=2)
            
        update_mapeo_markdown(title, custom_slug, len(reindexed_episodes))
        log(f"✅ [SUCCESS] '{title}' saved with {len(reindexed_episodes)} eps ({translated_count} Spanish subtitles)!")
        return custom_slug
    except Exception as e:
        log(f"  [ERROR] processing slug '{slug}': {e}")
        return None

def run_batch(target_count=100):
    catalog_path = 'data/dramatube.json'
    catalog_dramas = []
    if os.path.exists(catalog_path):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog_dramas = json.load(f)
            
    existing_slugs = set(d.get('slug', '').replace('dt-', '') for d in catalog_dramas if d.get('subtitles') and len(d.get('subtitles')) > 0)
    
    slugs_file = 'data/discovered_dramaexpress_slugs.json'
    discovered_slugs = []
    if os.path.exists(slugs_file):
        with open(slugs_file, 'r', encoding='utf-8') as f:
            discovered_slugs = json.load(f)
            
    log("============================================================")
    log("🚀 Starting Batch Ingestion & Translation Engine")
    log(f"Catalog currently has {len(catalog_dramas)} dramas ({len(existing_slugs)} with full subtitles).")
    log(f"Discovered slugs available in library: {len(discovered_slugs)}")
    log(f"Target count for this batch: {target_count}")
    log("============================================================\n")
    
    to_process = [s for s in discovered_slugs if s not in existing_slugs]
    log(f"Total new candidate slugs to process: {len(to_process)}")
    
    processed_count = 0
    for idx, slug in enumerate(to_process, start=1):
        if processed_count >= target_count:
            log(f"\n🎉 Reached target batch count of {target_count} dramas! Batch complete.")
            break
            
        log(f"\n[{idx}/{len(to_process)}] Batch Progress: ({processed_count}/{target_count}) -> Attempting '{slug}'")
        res = process_drama_slug(slug, catalog_dramas)
        if res:
            processed_count += 1
            time.sleep(0.5)

if __name__ == '__main__':
    batch_size = 100
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        batch_size = int(sys.argv[1])
    run_batch(batch_size)
