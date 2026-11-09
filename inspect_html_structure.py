with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/autoos_unified.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

marker = '<script type="module">'
idx = text.find(marker)
print('Marker at:', idx)
print('Before marker ends with:', repr(text[idx-100:idx]))
end_script = text.rfind('</script>')
print('Last script tag ends at:', end_script, 'total length:', len(text))
print('After script tag:', repr(text[end_script:end_script+50]))
