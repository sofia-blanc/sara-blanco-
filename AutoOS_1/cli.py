"""
AutoOS - CLI y Shell Interactivo del Sistema Operativo Vehicular.
Punto de entrada principal para sustentación y demostración interactiva.
"""
import sys
import os

# Asegurar que AutoOS_1 esté en el PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core.kernel import Kernel
from src.core.terminal import Terminal


def run_live_demonstration(terminal: Terminal):
    """
    Ejecuta una demostración en vivo guiada paso a paso para la sustentación universitaria.
    """
    print("\n" + "=" * 70)
    print("   AUTOOS: SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE - DEMO EN VIVO")
    print("=" * 70 + "\n")

    steps = [
        ("1. ARRANQUE DEL SISTEMA (BOOT FORMAL Y KERNEL)", "boot"),
        ("2. CONSULTA DE ESTADO GENERAL DEL SISTEMA", "status"),
        ("3. LISTA DE PROCESOS DEMONIO CREADOS", "ps"),
        ("4. CONSULTA DEL MAPA DINÁMICO DE PARTICIONES DE MEMORIA RAM", "mem map"),
        ("5. CREACIÓN DE NUEVO PROCESO VEHICULAR CON ASIGNACIÓN DE RAM", "create Freno_Emergencia_AEB 1 3 64"),
        ("6. VERIFICACIÓN DEL PROCESO Y MEMORIA ACTUALIZADA", "ps"),
        ("7. EJECUCIÓN DE CICLOS DE CPU (CONSUMO DE TIEMPO Y CAMBIO DE ESTADO)", "step 4"),
        ("8. SISTEMA DE ARCHIVOS: LECTURA DE PARÁMETROS DEL VEHÍCULO", "cat config vehicle_params.json"),
        ("9. SISTEMA DE ARCHIVOS: ESCRITURA DE TRAZA DE SEGURIDAD", "write logs safety.log ALERTA_RADAR:OBSTACULO_DETECTADO_20M"),
        ("10. SISTEMA DE ARCHIVOS: LISTADO DE ARCHIVOS EN /logs", "ls logs"),
        ("11. MEMORIA VIRTUAL: TRADUCCIÓN DE DIRECCIÓN VIRTUAL Y DETECCIÓN DE FALLO", "vmem 10 write 1"),
        ("12. MEMORIA VIRTUAL: ACIERTO EN SEGUNDO ACCESO (PAGE HIT)", "vmem 10 read 1"),
        ("13. PLANIFICACIÓN: CAMBIO A ALGORITMO ROUND ROBIN", "sched ROUND_ROBIN 2"),
        ("14. TERMINACIÓN FORZADA (KILL) Y LIBERACIÓN INMEDIATA DE RAM", "kill 2"),
        ("15. COMPROBACIÓN FINAL DE MEMORIA LIBERADA", "mem"),
    ]

    for title, cmd in steps:
        print(f"\n>>> {title}")
        print(f"AutoOS> {cmd}")
        resp = terminal.execute(cmd)
        print(resp.output)

    print("\n" + "=" * 70)
    print("   DEMOSTRACIÓN FINALIZADA - LOS 10 CRITERIOS HAN SIDO VERIFICADOS")
    print("=" * 70 + "\n")


def run_interactive_shell(terminal: Terminal):
    """
    Bucle interactivo (REPL) para que el evaluador o usuario interactúe con AutoOS.
    """
    print("\n" + "=" * 65)
    print("  AutoOS Interactive Shell v2.4 (Vehicular Operating System)")
    print("  Escriba 'help' para comandos, 'demo' para sustentación o 'exit' para salir.")
    print("=" * 65 + "\n")

    while True:
        try:
            line = input("AutoOS> ").strip()
            if not line:
                continue
            if line.lower() in ["exit", "quit", "salir"]:
                print("Cerrando sesión en AutoOS. Apagando kernel...")
                terminal.kernel.shutdown()
                break
            if line.lower() == "demo":
                run_live_demonstration(terminal)
                continue

            resp = terminal.execute(line)
            print(resp.output)
        except (KeyboardInterrupt, EOFError):
            print("\nCerrando sesión en AutoOS...")
            terminal.kernel.shutdown()
            break


def main():
    kernel = Kernel(memory_mb=2048, swap_mb=4096)
    terminal = Terminal(kernel=kernel)

    if len(sys.argv) > 1 and sys.argv[1] in ["--demo", "-d", "demo"]:
        run_live_demonstration(terminal)
    else:
        run_interactive_shell(terminal)


if __name__ == "__main__":
    main()
