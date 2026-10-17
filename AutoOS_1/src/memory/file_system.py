"""
Sistema de archivos de AutoOS.

Este módulo simula un sistema de archivos básico para un vehículo inteligente.

Funcionalidades:
- Crear archivos.
- Consultar archivos.
- Modificar archivos.
- Eliminar archivos.
- Listar archivos por carpeta.
- Mostrar la estructura completa.
"""


class FileSystem:
    """
    Representa el sistema de archivos virtual de AutoOS.

    Cada carpeta se almacena como un diccionario y cada archivo
    contiene información básica, como su tamaño.
    """

    def __init__(self):
        """
        Inicializa la estructura base del sistema de archivos.
        """

        self.structure = {
            "system": {},
            "apps": {},
            "users": {},
            "drivers": {},
            "config": {},
            "logs": {}
        }

    def create_file(self, folder, filename, size):
        """
        Crea un nuevo archivo dentro de una carpeta.

        :param folder: Carpeta donde se guardará el archivo.
        :param filename: Nombre del archivo.
        :param size: Tamaño del archivo en MB.
        :return: True si fue creado correctamente, False si la carpeta no existe.
        """

        if folder not in self.structure:
            return False

        self.structure[folder][filename] = {
            "size": size
        }

        return True

    def delete_file(self, folder, filename):
        """
        Elimina un archivo existente.

        :param folder: Carpeta donde se encuentra el archivo.
        :param filename: Nombre del archivo a eliminar.
        :return: True si fue eliminado, False en caso contrario.
        """

        if folder not in self.structure:
            return False

        if filename in self.structure[folder]:
            del self.structure[folder][filename]
            return True

        return False

    def update_file(self, folder, filename, new_size):
        """
        Modifica el tamaño de un archivo existente.

        :param folder: Carpeta donde se encuentra el archivo.
        :param filename: Nombre del archivo.
        :param new_size: Nuevo tamaño en MB.
        :return: True si fue actualizado correctamente,
                 False en caso contrario.
        """

        if folder not in self.structure:
            return False

        if filename not in self.structure[folder]:
            return False

        self.structure[folder][filename]["size"] = new_size

        return True

    def list_files(self, folder):
        """
        Retorna una lista con todos los archivos de una carpeta.

        :param folder: Carpeta a consultar.
        :return: Lista de nombres de archivos.
        """

        if folder not in self.structure:
            return []

        return list(self.structure[folder].keys())

    def folder_exists(self, folder):
        """
        Verifica si una carpeta existe.

        :param folder: Nombre de la carpeta.
        :return: True si existe, False en caso contrario.
        """

        return folder in self.structure

    def file_exists(self, folder, filename):
        """
        Verifica si un archivo existe dentro de una carpeta.

        :param folder: Carpeta donde buscar.
        :param filename: Nombre del archivo.
        :return: True si existe, False en caso contrario.
        """

        if folder not in self.structure:
            return False

        return filename in self.structure[folder]

    def to_dict(self):
        """
        Retorna la estructura completa del sistema de archivos.

        :return: Diccionario con carpetas y archivos.
        """

        return self.structure