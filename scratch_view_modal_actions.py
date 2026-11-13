with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = 1470640
print(text[idx+1500:idx+4500])
