with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('var b64 =')
print('b64 at:', idx)
print(text[max(0, idx-100):idx+500])
# Y busquemos donde termina el string base64 y que hace despues con el
end_b64 = text.find('";', idx)
print('After b64 string:\n', text[end_b64:end_b64+600])
