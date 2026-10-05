import requests, json

r = requests.get('http://127.0.0.1:8090/api/dramavibe/item?slug=dv-38783-claimed-by-three-alphas')
print("Status:", r.status_code)
d = r.json()
print("Title:", d.get('title'))
print("Total episodes:", d.get('total_episodes'))
print("Cover:", d.get('poster'))
print("Episodes count:", len(d.get('episodes', {})))

# Test episode 1 & episode 10
ep1 = requests.get('http://127.0.0.1:8090/proxy/episode?slug=dv-38783-claimed-by-three-alphas&ep=1')
print("Ep 1 status:", ep1.status_code, ep1.text[:120])
ep10 = requests.get('http://127.0.0.1:8090/proxy/episode?slug=dv-38783-claimed-by-three-alphas&ep=10')
print("Ep 10 status:", ep10.status_code, ep10.text[:120])
