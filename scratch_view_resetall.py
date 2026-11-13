with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('handleResetAll')
print('handleResetAll at:', idx)
print(text[idx-50:idx+600])
