"""Pruebas de integración V10 con el kernel REAL, sin servicios externos."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Auto"))
sys.path.insert(0, str(ROOT / "AutoOS_1"))
from Auto.bridge_react_kernel import sync_react_with_kernel
from src.core.kernel import Kernel


def request(req_id="test1", tick=3, processes=None, battery=82):
    return {"type": "autoos:kernel-sync", "requestId": req_id,
            "tick": tick, "batteryPct": battery,
            "processes": processes if processes is not None else [
                {"pid": 500, "name": "Prueba CPU", "memoryMb": 120,
                 "priority": 3, "burstTime": 25},
                {"pid": 501, "name": "GPS", "memoryMb": 80,
                 "priority": 2, "burstTime": 20},
            ]}


class PythonKernelBridgeTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.kernel = Kernel(memory_mb=2048, swap_mb=4096,
                             vfs_path=str(Path(self.dir.name) / "vfs.json"))
        self.state = {}

    def tearDown(self):
        self.dir.cleanup()

    def test_real_allocation_and_tick(self):
        result = sync_react_with_kernel(request(), self.kernel, self.state, True)
        self.assertTrue(result["booted"])
        self.assertEqual(result["tick"], 3)
        self.assertEqual(len(result["mappedPids"]), 2)
        self.assertGreaterEqual(result["ramMb"], 200)
        self.assertNotEqual(result["mappedPids"]["500"], 500)

    def test_idempotent_repeat_does_not_double_reserve(self):
        first = sync_react_with_kernel(request(), self.kernel, self.state, True)
        again = sync_react_with_kernel(request(), self.kernel, self.state, True)
        self.assertEqual(first["ramMb"], again["ramMb"])
        self.assertEqual(first["tick"], again["tick"])
        self.assertEqual(first["mappedPids"], again["mappedPids"])

    def test_removing_js_process_releases_real_allocation(self):
        first = sync_react_with_kernel(request(), self.kernel, self.state, True)
        second = sync_react_with_kernel(request(req_id="test2", tick=4, processes=[]),
                                        self.kernel, self.state, True)
        self.assertEqual(len(second["mappedPids"]), 0)
        self.assertLess(second["ramMb"], first["ramMb"])

    def test_rbac_denied_does_not_boot_or_write(self):
        result = sync_react_with_kernel(request(), self.kernel, self.state, False)
        self.assertFalse(result["booted"])
        self.assertIn("RBAC", " ".join(result["errors"]))
        self.assertEqual(len(self.kernel.engine.get_all_processes()), 0)

    def test_invalid_payload_and_limits(self):
        packet = request()
        packet["processes"] = [{"pid": 9, "name": "XX", "priority": 3,
                                 "memoryMb": 9999999, "burstTime": 3}]
        result = sync_react_with_kernel(packet, self.kernel, self.state, True)
        self.assertFalse(result["booted"])
        self.assertTrue(result["errors"])

    def test_ticks_are_limited(self):
        result = sync_react_with_kernel(request(tick=800), self.kernel, self.state, True)
        self.assertEqual(result["tick"], 12)


if __name__ == '__main__':
    unittest.main()
