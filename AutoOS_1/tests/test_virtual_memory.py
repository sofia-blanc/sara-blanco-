"""
Pruebas unitarias para VirtualMemory.

Estas pruebas verifican:

- Estado inicial.
- Asignación de memoria virtual.
- Liberación de memoria virtual.
- Límites del área SWAP.
- Verificación de espacio disponible.
"""

import unittest

from src.memory.virtual_memory import VirtualMemory


class TestVirtualMemory(unittest.TestCase):
    """
    Pruebas del área de memoria virtual (SWAP).
    """

    def setUp(self):
        """
        Se ejecuta antes de cada prueba.

        Crea una memoria virtual de 8192 MB.
        """

        self.virtual_memory = VirtualMemory(8192)

    def test_initial_swap_state(self):
        """
        Verifica el estado inicial de la memoria virtual.
        """

        self.assertEqual(
            self.virtual_memory.swap_size,
            8192
        )

        self.assertEqual(
            self.virtual_memory.used_swap,
            0
        )

        self.assertEqual(
            self.virtual_memory.free_swap,
            8192
        )

    def test_allocate_swap(self):
        """
        Verifica una asignación válida.
        """

        result = self.virtual_memory.allocate(1000)

        self.assertTrue(result)

        self.assertEqual(
            self.virtual_memory.used_swap,
            1000
        )

        self.assertEqual(
            self.virtual_memory.free_swap,
            7192
        )

    def test_allocate_too_much_swap(self):
        """
        Verifica que no sea posible superar
        el tamaño total de la memoria virtual.
        """

        result = self.virtual_memory.allocate(10000)

        self.assertFalse(result)

        self.assertEqual(
            self.virtual_memory.used_swap,
            0
        )

    def test_release_swap(self):
        """
        Verifica liberación de memoria virtual.
        """

        self.virtual_memory.allocate(1000)

        self.virtual_memory.release(400)

        self.assertEqual(
            self.virtual_memory.used_swap,
            600
        )

        self.assertEqual(
            self.virtual_memory.free_swap,
            7592
        )

    def test_has_enough_space(self):
        """
        Verifica detección de espacio disponible.
        """

        self.assertTrue(
            self.virtual_memory.has_enough_space(500)
        )

        self.assertFalse(
            self.virtual_memory.has_enough_space(10000)
        )


if __name__ == "__main__":
    unittest.main()
