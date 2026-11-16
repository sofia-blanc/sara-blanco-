"""
Pruebas unitarias para el subsistema de paginación y memoria virtual de AutoOS.

Verifica:
1. Creación de tablas de páginas e inicialización de marcos.
2. Traducción de direcciones virtuales con cálculo de páginas y desplazamientos (offsets).
3. Detección y atención de fallos de página (Page Faults).
4. Registro de aciertos de página (Page Hits) y cálculo de tasa de acierto (hit_ratio).
5. Algoritmo de reemplazo FIFO al agotarse los marcos físicos.
6. Algoritmo de reemplazo LRU expulsando la página menos recientemente referenciada.
7. Expulsión de páginas modificadas (dirty bit) hacia el área SWAP.
8. Liberación de recursos de memoria virtual al finalizar procesos.
"""
import unittest

from src.memory.virtual_memory import VirtualMemory, PageTableEntry
from src.core.event_logger import EventLogger


class TestVirtualMemoryPaging(unittest.TestCase):
    def setUp(self):
        self.logger = EventLogger()
        # Creamos una memoria virtual con 4 marcos físicos de 4 MB cada uno y 1024 MB de SWAP
        self.vmem = VirtualMemory(
            swap_size=1024,
            page_size=4,
            total_frames=4,
            replacement_algorithm="FIFO",
            logger=self.logger,
        )

    def test_1_address_translation_and_page_fault(self):
        """1. Traducción inicial genera fallo de página y mapea a un marco físico libre."""
        self.vmem.init_process_page_table(pid=10, num_pages=8)
        
        # Dirección virtual 10: página = 10 // 4 = 2, offset = 10 % 4 = 2
        result = self.vmem.translate_address(pid=10, virtual_address=10, current_tick=1)
        
        self.assertTrue(result["page_fault"])
        self.assertEqual(result["page_number"], 2)
        self.assertEqual(result["offset"], 2)
        self.assertEqual(result["frame_number"], 0)
        # Dirección física = (0 * 4) + 2 = 2
        self.assertEqual(result["physical_address"], 2)

        # La entrada en la tabla de páginas ahora debe ser válida y apuntar al marco 0
        table = self.vmem.get_page_table(pid=10)
        self.assertTrue(table[2].is_valid)
        self.assertEqual(table[2].frame_number, 0)
        self.assertEqual(self.vmem.page_faults, 1)

    def test_2_page_hit_on_subsequent_access(self):
        """2. Acceso subsecuente a la misma página genera un Page Hit sin fallo."""
        self.vmem.init_process_page_table(pid=10, num_pages=4)
        
        # Primer acceso: Page Fault
        self.vmem.translate_address(pid=10, virtual_address=8, current_tick=1)
        self.assertEqual(self.vmem.page_faults, 1)
        self.assertEqual(self.vmem.page_hits, 0)

        # Segundo acceso a la misma página (virtual_address=9 está en página 2): Page Hit
        hit_result = self.vmem.translate_address(pid=10, virtual_address=9, current_tick=2)
        self.assertFalse(hit_result["page_fault"])
        self.assertEqual(hit_result["page_number"], 2)
        self.assertEqual(hit_result["offset"], 1)
        self.assertEqual(self.vmem.page_hits, 1)
        self.assertEqual(self.vmem.hit_ratio, 50.0)

    def test_3_fifo_page_replacement(self):
        """3. Reemplazo FIFO: expulsa el marco más antiguo cuando se saturan los marcos."""
        self.vmem.replacement_algorithm = "FIFO"
        self.vmem.init_process_page_table(pid=1, num_pages=10)

        # Llenar los 4 marcos disponibles con páginas 0, 1, 2, 3
        # Marcos asignados: Marco 0 -> P0, Marco 1 -> P1, Marco 2 -> P2, Marco 3 -> P3
        for page in range(4):
            self.vmem.translate_address(pid=1, virtual_address=page * 4, current_tick=page + 1)

        self.assertEqual(self.vmem.page_faults, 4)
        self.assertEqual(self.vmem.page_replacements, 0)

        # Acceder a página 4: debe expulsar la más antigua según FIFO (Página 0 en Marco 0)
        trans = self.vmem.translate_address(pid=1, virtual_address=16, current_tick=5)
        self.assertTrue(trans["page_fault"])
        self.assertEqual(trans["frame_number"], 0) # Ocupa el marco 0 liberado
        self.assertIsNotNone(trans["victim_info"])
        self.assertEqual(trans["victim_info"]["victim_page"], 0)
        self.assertEqual(self.vmem.page_replacements, 1)

        # Verificar que la tabla de páginas marcó la página 0 como no válida
        table = self.vmem.get_page_table(pid=1)
        self.assertFalse(table[0].is_valid)
        self.assertIsNone(table[0].frame_number)
        self.assertTrue(table[4].is_valid)
        self.assertEqual(table[4].frame_number, 0)

    def test_4_lru_page_replacement(self):
        """4. Reemplazo LRU: expulsa la página menos recientemente referenciada."""
        vmem_lru = VirtualMemory(
            swap_size=1024,
            page_size=4,
            total_frames=3,
            replacement_algorithm="LRU",
            logger=self.logger,
        )
        vmem_lru.init_process_page_table(pid=2, num_pages=10)

        # Cargar páginas 0 (tick 1), 1 (tick 2), 2 (tick 3)
        vmem_lru.translate_address(pid=2, virtual_address=0, current_tick=1)
        vmem_lru.translate_address(pid=2, virtual_address=4, current_tick=2)
        vmem_lru.translate_address(pid=2, virtual_address=8, current_tick=3)

        # Re-referenciar página 0 en tick 4 (ahora la menos recientemente usada es página 1!)
        vmem_lru.translate_address(pid=2, virtual_address=0, current_tick=4)

        # Cargar página 3 en tick 5: en FIFO se expulsaría página 0, pero en LRU se expulsa página 1!
        trans = vmem_lru.translate_address(pid=2, virtual_address=12, current_tick=5)
        self.assertTrue(trans["page_fault"])
        self.assertEqual(trans["victim_info"]["victim_page"], 1)

    def test_5_dirty_page_saved_to_swap_on_eviction(self):
        """5. Páginas marcadas como dirty ocupan espacio en SWAP al ser expulsadas."""
        self.vmem.init_process_page_table(pid=1, num_pages=10)
        
        # Cargar 4 páginas
        for page in range(4):
            self.vmem.translate_address(pid=1, virtual_address=page * 4, current_tick=page + 1)

        # Modificar página 0 mediante una operación de escritura (is_write=True)
        self.vmem.translate_address(pid=1, virtual_address=0, current_tick=5, is_write=True)
        table = self.vmem.get_page_table(pid=1)
        self.assertTrue(table[0].is_dirty)

        self.assertEqual(self.vmem.used_swap, 0)

        # Forzar expulsión cargando página 4
        self.vmem.translate_address(pid=1, virtual_address=16, current_tick=6)
        
        # Como página 0 estaba dirty, debe haber sido escrita en SWAP (4 MB)
        self.assertEqual(self.vmem.used_swap, 4)
        self.assertEqual(table[0].swap_slot, 0)

    def test_6_release_process_pages(self):
        """6. Liberación de recursos al terminar proceso: libera marcos y espacio en SWAP."""
        self.vmem.init_process_page_table(pid=1, num_pages=6)
        # Cargar y expulsar para ocupar SWAP
        for page in range(5):
            self.vmem.translate_address(pid=1, virtual_address=page * 4, current_tick=page + 1, is_write=True)

        self.assertGreater(self.vmem.used_swap, 0)
        self.vmem.release_process_pages(pid=1)

        # Todo el SWAP y marcos deben haber quedado completamente liberados
        self.assertEqual(self.vmem.used_swap, 0)
        self.assertEqual(sum(1 for f in self.vmem._frames if f is not None), 0)
        self.assertIsNone(self.vmem.get_page_table(pid=1))


if __name__ == "__main__":
    unittest.main()
