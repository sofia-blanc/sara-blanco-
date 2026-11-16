"""
PERFECT REBUILD: Keep ALL original components (including ACM between GPS and st()),
only replace the OLD GPS section with new custom_js, and replace function st() with new app_js.

Structure:
  base_part [0:old_gps_start] = React lib + all original components (unchanged)
  middle_part [old_gps_start:old_st_section_start] = OLD GPS section -> REPLACED with new_custom_js
  app_part [old_st_section_start:end] = OLD function st() -> REPLACED with new_app_js

But we also need to keep the ACM and other components that were BETWEEN the GPS section
and the st() section in the old bundle!

Re-examining: The gap was 85086 chars (old GPS section to st() section).
Inside this gap: AlgorithmComparisonModal and NewProcessModal were defined.
But NewProcessModal IS in app_js (found in feature check), so only ACM is missing.

The ACM was in the ORIGINAL bundle portion (before our custom injection).
Let me check exactly:
- AlgorithmComparisonModal: pos 566232 in old working JS (640165 chars)
- Old GPS section starts: 504572
- Old st() section starts: 589658
So ACM (566232) is BETWEEN old GPS section (504572) and st() (589658).

New structure needed:
  base_part [0:old_gps_start]           = React lib + original components (OK)
  new_custom_js                          = NEW GPS section (haversine, etc.)
  acm_section [acm_start:old_st_start]  = ACM + other components between old GPS and st()
  new_app_js                             = NEW function st()
"""
import subprocess

with open('autoos_unified.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Use the CURRENT html which was last saved (640165 chars JS)
# Actually let's use a known good base - read the current autoos_unified to get the JS
# The current JS has: base_part(504572) + new_custom_js(93730) + new_app_js(50577) = 648880
# The OLD working JS had the ACM at pos 566232

# We need to go back to the OLD working JS. Let's reconstruct from what we know:
# OLD working JS structure:
#   [0:504572]       = base_part (React lib + components up to GPS section)
#   [504572:566232]  = OLD GPS section + stuff before ACM
#   [566232:589658]  = ACM + stuff after ACM before st()
#   [589658:640165]  = OLD function st() (broken)

# The new custom_js replaces [504572:old_st_start], and new_app_js replaces [old_st_start:end]
# But ACM is at [566232:589658] in the OLD js.
# After we replaced [504572:589658] with new_custom_js(93730 chars), ACM was lost.

# We need to also include the ACM portion. 
# ACM portion in OLD JS: wjs[566232:589658] = chars 566232 to 589658 of OLD working JS

# But we don't have the old working JS anymore (we overwrote autoos_unified.html).
# However, we DO have the orig_bundle.js which is the previous autoos_unified.html's JS.

with open('orig_bundle.js', 'r', encoding='utf-16') as f:
    orig_full = f.read()

print('orig_bundle.js length:', len(orig_full))
# orig_bundle was extracted from the OLD working HTML (before this session's fixes)
# It had the same structure as the working JS we analyzed

# Find ACM in orig_bundle
acm_pos_orig = orig_full.find('AlgorithmComparisonModal')
print('ACM in orig_bundle at:', acm_pos_orig)

# Find GPS section start in orig_bundle
rt_gps_comment = '// COMPONENT: GPS REAL-TIME SIMULATOR (rt_gps)'
gps_in_orig = orig_full.find(rt_gps_comment)
eq_before_gps_orig = orig_full.rfind('// ==========================================', 0, gps_in_orig)
print('GPS section in orig_bundle starts at:', eq_before_gps_orig)

# Find st() section in orig_bundle
st_header = 'var F = `/app/applet/src/App.tsx`;\nfunction st() {'
st_in_orig = orig_full.find(st_header)
eq_before_st_orig = orig_full.rfind('// ==========================================', 0, st_in_orig)
print('st() section in orig_bundle starts at:', eq_before_st_orig)

# Extract ACM section: from ACM pos back to nearest ===== before it
eq_before_acm = orig_full.rfind('// ==========================================', 0, acm_pos_orig)
print('ACM section in orig_bundle starts at:', eq_before_acm)
print('ACM section ends at:', eq_before_st_orig)

acm_section = orig_full[eq_before_acm:eq_before_st_orig]
print('ACM section length:', len(acm_section))
print('ACM section has AlgorithmComparisonModal:', 'AlgorithmComparisonModal' in acm_section)
print('ACM section has NewProcessModal:', 'NewProcessModal' in acm_section)

# Now read our new custom_js and app_js
with open('build_unified_bundle.py', 'r', encoding='utf-8') as f:
    build = f.read()

cj_start = build.find('custom_js = r"""') + 16
cj_end = build.find('"""', cj_start)
new_custom_js = build[cj_start:cj_end]

app_js_marker = 'app_js = r"""'
app_js_start_idx = build.find(app_js_marker) + len(app_js_marker)
app_js_end_idx = build.find('"""', app_js_start_idx)
new_app_js = build[app_js_start_idx:app_js_end_idx]

# Read current autoos_unified.html JS (which has correct base_part)
script_marker = '<script type="module">'
js_start_idx = html.find(script_marker) + len(script_marker)
js_end_idx = html.rfind('</script>')
current_js = html[js_start_idx:js_end_idx]

# Current JS structure: base_part(504572) + new_custom_js(93730) + new_app_js(50577+6)
# We need to find the base_part end in current_js
# The new_custom_js starts with our custom marker
custom_marker = '// ==========================================\n// ADDITIONAL LUCIDE ICONS'
custom_start_in_current = current_js.find(custom_marker)
print('\nCustom section starts in current_js at:', custom_start_in_current)

base_part = current_js[:custom_start_in_current]
print('Base part length:', len(base_part))

# Build final JS: base_part + new_custom_js + acm_section + new_app_js
final_js = base_part + new_custom_js + '\n' + acm_section + '\n' + new_app_js

ob = final_js.count('{')
cb = final_js.count('}')
op = final_js.count('(')
cp = final_js.count(')')
print('\nFINAL BALANCE:')
print('  {:', ob, '}:', cb, 'diff:', ob-cb)
print('  (:', op, '):', cp, 'diff:', op-cp)
print('  Length:', len(final_js))

checks = [
    ('haversineDistKm', 'GPS Haversine'),
    ('Configurador de Ruta', 'Route editor'),
    ('AUTOOS_HARDWARE_FAULT', 'Fault message handler'),
    ("userRole !== 'conductor'", 'Conductor guard'),
    ('rt_gps', 'GPS component'),
    ('SCHEDULER', 'Scheduler tab'),
    ('AlgorithmComparisonModal', 'ACM component'),
    ('NewProcessModal', 'New Process Modal'),
    ('INITIAL_VEHICLE_DEVICES', 'Device definitions'),
    ('createRoot', 'React createRoot'),
    ('function st()', 'App function'),
]
print('\nFeature checks:')
all_ok = True
for key, label in checks:
    ok = key in final_js
    if not ok: all_ok = False
    print('  ' + ('OK' if ok else 'MISSING') + ': ' + label)

if ob != cb or op != cp:
    print('\nERROR: Still imbalanced! NOT saving.')
    raise SystemExit(1)

print('\nSaving...')
with open('web/dist/assets/index-1GvPeIaz.js', 'w', encoding='utf-8') as f:
    f.write(final_js)

result = subprocess.run(['python', 'distribute_unified_html.py'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout[-1500:])
