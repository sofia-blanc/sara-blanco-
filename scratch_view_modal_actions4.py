with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = 1470640 + 11500
print(text[idx:idx+3500])
