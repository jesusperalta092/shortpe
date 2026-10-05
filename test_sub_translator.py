import urllib.request
import urllib.parse
import json
import re

def translate_text(text, source_lang='en', target_lang='es'):
    """Translates text from source_lang to target_lang using Google Translate API."""
    if not text.strip():
        return text
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    res = urllib.request.urlopen(req, timeout=10)
    data = json.loads(res.read().decode('utf-8'))
    return ''.join([part[0] for part in data[0] if part[0]])

def translate_srt(srt_content):
    """Parses SRT, translates all dialogue blocks, and preserves timestamps and indices."""
    blocks = re.split(r'\n\s*\n', srt_content.strip())
    translated_blocks = []
    
    # We can batch translate multiple dialogue lines together
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            idx = lines[0]
            timestamp = lines[1]
            dialogue = '\n'.join(lines[2:])
            translated_dialogue = translate_text(dialogue)
            translated_blocks.append(f"{idx}\n{timestamp}\n{translated_dialogue}")
        elif len(lines) == 2 and '-->' in lines[1]:
            idx = lines[0]
            timestamp = lines[1]
            translated_blocks.append(f"{idx}\n{timestamp}")
        else:
            translated_blocks.append(block)
            
    return '\n\n'.join(translated_blocks)

# Sample English SRT
sample_srt = """1
00:00:01,916 --> 00:00:03,625
God, I'm gonna miss
this once I'm married.

2
00:00:04,125 --> 00:00:05,375
Why do you have to
marry someone else?

3
00:00:05,500 --> 00:00:08,742
Finn Hartley

4
00:00:05,791 --> 00:00:06,541
That's Finn,

5
00:00:06,750 --> 00:00:07,625
the man I've
been secretly
in love with for years.
"""

print("=== ORIGINAL (ENGLISH SRT) ===")
print(sample_srt)

print("\n=== TRANSLATING TO SPANISH ===")
es_srt = translate_srt(sample_srt)
print(es_srt)
