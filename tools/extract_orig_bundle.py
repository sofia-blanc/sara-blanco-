import os

with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/autoos_unified.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

marker = '<script type="module">'
s2 = text.find(marker) + len(marker) + 1
e2 = text.rfind('</script>')
bundle_js = text[s2:e2]

with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/orig_bundle.js', 'w', encoding='utf-16') as f:
    f.write(bundle_js)

print('Saved orig_bundle.js, length:', len(bundle_js))
