import requests
import json

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://dramix.tv/es/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1',
    'Origin': 'https://dramix.tv',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Content-Type': 'application/json'
}

payload = {
    "provider": "dramabox",
    "bookId": "42000027513",
    "episode": 1,
    "slug": "aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado",
    "locale": "es"
}

# 1. Pedir ticket
print("1. Requesting ticket...")
r_ticket = session.post('https://dramix.tv/api/playback/ticket', headers=headers, json=payload)
print(f"Ticket Status: {r_ticket.status_code}")
print(f"Ticket Response: {r_ticket.text}")

if r_ticket.status_code == 200:
    ticket_data = r_ticket.json()
    ticket = ticket_data.get('ticket')
    print(f"Got Ticket: {ticket[:30]}...")

    # 2. Pedir Playback con el ticket
    play_headers = dict(headers)
    play_headers['Authorization'] = f'Playback {ticket}'
    play_url = 'https://dramix.tv/api/playback/dramabox/42000027513/1?lang=es&slug=aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado'
    print(f"\n2. Requesting Playback: {play_url}")
    r_play = session.post(play_url, headers=play_headers)
    print(f"Playback Status: {r_play.status_code}")
    print(f"Playback Response:")
    print(r_play.text)

    try:
        data = r_play.json()
        with open('_dramix_playback_success.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass
