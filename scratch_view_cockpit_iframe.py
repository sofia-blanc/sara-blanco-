with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = 1552443
print(text[idx:idx+1500])
# Y busquemos donde se renderiza el iframe con srcDoc
idx2 = text.find('srcDoc', idx)
print('srcDoc at:', idx2)
if idx2 != -1:
    print(text[idx2-100:idx2+300])
