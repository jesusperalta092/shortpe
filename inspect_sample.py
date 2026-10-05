import re
import json

with open('sample_page.html', 'r', encoding='utf-8') as f:
    text = f.read()

print(f"Total HTML length: {len(text)}")

# Look for patterns
book_ids = re.findall(r'bookId[\\"\':\s]+([a-zA-Z0-9_-]{5,})', text)
print("Found bookIds:", set(book_ids))

titles = re.findall(r'title[\\"\':\s]+([a-zA-Z0-9\s,\'-]{5,})', text)
print("Found title candidates:", titles[:5])

# Find api calls
api_calls = re.findall(r'/api/[a-zA-Z0-9/_-]+', text)
print("Found API calls:", set(api_calls))

# Find next_f chunks
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', text)
print(f"Found {len(chunks)} Next.js push chunks.")
for i, c in enumerate(chunks):
    if 'episode' in c or 'bookId' in c or 'series' in c:
        print(f"Chunk {i} snippet: {c[:200]}")
