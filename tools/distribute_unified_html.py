import os
import base64
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Read JS bundle
bundle_path = BASE_DIR / "web" / "dist" / "assets" / "index-1GvPeIaz.js"
with open(bundle_path, "r", encoding="utf-8") as f:
    bundle_js = f.read()

# 2. Read cockpit HTML
cockpit_path = BASE_DIR / "web" / "public" / "autoos_interactive.html"
if not cockpit_path.exists():
    cockpit_path = BASE_DIR / "Auto" / "autoos_interactive.html"

with open(cockpit_path, "r", encoding="utf-8") as f:
    cockpit_html = f.read()

cockpit_b64 = base64.b64encode(cockpit_html.encode("utf-8")).decode("ascii")

# 3. Read template
target_unified = BASE_DIR / "Auto" / "autoos_unified.html"
with open(target_unified, "r", encoding="utf-8") as f:
    unified_html = f.read()

# Replace embedded cockpit base64
b64_marker_start = 'var b64 = "'
idx_b64 = unified_html.find(b64_marker_start)
if idx_b64 != -1:
    idx_b64_end = unified_html.find('"', idx_b64 + len(b64_marker_start))
    unified_html = unified_html[:idx_b64 + len(b64_marker_start)] + cockpit_b64 + unified_html[idx_b64_end:]
    print("Embedded updated base64 cockpit")

# Replace script module
script_marker = '<script type="module">'
idx_script = unified_html.find(script_marker)
if idx_script != -1:
    idx_script_end = unified_html.rfind('</script>')
    unified_html = unified_html[:idx_script + len(script_marker)] + '\n' + bundle_js + '\n    ' + unified_html[idx_script_end:]
    print("Injected new JS bundle")

# Save directly to Auto/autoos_unified.html (single canonical runtime file)
with open(target_unified, "w", encoding="utf-8") as f:
    f.write(unified_html)
print(f"Saved: {target_unified} (Length: {len(unified_html)})")
