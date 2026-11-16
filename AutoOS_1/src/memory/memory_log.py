"""
Sistema de registro (Logs) de AutoOS.

Este módulo registra eventos relacionados con:

- Memoria RAM.
- Memoria virtual.
- Sistema de archivos.
- Almacenamiento.

Su propósito es permitir auditoría y monitoreo
de las operaciones realizadas por el sistema.
"""

from datetime import datetime


class MemoryLog:
    """
    Representa la bitácora de eventos del subsistema
    de memoria y almacenamiento de AutoOS.
    """

    def __init__(self):
        """
        Inicializa una lista vacía de registros.
        """

        self._logs = []

    def add_log(self, level, message):
        """
        Registra un nuevo evento.

        Niveles sugeridos:

        - INFO
        - WARNING
        - ERROR

        :param level: Nivel del evento.
        :param message: Descripción del evento.
        """

        self._logs.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "level": level,
                "message": message
            }
        )

    def get_logs(self):
        """
        Retorna todos los registros almacenados.

        :return: Lista de logs.
        """

        return self._logs

    def clear_logs(self):
        """
        Elimina todos los registros almacenados.
        """

        self._logs.clear()

    @property
    def total_logs(self):
        """
        Retorna la cantidad total de registros.

        :return: Número de logs.
        """

        return len(self._logs)

    def to_dict(self):
        """
        Convierte la bitácora completa a un formato
        serializable.

        :return: Lista de diccionarios.
        """

        return self._logs

    def __repr__(self):
        """
        Representación legible de la bitácora.
        """

        return (
            f"MemoryLog(total_logs={self.total_logs})"
        )