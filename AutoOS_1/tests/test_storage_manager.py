"""
Pruebas unitarias para StorageManager.
"""

import unittest

from src.memory.storage_manager import StorageManager


class TestStorageManager(unittest.TestCase):
    """
    Pruebas del gestor de almacenamiento.
    """

    def setUp(self):
        """
        Se ejecuta antes de cada prueba.
        """

        self.storage = StorageManager(50000)

    def test_initial_storage_state(self):
        """
        Verifica el estado inicial del almacenamiento.
        """

        self.assertEqual(self.storage.capacity, 50000)
        self.assertEqual(self.storage.used_space, 0)
        self.assertEqual(self.storage.free_space, 50000)

    def test_allocate_storage(self):
        """
        Verifica una asignación válida.
        """

        result = self.storage.allocate(1000)

        self.assertTrue(result)
        self.assertEqual(self.storage.used_space, 1000)
        self.assertEqual(self.storage.free_space, 49000)

    def test_allocate_too_much_storage(self):
        """
        Verifica que no se pueda superar
        la capacidad disponible.
        """

        result = self.storage.allocate(60000)

        self.assertFalse(result)
        self.assertEqual(self.storage.used_space, 0)

    def test_release_storage(self):
        """
        Verifica liberación de espacio.
        """

        self.storage.allocate(1000)
        self.storage.release(400)

        self.assertEqual(self.storage.used_space, 600)
        self.assertEqual(self.storage.free_space, 49400)

    def test_has_enough_space(self):
        """
        Verifica detección de espacio disponible.
        """

        self.assertTrue(
            self.storage.has_enough_space(500)
        )

        self.assertFalse(
            self.storage.has_enough_space(60000)
        )


if __name__ == "__main__":
    unittest.main()