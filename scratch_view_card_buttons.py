with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = 1413654
print(text[idx-200:idx+1500])
