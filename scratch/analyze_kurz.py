import re
import json

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

with open('scratch/kurz_ep_raw.html', 'r', encoding='utf-8') as f:
    ep_html = f.read()

print("=== HOME ANALYSIS ===")
# Headings / Sections
sections = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', home_html, re.I)
print(f"Total headings ({len(sections)}):")
for s in sections:
    # strip html tags if any
    clean_s = re.sub(r'<[^>]+>', '', s).strip()
    if clean_s:
        print("  -", clean_s)

# Script tags in home
scripts = re.findall(r'<script([^>]*)>(.*?)</script>', home_html, re.DOTALL | re.I)
print(f"\nScripts in home ({len(scripts)}):")
for i, (attrs, body) in enumerate(scripts):
    body_clean = body.strip()
    print(f"Script {i} attrs: {attrs.strip()[:60]} | body_len: {len(body_clean)}")
    if len(body_clean) > 0 and len(body_clean) < 500:
        print("   Body:", body_clean[:200])
    elif 'self.__next_f' in body_clean or 'webpack' in body_clean or 'api' in body_clean.lower():
        print("   Key body snippet:", body_clean[:200])

print("\n=== EPISODE ANALYSIS ===")
title = re.findall(r'<title>(.*?)</title>', ep_html, re.I)
print("Title:", title)

# Videos, audio, iframe, m3u8, mp4, etc.
media_matches = re.findall(r'(https?://[^\s"\'<>]+\.(?:m3u8|mp4|webm|ts|mov)[^\s"\'<>]*)', ep_html, re.I)
print("Media matches:", media_matches)

# Look for json or data attributes
data_attrs = re.findall(r'data-[a-z0-9_-]+="([^"]+)"', ep_html, re.I)
print("Data attrs sample:", data_attrs[:5])

# Scripts in ep
ep_scripts = re.findall(r'<script([^>]*)>(.*?)</script>', ep_html, re.DOTALL | re.I)
print(f"\nScripts in ep ({len(ep_scripts)}):")
for i, (attrs, body) in enumerate(ep_scripts):
    body_clean = body.strip()
    print(f"Ep Script {i} attrs: {attrs.strip()[:60]} | body_len: {len(body_clean)}")
    if len(body_clean) > 0:
        print("   Snippet:", body_clean[:250])
