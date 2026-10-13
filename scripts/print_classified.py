import json, sys

sys.stdout.reconfigure(encoding='utf-8')
from classify_hotdramas import spanish_list, non_spanish_list

print("=== 31 SPANISH TITLES ===")
for i, d in enumerate(spanish_list):
    print(f"{i+1:2d}. {d.get('title')} ({d.get('slug')})")

print("\n=== NON-SPANISH SAMPLE ===")
for i, d in enumerate(non_spanish_list[:15]):
    print(f"{i+1:2d}. {d.get('title')}")
