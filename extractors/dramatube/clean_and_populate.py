import os, sys, json, re, requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.dramatube import fetch_episode_source, DATA_PATH, BASE_URL, HEADERS

ALL_SLUGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'dramaexpress_all_slugs.json')
all_slugs = json.load(open(ALL_SLUGS_FILE, encoding='utf-8'))

print(f"Total candidate slugs from sitemaps: {len(all_slugs)}")

def extract_verified_drama(slug):
    page_url = f'{BASE_URL}/series/{slug}/episode-1'
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 1. Extract true Title
        raw_title = soup.title.string if soup.title else slug
        title = raw_title.split(' Episode 1')[0].split(' - Watch')[0].split(' | DramaExpress')[0].strip()

        # 2. Extract true Description
        desc = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content']

        # 3. Extract exact BookId
        book_id_match = re.search(r'bookId[\\"]*:\s*[\\"]*([a-zA-Z0-9_-]+)[\\"]*', r.text)
        if not book_id_match:
            return None
        book_id = book_id_match.group(1)

        # 4. Extract true Poster strictly from og:image
        og = soup.find('meta', property='og:image')
        poster = og.get('content') if og else ''
        if not poster or 'tiktokcdn' in poster:
            # Skip items without a stable, permanent poster
            return None

        # Verify that the poster URL is actually alive and returns 200 image
        try:
            pr = requests.get(poster, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, stream=True)
            if pr.status_code != 200 or pr.headers.get('Content-Type','').startswith('text/html'):
                return None
        except Exception:
            return None

        # 5. Extract episode numbers
        ep_numbers = [int(x) for x in re.findall(r'serial_number[\\"]*:\s*(\d+)', r.text)]
        total_episodes = max(ep_numbers) if ep_numbers else 1

        # 6. Fetch Episode 1 to test stream validity first
        _, ep1_stream, ep1_subs = fetch_episode_source(book_id, 1, page_url)
        if not ep1_stream or 'goodbos' in ep1_stream or 'shortdizilab' in ep1_stream or 'tiktokcdn' in ep1_stream:
            return None

        # Quick check if ep1 stream is alive
        try:
            sr = requests.get(ep1_stream, headers={'User-Agent': 'Mozilla/5.0'}, timeout=6)
            if sr.status_code != 200 or len(sr.content) < 50:
                return None
        except Exception:
            return None

        # 7. Fetch all remaining episodes in parallel
        episodes_dict = {'1': ep1_stream}
        subtitles_dict = {'1': ep1_subs} if ep1_subs else {}
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(fetch_episode_source, book_id, ep, page_url) for ep in range(2, total_episodes + 1)]
            for fut in futures:
                ep_num, stream, subs = fut.result()
                if stream and 'goodbos' not in stream and 'shortdizilab' not in stream and 'tiktokcdn' not in stream:
                    episodes_dict[str(ep_num)] = stream
                if subs:
                    subtitles_dict[str(ep_num)] = subs

        if len(episodes_dict) < 1:
            return None

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
        return None


def run_clean_pipeline():
    print("=== Starting 100% Verified DramaTube Pipeline ===")
    
    # Load and keep only already verified items with unique, working posters
    verified_results = []
    seen_posters = set()
    seen_slugs = set()

    if os.path.exists(DATA_PATH):
        try:
            curr = json.load(open(DATA_PATH, encoding='utf-8'))
            for d in curr:
                p = d.get('poster', '')
                s = d.get('slug', '')
                # Filter out broken tiktokcdn, duplicates, or empty
                if p and 'tiktokcdn' not in p and 'Forbidden' not in d.get('title','') and p not in seen_posters and s not in seen_slugs:
                    try:
                        r = requests.get(p, headers={'User-Agent': 'Mozilla/5.0'}, timeout=4, stream=True)
                        if r.status_code == 200 and not r.headers.get('Content-Type','').startswith('text/html'):
                            # Also check episode 1 stream
                            ep1 = d.get('episodes', {}).get('1', '')
                            if ep1 and 'tiktokcdn' not in ep1 and 'goodbos' not in ep1:
                                verified_results.append(d)
                                seen_posters.add(p)
                                seen_slugs.add(s)
                    except Exception:
                        pass
        except Exception as e:
            print("Error reading current catalog:", e)

    print(f"Existing clean & verified dramas: {len(verified_results)}")

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(verified_results, f, ensure_ascii=False, indent=2)

    # Process pending slugs to find more 100% verified dramas
    remaining_slugs = [s for s in all_slugs if f'dt-{s}' not in seen_slugs]
    print(f"Scanning {len(remaining_slugs)} slugs for fresh valid titles...")

    batch_size = 12
    for i in range(0, len(remaining_slugs), batch_size):
        batch = remaining_slugs[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_slug = {executor.submit(extract_verified_drama, s): s for s in batch}
            for fut in as_completed(future_to_slug):
                s = future_to_slug[fut]
                try:
                    item = fut.result()
                    if item:
                        p = item.get('poster', '')
                        if p and p not in seen_posters:
                            seen_posters.add(p)
                            seen_slugs.add(item['slug'])
                            verified_results.append(item)
                            print(f"[{len(verified_results)}] [VERIFIED OK] {item['title']} ({item['total_episodes']} eps) | Poster: {p[:60]}...")
                            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                                json.dump(verified_results, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass

        print(f"Progress: {i + len(batch)}/{len(remaining_slugs)} scanned | {len(verified_results)} verified in catalog")

if __name__ == '__main__':
    run_clean_pipeline()
