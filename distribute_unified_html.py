import os
import base64

# 1. Read the newly built JS bundle
with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/web/dist/assets/index-1GvPeIaz.js', 'r', encoding='utf-8') as f:
    bundle_js = f.read()

# 2. Read the latest autoos_interactive.html (with the fault sync handlers)
with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    cockpit_html = f.read()

# Encode cockpit HTML as Base64 for embedding
cockpit_b64 = base64.b64encode(cockpit_html.encode('utf-8')).decode('ascii')

# 3. Read autoos_unified.html template
with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/autoos_unified.html', 'r', encoding='utf-8') as f:
    unified_html = f.read()

# Replace embedded cockpit base64 string
b64_marker_start = 'var b64 = "'
idx_b64 = unified_html.find(b64_marker_start)
if idx_b64 != -1:
    idx_b64_end = unified_html.find('"', idx_b64 + len(b64_marker_start))
    unified_html = unified_html[:idx_b64 + len(b64_marker_start)] + cockpit_b64 + unified_html[idx_b64_end:]
    print("Embedded updated base64 cockpit into autoos_unified.html")
else:
    print("Warning: b64 marker not found in autoos_unified.html")

# Replace script content with the newly compiled bundle_js
script_marker = '<script type="module">'
idx_script = unified_html.find(script_marker)
if idx_script != -1:
    idx_script_end = unified_html.rfind('</script>')
    unified_html = unified_html[:idx_script + len(script_marker)] + '\n' + bundle_js + '\n    ' + unified_html[idx_script_end:]
    print("Injected new JS bundle into autoos_unified.html")
else:
    print("Warning: module script tag not found in autoos_unified.html")

# Save into all locations where autoos_unified.html is served from
destinations = [
    'C:/Users/Usuario/Desktop/mio/universidad/autoos/autoos_unified.html',
    'C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/autoos_unified.html',
    'C:/Users/Usuario/Desktop/mio/universidad/autoos/web/dist/autoos_unified.html',
    'C:/Users/Usuario/Desktop/mio/universidad/autoos/web/public/autoos_unified.html'
]

for dest in destinations:
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(unified_html)
    print("Saved:", dest, "Length:", len(unified_html))

print("All unified HTML files updated successfully!")
