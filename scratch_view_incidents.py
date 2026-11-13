with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('scen_camera_occlusion')
print('scen_camera_occlusion at:', idx)
print(text[idx-400:idx+600])
