"""
Sistema de archivos de AutoOS (VFS - Virtual File System).

Este módulo implementa el sistema de archivos jerárquico para el vehículo inteligente
con persistencia en almacenamiento secundario.

Funcionalidades:
- Creación, lectura, escritura y actualización de archivos.
- Almacenamiento de metadatos (tamaño en MB/KB, contenido, marcas temporales, permisos).
- Eliminación de archivos y directorios.
- Navegación y listado de directorios.
- Persistencia automática en disco (sobrevive a reinicios de la aplicación).
"""
import os
import json
import time
from typing import Dict, List, Optional, Any


class FileSystem:
    """
    Representa el sistema de archivos virtual y persistente de AutoOS.

    Gestiona carpetas del vehículo (/system, /apps, /users, /drivers, /config, /logs)
    y sincroniza el árbol de archivos con un almacenamiento en disco en formato JSON.
    """

    DEFAULT_FOLDERS = ["system", "apps", "users", "drivers", "config", "logs"]

    def __init__(self, storage_path: Optional[str] = None, auto_load: bool = True):
        """
        Inicializa el sistema de archivos.

        :param storage_path: Ruta del archivo JSON donde se persistirá el estado.
                             Si es None, opera en memoria salvo que se configure después.
        :param auto_load: Si es True y storage_path existe, carga el estado persistente.
        """
        self.storage_path: Optional[str] = storage_path
        self.structure: Dict[str, Dict[str, Dict[str, Any]]] = {
            folder: {} for folder in self.DEFAULT_FOLDERS
        }

        if auto_load and self.storage_path and os.path.exists(self.storage_path):
            self.load_from_disk(self.storage_path)

    def _persist_if_configured(self) -> None:
        """Guarda el estado en disco automáticamente si storage_path está definido."""
        if self.storage_path:
            self.save_to_disk(self.storage_path)

    # --- Operaciones de Archivos (Lectura, Escritura, Creación, Modificación) ---

    def create_file(
        self,
        folder: str,
        filename: str,
        size: int = 1,
        content: str = "",
        permissions: str = "0644",
    ) -> bool:
        """
        Crea un nuevo archivo dentro de una carpeta del sistema.

        :param folder: Nombre de la carpeta destino (sin barra inicial, ej. 'config').
        :param filename: Nombre del archivo (ej. 'vehicle_params.json').
        :param size: Tamaño estimado en MB (>= 0).
        :param content: Contenido textual del archivo.
        :param permissions: Permisos en formato octal/simbólico.
        :return: True si fue creado correctamente, False si la carpeta no existe.
        """
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure:
            return False

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.structure[folder_key][filename] = {
            "size": max(0, size),
            "content": content,
            "permissions": permissions,
            "created_at": now,
            "updated_at": now,
        }

        self._persist_if_configured()
        return True

    def read_file(self, folder: str, filename: str) -> Optional[str]:
        """
        Lee el contenido textual de un archivo existente.

        :param folder: Carpeta contenedora.
        :param filename: Nombre del archivo.
        :return: Cadena de texto con el contenido, o None si no existe.
        """
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure or filename not in self.structure[folder_key]:
            return None

        return self.structure[folder_key][filename].get("content", "")

    def write_file(
        self,
        folder: str,
        filename: str,
        content: str,
        mode: str = "w",
        estimated_size: Optional[int] = None,
    ) -> bool:
        """
        Escribe datos en un archivo existente o lo crea si no existe.

        :param folder: Carpeta contenedora.
        :param filename: Nombre del archivo.
        :param content: Cadena de texto a escribir o agregar.
        :param mode: 'w' para sobreescribir, 'a' para concatenar.
        :param estimated_size: Tamaño opcional en MB. Si es None, se calcula según longitud.
        :return: True si la operación tuvo éxito, False si la carpeta no existe.
        """
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure:
            return False

        now = time.strftime("%Y-%m-%d %H:%M:%S")

        if filename in self.structure[folder_key]:
            current = self.structure[folder_key][filename]
            if mode == "a":
                new_content = current.get("content", "") + content
            else:
                new_content = content

            current["content"] = new_content
            current["updated_at"] = now
            if estimated_size is not None:
                current["size"] = estimated_size
            else:
                # 1 MB mínimo por defecto si tiene contenido
                current["size"] = max(1, len(new_content.encode("utf-8")) // 1024)
        else:
            calc_size = estimated_size if estimated_size is not None else max(1, len(content.encode("utf-8")) // 1024)
            self.structure[folder_key][filename] = {
                "size": calc_size,
                "content": content,
                "permissions": "0644",
                "created_at": now,
                "updated_at": now,
            }

        self._persist_if_configured()
        return True

    def update_file(self, folder: str, filename: str, new_size: int) -> bool:
        """
        Modifica el tamaño asignado a un archivo existente (compatibilidad histórica).
        """
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure or filename not in self.structure[folder_key]:
            return False

        self.structure[folder_key][filename]["size"] = new_size
        self.structure[folder_key][filename]["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._persist_if_configured()
        return True

    def delete_file(self, folder: str, filename: str) -> bool:
        """
        Elimina un archivo existente.

        :param folder: Carpeta donde reside el archivo.
        :param filename: Nombre del archivo a eliminar.
        :return: True si fue eliminado, False si no existe.
        """
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure:
            return False

        if filename in self.structure[folder_key]:
            del self.structure[folder_key][filename]
            self._persist_if_configured()
            return True

        return False

    # --- Operaciones de Directorios y Consultas ---

    def create_directory(self, folder: str) -> bool:
        """
        Crea un nuevo directorio o carpeta en el sistema de archivos.

        :param folder: Nombre de la carpeta a crear.
        :return: True si fue creada, False si ya existía.
        """
        folder_key = folder.lstrip("/")
        if folder_key in self.structure:
            return False

        self.structure[folder_key] = {}
        self._persist_if_configured()
        return True

    def list_files(self, folder: str) -> List[str]:
        """
        Retorna la lista de nombres de archivos presentes en una carpeta.
        """
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure:
            return []

        return list(self.structure[folder_key].keys())

    def list_directories(self) -> List[str]:
        """
        Retorna la lista de todos los directorios existentes en el sistema de archivos.
        """
        return list(self.structure.keys())

    def folder_exists(self, folder: str) -> bool:
        """Verifica si una carpeta existe."""
        folder_key = folder.lstrip("/")
        return folder_key in self.structure

    def file_exists(self, folder: str, filename: str) -> bool:
        """Verifica si un archivo existe dentro de una carpeta."""
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure:
            return False
        return filename in self.structure[folder_key]

    def get_file_info(self, folder: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los metadatos completos de un archivo (tamaño, contenido, permisos, fechas).
        """
        folder_key = folder.lstrip("/")
        if folder_key not in self.structure or filename not in self.structure[folder_key]:
            return None
        return dict(self.structure[folder_key][filename])

    # --- Persistencia en Almacenamiento Secundario (Disco / JSON) ---

    def save_to_disk(self, filepath: Optional[str] = None) -> bool:
        """
        Guarda la estructura completa de carpetas, archivos y contenidos en un archivo JSON en disco.
        Garantiza que los datos sobrevivan a reinicios del simulador.

        :param filepath: Ruta del archivo destino en disco. Si es None, usa self.storage_path.
        :return: True si se guardó con éxito, False en caso de error.
        """
        target_path = filepath or self.storage_path
        if not target_path:
            return False

        try:
            # Asegurar directorio padre
            parent_dir = os.path.dirname(target_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(self.structure, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_from_disk(self, filepath: Optional[str] = None) -> bool:
        """
        Carga la estructura de carpetas, archivos y contenidos desde un archivo JSON en disco.

        :param filepath: Ruta del archivo origen. Si es None, usa self.storage_path.
        :return: True si se cargó exitosamente, False si no existe o hubo error.
        """
        source_path = filepath or self.storage_path
        if not source_path or not os.path.exists(source_path):
            return False

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                # Preservar carpetas por defecto
                for folder in self.DEFAULT_FOLDERS:
                    if folder not in loaded:
                        loaded[folder] = {}
                self.structure = loaded
                return True
            return False
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Retorna la estructura completa del sistema de archivos."""
        return self.structure

    def __repr__(self) -> str:
        total_files = sum(len(files) for files in self.structure.values())
        return f"FileSystem(Folders={len(self.structure)}, TotalFiles={total_files})"