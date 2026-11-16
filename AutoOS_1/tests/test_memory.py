"""
Pruebas unitarias para MemoryManager.
"""

import unittest

from src.memory.memory import MemoryManager


class TestMemoryManager(unittest.TestCase):
    """
    Pruebas del gestor de memoria RAM.
    """

    def setUp(self):
        """
        Se ejecuta antes de cada prueba.
        """

        self.memory = MemoryManager(4096)

    def test_initial_memory_state(self):
        """
        Verifica que la memoria inicie correctamente.
        """

        self.assertEqual(self.memory.total_memory, 4096)
        self.assertEqual(self.memory.used_memory, 0)
        self.assertEqual(self.memory.free_memory, 4096)

    def test_allocate_memory(self):
        """
        Verifica una asignación válida.
        """

        result = self.memory.allocate(1000)

        self.assertTrue(result)
        self.assertEqual(self.memory.used_memory, 1000)
        self.assertEqual(self.memory.free_memory, 3096)

    def test_allocate_too_much_memory(self):
        """
        Verifica que no se pueda superar la RAM.
        """

        result = self.memory.allocate(5000)

        self.assertFalse(result)
        self.assertEqual(self.memory.used_memory, 0)

    def test_release_memory(self):
        """
        Verifica liberación de memoria.
        """

        self.memory.allocate(1000)
        self.memory.release(500)

        self.assertEqual(self.memory.used_memory, 500)
        self.assertEqual(self.memory.free_memory, 3596)

    def test_has_enough_memory(self):
        """
        Verifica detección de memoria disponible.
        """

        self.assertTrue(
            self.memory.has_enough_memory(500)
        )

        self.assertFalse(
            self.memory.has_enough_memory(6000)
        )


if __name__ == "__main__":
    unittest.main()