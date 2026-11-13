with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('AUTOOS_RESET_DEVICE')
print('AUTOOS_RESET_DEVICE at:', idx)
print(text[max(0, idx-100):idx+400])
