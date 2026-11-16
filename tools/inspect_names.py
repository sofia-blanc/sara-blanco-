import sys

with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 1382670
s1 = text[pos-1000:pos+200]
pos2 = 1443894
s2 = text[pos2-1000:pos2+200]

with open('tools/comp_info.txt', 'w', encoding='utf-8') as out:
    out.write("--- HEALTH MATRIX ---\n")
    out.write(s1)
    out.write("\n\n--- FAULT SIMULATOR ---\n")
    out.write(s2)

print("Saved to tools/comp_info.txt")
