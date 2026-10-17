"""
Memoria virtual de AutoOS.

Este módulo simula una zona de intercambio (SWAP)
utilizada cuando la memoria RAM disponible no es suficiente.

Responsabilidades:

- Asignar memoria virtual.
- Liberar memoria virtual.
- Mostrar memoria utilizada.
- Mostrar memoria disponible.
- Detectar cuando el área SWAP está llena.
"""


class VirtualMemory:
    """
    Representa el área de memoria virtual (SWAP) de AutoOS.

    Cuando la RAM no tiene suficiente espacio disponible,
    los datos pueden almacenarse temporalmente en esta área.
    """

    def __init__(self, swap_size=8192):
        """
        Inicializa la memoria virtual.

        :param swap_size: Tamaño total del área SWAP en MB.
        """

        self._swap_size = swap_size
        self._used_swap = 0

    @property
    def swap_size(self):
        """
        Retorna el tamaño total del área SWAP.

        :return: Tamaño total en MB.
        """

        return self._swap_size

    @property
    def used_swap(self):
        """
        Retorna la cantidad de memoria virtual utilizada.

        :return: Memoria utilizada en MB.
        """

        return self._used_swap

    @property
    def free_swap(self):
        """
        Calcula la memoria virtual disponible.

        :return: Memoria libre en MB.
        """

        return self._swap_size - self._used_swap

    def allocate(self, size):
        """
        Asigna memoria virtual.

        :param size: Cantidad de memoria requerida en MB.
        :return: True si la operación fue exitosa,
                 False en caso contrario.
        """

        if size <= 0:
            return False

        if size > self.free_swap:
            return False

        self._used_swap += size

        return True

    def release(self, size):
        """
        Libera memoria virtual.

        :param size: Cantidad de memoria a liberar en MB.
        :return: True si la operación fue válida,
                 False en caso contrario.
        """

        if size <= 0:
            return False

        self._used_swap -= size

        if self._used_swap < 0:
            self._used_swap = 0

        return True

    def has_enough_space(self, required_size):
        """
        Verifica si existe espacio suficiente
        en el área SWAP.

        :param required_size: Espacio requerido en MB.
        :return: True si existe espacio disponible.
        """

        return required_size <= self.free_swap

    def to_dict(self):
        """
        Genera un diccionario con el estado
        actual de la memoria virtual.

        :return: Diccionario serializable.
        """

        return {
            "swap_size": self.swap_size,
            "used_swap": self.used_swap,
            "free_swap": self.free_swap
        }

    def __repr__(self):
        """
        Representación legible del objeto.
        """

        return (
            f"VirtualMemory("
            f"total={self.swap_size} MB, "
            f"used={self.used_swap} MB, "
            f"free={self.free_swap} MB)"
        )