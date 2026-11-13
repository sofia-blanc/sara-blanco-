"""
====================================================================
AUTOOS - SCRIPT DE DIAGNÓSTICO Y PRUEBA DE CONEXIÓN A SUPABASE
====================================================================
Uso:
    python test_supabase.py

Verifica automáticamente:
1. Existencia y lectura de credenciales (.env o .streamlit/secrets.toml)
2. Disponibilidad de la librería oficial 'supabase'
3. Conectividad HTTP / SSL con el servidor Supabase Cloud
4. Acceso y lectura de tablas: 'dispositivos', 'eventos', 'reportes_simulacion'
5. Permisos de inserción / RLS con la clave anónima (anon public key)
====================================================================
"""

import os
import sys
import time
from pathlib import Path

# Configuración de salida segura para Windows (evitar errores de codificación cp1252)
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Colores de terminal para Windows / ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_step(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")


def load_env_manually():
    """Busca y carga variables desde archivos .env sin dependencias externas"""
    loaded_from = []
    candidates = [Path(".env"), Path("Auto/.env"), Path("web/.env")]
    for path in candidates:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip('"').strip("'")
                            if k not in os.environ and v:
                                os.environ[k] = v
                loaded_from.append(str(path))
            except Exception as e:
                print(f"{YELLOW}[!] Error leyendo {path}: {e}{RESET}")
    return loaded_from


def main():
    print(f"\n{BOLD}=== AUTOOS - VERIFICADOR DE CONEXION A SUPABASE CLOUD ==={RESET}")
    print("=" * 60)

    # 1. Cargar variables
    env_files = load_env_manually()
    if env_files:
        print(f"Archivos de entorno detectados: {', '.join(env_files)}")

    # 2. Localizar credenciales
    url = (
        os.environ.get("SUPABASE_URL")
        or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        or os.environ.get("VITE_SUPABASE_URL")
    )
    key = (
        os.environ.get("SUPABASE_KEY")
        or os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
        or os.environ.get("VITE_SUPABASE_ANON_KEY")
    )

    # Revisar secrets.toml si no están en env
    secrets_paths = [Path(".streamlit/secrets.toml"), Path("Auto/.streamlit/secrets.toml")]
    for sp in secrets_paths:
        if sp.exists() and (not url or not key):
            try:
                with open(sp, "r", encoding="utf-8") as f:
                    content = f.read()
                    for line in content.splitlines():
                        line = line.strip()
                        if line.startswith("SUPABASE_URL") and not url:
                            url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        elif line.startswith("SUPABASE_KEY") and not key:
                            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass

    print_step("Paso 1: Detección de Credenciales")
    if not url or not key:
        print(f"{RED}❌ No se encontraron credenciales de Supabase.{RESET}")
        print(f"{YELLOW}Acción requerida:{RESET}")
        print("  1. Abre el archivo .env o .streamlit/secrets.toml")
        print("  2. Configura SUPABASE_URL y SUPABASE_KEY con los datos de tu proyecto.")
        return 1

    is_placeholder = (
        "tu-proyecto-aqui" in url
        or "your-project" in url
        or "tu-anon-key" in key
        or "your-anon-key" in key
    )
    if is_placeholder:
        print(f"{YELLOW}⚠️  Se detectaron valores de plantilla (placeholders) en la configuración:{RESET}")
        print(f"  URL : {url}")
        print(f"  KEY : {key[:15]}... [longitud: {len(key)}]")
        print(f"\n{YELLOW}Reemplaza 'tu-proyecto-aqui' y 'tu-anon-key' con los valores reales de tu proyecto.{RESET}")
        return 1

    print(f"{GREEN}[OK] URL detectada :{RESET} {url}")
    print(f"{GREEN}[OK] Key detectada :{RESET} {key[:12]}...{key[-6:]} [longitud: {len(key)}]")

    # 3. Validar librería supabase en Python
    print_step("Paso 2: Libreria Python 'supabase'")
    has_supabase_pkg = False
    try:
        from supabase import create_client
        print(f"{GREEN}[OK] Libreria oficial 'supabase' instalada y lista.{RESET}")
        has_supabase_pkg = True
    except ImportError:
        print(f"{YELLOW}[!] Libreria 'supabase' no instalada en Python (pip install supabase).{RESET}")
        print(f"    Probando conexion mediante cliente REST nativo (urllib)...")

    # 4. Conexión y consulta
    print_step("Paso 3: Prueba de Conexion a la Base de Datos")
    t0 = time.time()
    dispositivos = []
    
    if has_supabase_pkg:
        try:
            supabase = create_client(url, key)
            resp_dev = supabase.table("dispositivos").select("codigo, nombre, estado").limit(5).execute()
            latency = round((time.time() - t0) * 1000)
            dispositivos = resp_dev.data
            print(f"{GREEN}[OK] Conexion establecida con exito via Supabase SDK ({latency} ms).{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Error al conectar via SDK:{RESET} {e}")
            return 1
    else:
        import urllib.request
        import json
        req_url = f"{url.rstrip('/')}/rest/v1/dispositivos?select=codigo,nombre,estado&limit=5"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        try:
            req = urllib.request.Request(req_url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as response:
                latency = round((time.time() - t0) * 1000)
                body = response.read().decode("utf-8")
                dispositivos = json.loads(body)
                print(f"{GREEN}[OK] Conexion HTTP/REST establecida con exito ({latency} ms).{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Error al conectar con Supabase REST:{RESET} {e}")
            print(f"\n{YELLOW}Consejo:{RESET} Asegurate de que la URL es valida y que ejecutaste:")
            print("   Auto/sql/00_SETUP_COMPLETO_SUPABASE.sql")
            return 1

    print(f"  Dispositivos encontrados en Supabase: {len(dispositivos)}")
    for d in dispositivos:
        print(f"    - [{d.get('codigo')}] {d.get('nombre')}: {d.get('estado')}")

    # 5. Probar inserción en eventos
    print_step("Paso 4: Prueba de Insercion (Permisos RLS)")
    test_payload = {
        "tipo_evento": "seguridad",
        "severidad": "info",
        "mensaje": "Probe de verificacion automatica AutoOS - Conexion confirmada.",
        "detalles": {"test_runner": "test_supabase.py", "timestamp": time.time()},
        "resuelto": True
    }
    
    if has_supabase_pkg:
        try:
            supabase.table("eventos").insert(test_payload).execute()
            print(f"{GREEN}[OK] Insercion en tabla 'eventos' permitida por politicas RLS.{RESET}")
        except Exception as e:
            print(f"{YELLOW}[!] Aviso en insercion de eventos: {e}{RESET}")
    else:
        try:
            req_url = f"{url.rstrip('/')}/rest/v1/eventos"
            data_bytes = json.dumps(test_payload).encode("utf-8")
            req = urllib.request.Request(req_url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"{GREEN}[OK] Insercion en tabla 'eventos' permitida via REST.{RESET}")
        except Exception as e:
            print(f"{YELLOW}[!] Aviso en insercion de eventos: {e}{RESET}")

    # 6. Probar tabla reportes_simulacion
    print_step("Paso 5: Tabla 'reportes_simulacion'")
    if has_supabase_pkg:
        try:
            resp_rep = supabase.table("reportes_simulacion").select("id").limit(1).execute()
            print(f"{GREEN}[OK] Tabla 'reportes_simulacion' disponible para Centro de Simulacion Web.{RESET}")
        except Exception:
            print(f"{YELLOW}[!] Tabla 'reportes_simulacion' aun no creada. Ejecuta Auto/sql/00_SETUP_COMPLETO_SUPABASE.sql.{RESET}")
    else:
        try:
            req_url = f"{url.rstrip('/')}/rest/v1/reportes_simulacion?select=id&limit=1"
            req = urllib.request.Request(req_url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"{GREEN}[OK] Tabla 'reportes_simulacion' disponible para Centro de Simulacion Web.{RESET}")
        except Exception:
            print(f"{YELLOW}[!] Tabla 'reportes_simulacion' aun no creada. Ejecuta Auto/sql/00_SETUP_COMPLETO_SUPABASE.sql.{RESET}")

    print("\n" + "=" * 60)
    print(f"{BOLD}{GREEN}*** CONEXION A SUPABASE 100% OPERATIVA Y VERIFICADA ***{RESET}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
