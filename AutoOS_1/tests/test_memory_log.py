"""
Pruebas unitarias para MemoryLog.
"""

import unittest

from src.memory.memory_log import MemoryLog


class TestMemoryLog(unittest.TestCase):
    """
    Pruebas del sistema de logs.
    """

    def setUp(self):
        """
        Se ejecuta antes de cada prueba.
        """

        self.logger = MemoryLog()

    def test_initial_state(self):
        """
        Verifica estado inicial.
        """

        self.assertEqual(
            self.logger.total_logs,
            0
        )

    def test_add_log(self):
        """
        Verifica registro de eventos.
        """

        self.logger.add_log(
            "INFO",
            "Proceso GPS iniciado"
        )

        self.assertEqual(
            self.logger.total_logs,
            1
        )

    def test_get_logs(self):
        """
        Verifica recuperación de logs.
        """

        self.logger.add_log(
            "INFO",
            "Evento de prueba"
        )

        logs = self.logger.get_logs()

        self.assertEqual(
            len(logs),
            1
        )

        self.assertEqual(
            logs[0]["level"],
            "INFO"
        )

    def test_clear_logs(self):
        """
        Verifica limpieza de registros.
        """

        self.logger.add_log(
            "INFO",
            "Evento de prueba"
        )

        self.logger.clear_logs()

        self.assertEqual(
            self.logger.total_logs,
            0
        )

    def test_to_dict(self):
        """
        Verifica conversión serializable.
        """

        self.logger.add_log(
            "WARNING",
            "Memoria virtual activada"
        )

        logs = self.logger.to_dict()

        self.assertEqual(
            logs[0]["level"],
            "WARNING"
        )


if __name__ == "__main__":
    unittest.main()