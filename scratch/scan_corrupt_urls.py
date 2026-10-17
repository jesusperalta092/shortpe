import json
import glob
import os

print("=== CHECKING ALL DATA JSON FILES FOR DECRYPT-STREAM OR ${ ===")
for p in glob.glob('data/*.json'):
    text = open(p, encoding='utf-8').read()
    if 'decrypt-stream' in text:
        print(f"FOUND decrypt-stream in {p}")
    if '${' in text:
        print(f"FOUND ${{ in {p}")
    if 'api.sansekai' in text:
        print(f"FOUND api.sansekai in {p}")

print("Scan complete.")
