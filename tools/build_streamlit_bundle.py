"""Publish a Vite production build to the self-contained Streamlit HTML bundle.

Usage (from repository root):
    cd web
    npm ci
    npm run build
    cd ..
    python tools/build_streamlit_bundle.py

This replaces the old tooling's hard-coded JS filename and missing orig_bundle.js.
No extra Python packages are required. No network calls are made.
"""
from __future__ import annotations

import base64
import re
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'web' / 'dist'
OUTPUT = ROOT / 'Auto' / 'autoos_unified.html'
COCKPIT = ROOT / 'web' / 'public' / 'autoos_interactive.html'
# AUTOOS V10: mismo bundle visual, distinto protocolo para hablar con Python.
COMPONENT_DIR = ROOT / 'Auto' / 'bridge_component'
COMPONENT_BOOTSTRAP = ROOT / 'tools' / 'streamlit_component_bootstrap.js'


def read_dist_asset(url: str) -> str:
    """Read only local build assets under dist, not absolute URLs or traversals."""
    url = unescape(url).split('?', 1)[0].split('#', 1)[0]
    if re.match(r'(?i)https?://', url) or url.startswith('//'):
        raise ValueError(f'Unexpected remote asset: {url}')
    rel = url.lstrip('/')
    asset = (DIST / rel).resolve()
    if not asset.is_relative_to(DIST.resolve()) or not asset.is_file():
        raise FileNotFoundError(f'No existe el recurso del build: {url} ({asset})')
    return asset.read_text(encoding='utf-8')


def build() -> None:
    index = DIST / 'index.html'
    if not index.is_file():
        raise SystemExit('No existe web/dist/index.html. Ejecuta cd web; npm ci; npm run build')
    if not COCKPIT.is_file():
        raise SystemExit('Falta web/public/autoos_interactive.html')
    html = index.read_text(encoding='utf-8')

    def inline_css(m: re.Match[str]) -> str:
        url = m.group(1)
        css = read_dist_asset(url)
        return '<style data-autoos-built-css="true">\n' + css.replace('</style', '<\\/style') + '\n</style>'

    css_re = re.compile(r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])(?=[^>]*\bhref=["\']([^"\']+\.css)["\'])[^>]*>', re.IGNORECASE)
    html, css_count = css_re.subn(inline_css, html)
    if not css_count:
        raise RuntimeError('El HTML compilado no contiene un CSS local de Vite para integrar.')

    def inline_js(m: re.Match[str]) -> str:
        url = m.group(1)
        js = read_dist_asset(url)
        # HTML parser must not terminate the tag on a JS string literal.
        js = re.sub(r'</script', r'<\\/script', js, flags=re.IGNORECASE)
        return '<script type="module" data-autoos-built-js="true">\n' + js + '\n</script>'

    js_re = re.compile(r'<script\b(?=[^>]*\btype=["\']module["\'])(?=[^>]*\bsrc=["\']([^"\']+\.js)["\'])[^>]*>\s*</script>', re.IGNORECASE)
    html, js_count = js_re.subn(inline_js, html)
    if js_count != 1:
        raise RuntimeError(f'Se esperaba un módulo JS principal de Vite; encontrados {js_count}. No se modificó el HTML publicado.')

    # If Vite splits JS into separate chunks in a future version, prevent a silently broken bundle.
    if re.search(r'<script[^>]+\bsrc=|<link[^>]+\brel=["\']modulepreload', html, re.IGNORECASE):
        raise RuntimeError('El build utiliza archivos JS externos/chunks. No se genera un HTML incompleto.')

    cockpit_bytes = COCKPIT.read_bytes()
    cockpit_b64 = base64.b64encode(cockpit_bytes).decode('ascii')
    inject = '''<script data-autoos-cockpit="true">
(function(){
  try {
    const b64 = "''' + cockpit_b64 + '''";
    const bytes = Uint8Array.from(atob(b64), ch => ch.charCodeAt(0));
    window.__AUTOOS_COCKPIT_HTML__ = new TextDecoder('utf-8').decode(bytes);
  } catch (err) { console.error('Error cargando cockpit de AutoOS:', err); }
})();
</script>
'''
    if '</head>' not in html:
        raise RuntimeError('No se encontró </head> en el HTML generado')
    html = html.replace('</head>', inject + '</head>', 1)
    # El HTML clásico permanece como respaldo y para la pestaña técnica.
    OUTPUT.write_text(html, encoding='utf-8')
    # V10: empaquetado como componente bidireccional de Streamlit. La única
    # diferencia es el protocolo JS incluido ANTES de montar React.
    if COMPONENT_BOOTSTRAP.is_file():
        bridge_js = COMPONENT_BOOTSTRAP.read_text(encoding='utf-8')
        bridge_html = html.replace('</head>',
            '<script data-autoos-kernel-component="v10">\n' + bridge_js + '\n</script>\n</head>', 1)
        COMPONENT_DIR.mkdir(parents=True, exist_ok=True)
        (COMPONENT_DIR / 'index.html').write_text(bridge_html, encoding='utf-8')
        print(f'Puente Python generado: {(COMPONENT_DIR / "index.html").relative_to(ROOT)}')
    else:
        raise FileNotFoundError(f'No existe {COMPONENT_BOOTSTRAP}')
    print(f'OK: {OUTPUT.relative_to(ROOT)} reconstruido desde Vite')
    print(f'CSS integrado: {css_count}; JS integrado: {js_count}; cockpit embebido: {len(cockpit_bytes)} bytes')
    print(f'Tamaño final: {len(html.encode("utf-8")):,} bytes')


if __name__ == '__main__':
    build()
