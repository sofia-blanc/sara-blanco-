"""
Pruebas unitarias para FileSystem.
"""

import unittest

from src.memory.file_system import FileSystem


class TestFileSystem(unittest.TestCase):
    """
    Pruebas del sistema de archivos de AutoOS.
    """

    def setUp(self):
        """
        Se ejecuta antes de cada prueba.
        """

        self.fs = FileSystem()

    def test_initial_structure(self):
        """
        Verifica que la estructura inicial exista.
        """

        self.assertTrue(self.fs.folder_exists("system"))
        self.assertTrue(self.fs.folder_exists("apps"))
        self.assertTrue(self.fs.folder_exists("users"))
        self.assertTrue(self.fs.folder_exists("drivers"))
        self.assertTrue(self.fs.folder_exists("config"))
        self.assertTrue(self.fs.folder_exists("logs"))

    def test_create_file(self):
        """
        Verifica creación de archivos.
        """

        result = self.fs.create_file(
            "logs",
            "gps.log",
            10
        )

        self.assertTrue(result)

        self.assertTrue(
            self.fs.file_exists(
                "logs",
                "gps.log"
            )
        )

    def test_update_file(self):
        """
        Verifica modificación de archivos.
        """

        self.fs.create_file(
            "logs",
            "gps.log",
            10
        )

        result = self.fs.update_file(
            "logs",
            "gps.log",
            20
        )

        self.assertTrue(result)

        self.assertEqual(
            self.fs.structure["logs"]["gps.log"]["size"],
            20
        )

    def test_delete_file(self):
        """
        Verifica eliminación de archivos.
        """

        self.fs.create_file(
            "logs",
            "gps.log",
            10
        )

        result = self.fs.delete_file(
            "logs",
            "gps.log"
        )

        self.assertTrue(result)

        self.assertFalse(
            self.fs.file_exists(
                "logs",
                "gps.log"
            )
        )

    def test_list_files(self):
        """
        Verifica listado de archivos.
        """

        self.fs.create_file(
            "logs",
            "gps.log",
            10
        )

        files = self.fs.list_files("logs")

        self.assertIn(
            "gps.log",
            files
        )


if __name__ == "__main__":
    unittest.main()