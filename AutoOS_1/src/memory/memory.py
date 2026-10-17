"""
Gestor de memoria RAM de AutoOS.

Este módulo simula la memoria principal (RAM) utilizada por el vehículo
inteligente. Es responsable de:

- Asignar memoria a procesos.
- Liberar memoria cuando un proceso finaliza.
- Calcular memoria utilizada.
- Calcular memoria disponible.
- Detectar falta de memoria.

Ejemplos de procesos que consumen memoria:

- GPS
- Cámara
- Sensores
- Navegación
- Multimedia
- Comunicación

La memoria se expresa en MB (Megabytes).
"""


class MemoryManager:
    """
    Representa el gestor de memoria RAM de AutoOS.

    Mantiene el control de la memoria total instalada,
    la memoria actualmente utilizada y la memoria disponible.
    """

    def __init__(self, total_memory=4096):
        """
        Inicializa el gestor de memoria.

        Por defecto AutoOS cuenta con 4096 MB de RAM.

        :param total_memory: Memoria total instalada en MB.
        """

        self._total_memory = total_memory
        self._used_memory = 0

    @property
    def total_memory(self):
        """
        Retorna la cantidad total de memoria RAM.

        :return: Memoria total en MB.
        """

        return self._total_memory

    @property
    def used_memory(self):
        """
        Retorna la memoria actualmente utilizada.

        :return: Memoria usada en MB.
        """

        return self._used_memory

    @property
    def free_memory(self):
        """
        Calcula la memoria disponible.

        Fórmula:

        memoria libre = memoria total - memoria usada

        :return: Memoria libre en MB.
        """

        return self._total_memory - self._used_memory

    def allocate(self, size):
        """
        Intenta reservar memoria para un proceso.

        Ejemplo:

        Si hay 3000 MB libres y un proceso solicita
        500 MB, la operación será exitosa.

        Si un proceso solicita más memoria de la
        disponible, la operación fallará.

        :param size: Cantidad de memoria a asignar en MB.
        :return: True si la asignación fue exitosa,
                 False en caso contrario.
        """

        if size <= 0:
            return False

        if size > self.free_memory:
            return False

        self._used_memory += size

        return True

    def release(self, size):
        """
        Libera memoria utilizada por un proceso.

        Ejemplo:

        Si actualmente hay 1000 MB ocupados y se liberan
        300 MB, el resultado será 700 MB ocupados.

        :param size: Cantidad de memoria a liberar en MB.
        :return: True si la liberación fue válida,
                 False en caso contrario.
        """

        if size <= 0:
            return False

        self._used_memory -= size

        if self._used_memory < 0:
            self._used_memory = 0

        return True

    def has_enough_memory(self, required_memory):
        """
        Verifica si existe memoria suficiente para
        satisfacer una solicitud.

        :param required_memory: Memoria requerida en MB.
        :return: True si existe memoria suficiente,
                 False en caso contrario.
        """

        return required_memory <= self.free_memory

    def to_dict(self):
        """
        Genera una representación serializable del
        estado actual de la memoria.

        Ideal para:

        - Dashboard
        - API
        - Supabase
        - Logs

        :return: Diccionario con el estado de la RAM.
        """

        return {
            "total_memory": self.total_memory,
            "used_memory": self.used_memory,
            "free_memory": self.free_memory
        }

    def __repr__(self):
        """
        Representación legible del gestor de memoria.
        """

        return (
            f"MemoryManager("
            f"total={self.total_memory} MB, "
            f"used={self.used_memory} MB, "
            f"free={self.free_memory} MB)"
        )