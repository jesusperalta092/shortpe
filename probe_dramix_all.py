import requests
import json
import time

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://dramix.tv/es/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1',
    'Origin': 'https://dramix.tv',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Content-Type': 'application/json'
}

def get_dramix_episode(slug, book_id, ep):
    payload = {
        "provider": "dramabox",
        "bookId": str(book_id),
        "episode": int(ep),
        "slug": slug,
        "locale": "es"
    }
    r_ticket = session.post('https://dramix.tv/api/playback/ticket', headers=headers, json=payload, timeout=10)
    if r_ticket.status_code != 200:
        return False, f"Ticket error {r_ticket.status_code}: {r_ticket.text}"
    ticket = r_ticket.json().get('ticket')
    
    play_headers = dict(headers)
    play_headers['Authorization'] = f'Playback {ticket}'
    play_url = f'https://dramix.tv/api/playback/dramabox/{book_id}/{ep}?lang=es&slug={slug}'
    r_play = session.post(play_url, headers=play_headers, timeout=10)
    if r_play.status_code != 200:
        return False, f"Play error {r_play.status_code}: {r_play.text}"
    
    data = r_play.json()
    video_url = data.get('video', {}).get('url')
    return True, video_url

print("Probing multiple episodes...")
for ep_num in [1, 2, 5, 10, 25, 51]:
    ok, res = get_dramix_episode('aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado', '42000027513', ep_num)
    if ok:
        print(f"  [OK] Ep {ep_num}: Exitoso -> {res[:70]}...")
    else:
        print(f"  [ERR] Ep {ep_num}: Fallo -> {res}")
    time.sleep(0.3)
