"""
====================================================================
AUTOOS - VEHÍCULO INTELIGENTE (ENTRYPOINT PRINCIPAL)
Lanzador del Dashboard Integrado para Despliegue Local y Cloud
Responsable: Integrante 4 (Interfaz e Integración)
====================================================================
"""
import sys
import os
from pathlib import Path

# Configurar ruta absoluta al módulo integrado Auto
BASE_DIR = Path(__file__).resolve().parent
AUTO_DIR = BASE_DIR / "Auto"

if str(AUTO_DIR) not in sys.path:
    sys.path.insert(0, str(AUTO_DIR))

# Cambiar directorio de trabajo para resolución consistente de .streamlit/secrets.toml
os.chdir(str(AUTO_DIR))

# Ejecutar el dashboard principal integrado
auto_app_file = AUTO_DIR / "app.py"
with open(auto_app_file, "r", encoding="utf-8") as f:
    app_code = f.read()

exec(compile(app_code, str(auto_app_file), "exec"), {"__name__": "__main__", "__file__": str(auto_app_file)})
