import requests
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://dramix.tv/es/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1',
    'Origin': 'https://dramix.tv',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
})

# 1. Visitar la página para cookies
r0 = session.get('https://dramix.tv/es/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1')
print("Page visit cookies:", session.cookies.get_dict())

# 2. Pedir ticket si aplica
r_ticket = session.post('https://dramix.tv/api/playback/ticket', json={})
print("Ticket status:", r_ticket.status_code, r_ticket.text)

# 3. Pedir playback
play_url = 'https://dramix.tv/api/playback/dramabox/42000027513/1?lang=es&slug=aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado'
r_play = session.get(play_url)
print("\nPlayback status:", r_play.status_code)
print("Playback response:")
print(r_play.text[:2000])

try:
    data = r_play.json()
    with open('_dramix_playback_ep1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
except:
    pass
