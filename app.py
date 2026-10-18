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

# Configurar rutas absolutas consistentes al módulo raíz y módulo Auto
BASE_DIR = Path(__file__).resolve().parent
AUTO_DIR = BASE_DIR / "Auto"

for d in [str(BASE_DIR), str(AUTO_DIR)]:
    if d not in sys.path:
        sys.path.insert(0, d)

# Cambiar directorio de trabajo para resolución consistente
os.chdir(str(AUTO_DIR))

# Ejecutar el dashboard principal integrado
auto_app_file = AUTO_DIR / "app.py"
with open(auto_app_file, "r", encoding="utf-8") as f:
    app_code = f.read()

exec(compile(app_code, str(auto_app_file), "exec"), {"__name__": "__main__", "__file__": str(auto_app_file)})
