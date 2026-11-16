"""
Gestor de almacenamiento de AutoOS.

Este módulo simula el almacenamiento persistente del vehículo inteligente.

Responsabilidades:

- Almacenar archivos.
- Liberar espacio de almacenamiento.
- Consultar espacio utilizado.
- Consultar espacio disponible.
- Detectar falta de espacio.

Ejemplos de archivos almacenados:

- gps.log
- camera.log
- navigation.cfg
- sensor_data.txt
- multimedia.cache

Las capacidades se expresan en MB (Megabytes).
"""


class StorageManager:
    """
    Representa el gestor de almacenamiento de AutoOS.

    Mantiene el control del espacio total disponible,
    el espacio utilizado y el espacio libre.
    """

    def __init__(self, capacity=50000):
        """
        Inicializa el almacenamiento del sistema.

        Por defecto AutoOS dispone de 50000 MB
        de almacenamiento.

        :param capacity: Capacidad total en MB.
        """

        self._capacity = capacity
        self._used_space = 0

    @property
    def capacity(self):
        """
        Retorna la capacidad total del almacenamiento.

        :return: Capacidad total en MB.
        """

        return self._capacity

    @property
    def used_space(self):
        """
        Retorna el espacio actualmente utilizado.

        :return: Espacio utilizado en MB.
        """

        return self._used_space

    @property
    def free_space(self):
        """
        Calcula el espacio disponible.

        Fórmula:

        espacio libre = capacidad total - espacio usado

        :return: Espacio libre en MB.
        """

        return self._capacity - self._used_space

    def allocate(self, size):
        """
        Reserva espacio de almacenamiento.

        Ejemplo:

        Si existen 10000 MB libres y se desea guardar
        un archivo de 500 MB, la operación será exitosa.

        :param size: Espacio requerido en MB.
        :return: True si fue posible reservar espacio,
                 False en caso contrario.
        """

        if size <= 0:
            return False

        if size > self.free_space:
            return False

        self._used_space += size

        return True

    def release(self, size):
        """
        Libera espacio previamente utilizado.

        Ejemplo:

        Si se elimina un archivo de 300 MB,
        esos 300 MB vuelven a estar disponibles.

        :param size: Espacio a liberar en MB.
        :return: True si la operación fue válida,
                 False en caso contrario.
        """

        if size <= 0:
            return False

        self._used_space -= size

        if self._used_space < 0:
            self._used_space = 0

        return True

    def has_enough_space(self, required_space):
        """
        Verifica si existe espacio suficiente.

        :param required_space: Espacio requerido en MB.
        :return: True si existe espacio suficiente,
                 False en caso contrario.
        """

        return required_space <= self.free_space

    def to_dict(self):
        """
        Genera una representación serializable
        del estado del almacenamiento.

        Ideal para:

        - Dashboard
        - API
        - Supabase
        - Logs

        :return: Diccionario con el estado
                 del almacenamiento.
        """

        return {
            "capacity": self.capacity,
            "used_space": self.used_space,
            "free_space": self.free_space
        }

    def __repr__(self):
        """
        Representación legible del almacenamiento.
        """

        return (
            f"StorageManager("
            f"capacity={self.capacity} MB, "
            f"used={self.used_space} MB, "
            f"free={self.free_space} MB)"
        )