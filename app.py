"""
====================================================================
AUTOOS - VEHÍCULO INTELIGENTE (ENTRYPOINT PRINCIPAL)
Lanzador del Dashboard Integrado para Despliegue Local y Cloud
====================================================================
"""

import os
import runpy
from pathlib import Path

# Ruta al script principal dentro de Auto/
BASE_DIR = Path(__file__).resolve().parent
AUTO_DIR = BASE_DIR / "Auto"
AUTO_APP = AUTO_DIR / "app.py"

# Cambiar directorio de trabajo a Auto/ para resolución consistente de recursos
os.chdir(str(AUTO_DIR))

# Ejecutar de forma estándar el dashboard principal
runpy.run_path(str(AUTO_APP), run_name="__main__")
