"""
Pruebas de operaciones reales y persistencia en disco del sistema de archivos de AutoOS.

Verifica:
1. Creación y lectura de archivos con contenido textual y metadatos.
2. Escritura y concatenación (append) de contenidos.
3. Eliminación de archivos y verificación de inexistencia.
4. Creación y listado de nuevos directorios.
5. Persistencia real en disco (sobrevive al reinicio de la aplicación).
6. Persistencia de eliminaciones y modificaciones tras recargar.
"""
import unittest
import os
import tempfile

from src.memory.file_system import FileSystem


class TestFileSystemPersistence(unittest.TestCase):
    def setUp(self):
        # Crear archivo temporal para simular disco persistente
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_file.close()
        self.storage_path = self.temp_file.name
        self.fs = FileSystem(storage_path=self.storage_path, auto_load=False)

    def tearDown(self):
        # Limpiar archivo temporal al concluir la prueba
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)

    def test_1_create_and_read_file_with_content(self):
        """1. Creación y lectura de archivo con contenido real y metadatos."""
        created = self.fs.create_file(
            folder="config",
            filename="vehicle_calibration.json",
            size=5,
            content='{"steering_ratio": 14.5, "braking_force_nm": 4200}',
            permissions="0600",
        )
        self.assertTrue(created)

        # Leer archivo
        content = self.fs.read_file("config", "vehicle_calibration.json")
        self.assertIn("braking_force_nm", content)

        # Consultar metadatos
        info = self.fs.get_file_info("config", "vehicle_calibration.json")
        self.assertEqual(info["permissions"], "0600")
        self.assertEqual(info["size"], 5)
        self.assertIn("created_at", info)

    def test_2_write_and_append_file(self):
        """2. Escritura y concatenación (append) de contenidos en un log vehicular."""
        # Escribir línea 1
        self.fs.write_file("logs", "can_bus.log", "TRAZA_CAN: 0x1A2 [00 12 FF]\n")
        content1 = self.fs.read_file("logs", "can_bus.log")
        self.assertEqual(content1, "TRAZA_CAN: 0x1A2 [00 12 FF]\n")

        # Concatenar línea 2 (mode='a')
        self.fs.write_file("logs", "can_bus.log", "TRAZA_CAN: 0x1B4 [AA BB CC]\n", mode="a")
        content2 = self.fs.read_file("logs", "can_bus.log")
        self.assertIn("0x1A2", content2)
        self.assertIn("0x1B4", content2)

    def test_3_delete_file(self):
        """3. Eliminación de archivo existente."""
        self.fs.create_file("logs", "temp.log", 1, "datos temporales")
        self.assertTrue(self.fs.file_exists("logs", "temp.log"))

        deleted = self.fs.delete_file("logs", "temp.log")
        self.assertTrue(deleted)
        self.assertFalse(self.fs.file_exists("logs", "temp.log"))
        self.assertIsNone(self.fs.read_file("logs", "temp.log"))

    def test_4_create_and_list_directories(self):
        """4. Creación y listado de directorios."""
        created = self.fs.create_directory("telemetry")
        self.assertTrue(created)
        self.assertTrue(self.fs.folder_exists("telemetry"))

        # No permite duplicar directorio existente
        dup = self.fs.create_directory("telemetry")
        self.assertFalse(dup)

        dirs = self.fs.list_directories()
        self.assertIn("telemetry", dirs)
        self.assertIn("system", dirs)

    def test_5_disk_persistence_survives_reboot(self):
        """5. Persistencia en disco: un nuevo FileSystem carga los archivos existentes."""
        # 1. Crear datos en la instancia inicial
        self.fs.create_file(
            folder="config",
            filename="ecu_map.cfg",
            size=15,
            content="MAP_ID=SPORT_PLUS;TORQUE_LIMIT=650NM",
        )
        self.fs.create_directory("radar")
        self.fs.create_file("radar", "point_cloud.bin", 20, "BIN_RADAR_DATA_BYTES")
        
        # Guardar en disco explícitamente (o verificado por autoguardado)
        self.fs.save_to_disk()

        # 2. Simular apagado y reinicio completo del sistema instanciando un nuevo FileSystem
        rebooted_fs = FileSystem(storage_path=self.storage_path, auto_load=True)

        # 3. Verificar que los datos sobreviven intactos
        self.assertTrue(rebooted_fs.folder_exists("radar"))
        self.assertTrue(rebooted_fs.file_exists("config", "ecu_map.cfg"))
        self.assertTrue(rebooted_fs.file_exists("radar", "point_cloud.bin"))

        content_recovered = rebooted_fs.read_file("config", "ecu_map.cfg")
        self.assertEqual(content_recovered, "MAP_ID=SPORT_PLUS;TORQUE_LIMIT=650NM")

        radar_data = rebooted_fs.read_file("radar", "point_cloud.bin")
        self.assertEqual(radar_data, "BIN_RADAR_DATA_BYTES")

    def test_6_persistence_after_modification_and_deletion(self):
        """6. Las modificaciones y eliminaciones también se reflejan tras reiniciar."""
        self.fs.create_file("logs", "error.log", 2, "Error 404")
        self.fs.save_to_disk()

        # Eliminar archivo
        self.fs.delete_file("logs", "error.log")

        # Reiniciar
        reloaded_fs = FileSystem(storage_path=self.storage_path, auto_load=True)
        self.assertFalse(reloaded_fs.file_exists("logs", "error.log"))
        self.assertIsNone(reloaded_fs.read_file("logs", "error.log"))


if __name__ == "__main__":
    unittest.main()
