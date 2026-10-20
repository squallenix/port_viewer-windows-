import unittest
import os
import psutil
from src.security import validate_pid, is_critical_process, is_sensitive_process
from src.port_scanner import scan_ports, PortItem
from src.process_manager import terminate_process_by_pid
from src.ui.app import PortViewerApp

class TestSecurityAndProcessManager(unittest.TestCase):
    def test_pid_validation(self):
        # Negative / zero / system PIDs
        ok, msg = validate_pid(-1)
        self.assertFalse(ok)
        
        ok, msg = validate_pid(0)
        self.assertFalse(ok)
        self.assertIn("BSOD", msg)
        
        ok, msg = validate_pid(4)
        self.assertFalse(ok)
        self.assertIn("BSOD", msg)

        # Self PID
        ok, msg = validate_pid(os.getpid())
        self.assertFalse(ok)
        self.assertIn("Port Viewer application itself", msg)

        # Valid arbitrary PID
        ok, msg = validate_pid(123456)
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_critical_process_protection(self):
        self.assertTrue(is_critical_process("smss.exe"))
        self.assertTrue(is_critical_process("CSRSS.EXE"))
        self.assertTrue(is_critical_process("wininit.exe"))
        self.assertTrue(is_critical_process("services.exe"))
        self.assertTrue(is_critical_process("lsass.exe"))
        
        self.assertFalse(is_critical_process("node.exe"))
        self.assertFalse(is_critical_process("python.exe"))
        self.assertFalse(is_critical_process("nginx.exe"))

    def test_sensitive_process_flag(self):
        self.assertTrue(is_sensitive_process("svchost.exe"))
        self.assertTrue(is_sensitive_process("explorer.exe"))
        self.assertFalse(is_sensitive_process("node.exe"))

    def test_safe_termination_blocks_critical(self):
        # Attempting to terminate PID 4 should immediately be rejected
        res = terminate_process_by_pid(4)
        self.assertFalse(res.success)
        self.assertIn("BSOD", res.message)

        # Attempting to terminate PID 0 should immediately be rejected
        res0 = terminate_process_by_pid(0)
        self.assertFalse(res0.success)

        # Non-existent PID
        res_non = terminate_process_by_pid(9999999)
        self.assertFalse(res_non.success)
        self.assertIn("no longer running", res_non.message)

    def test_scan_ports(self):
        ports = scan_ports()
        self.assertIsInstance(ports, list)
        self.assertGreater(len(ports), 0)
        
        first = ports[0]
        self.assertIsInstance(first, PortItem)
        self.assertIn(first.protocol, ["TCP", "UDP"])
        self.assertIsInstance(first.local_port, int)

    def test_column_sorting(self):
        # Create mock dummy items to verify sorting logic
        items = [
            PortItem("TCP", "127.0.0.1", 8080, "", None, "LISTEN", 100, "node.exe", "", 0.0, 50.0, False, False),
            PortItem("UDP", "0.0.0.0", 3000, "", None, "ACTIVE", 200, "python.exe", "", 0.0, 120.0, False, False),
            PortItem("TCP", "0.0.0.0", 5432, "", None, "LISTEN", 50, "postgres.exe", "", 0.0, 80.0, False, False),
        ]

        # Use an instance of PortViewerApp logic without opening full GUI
        # Test helper method directly
        class MockApp:
            sort_column = "PORT"
            sort_ascending = True
            _sort_items = PortViewerApp._sort_items

        app = MockApp()

        # 1. Port Ascending
        app.sort_column = "PORT"
        app.sort_ascending = True
        sorted_items = app._sort_items(items)
        self.assertEqual([x.local_port for x in sorted_items], [3000, 5432, 8080])

        # 2. Port Descending
        app.sort_ascending = False
        sorted_items = app._sort_items(items)
        self.assertEqual([x.local_port for x in sorted_items], [8080, 5432, 3000])

        # 3. PID Ascending
        app.sort_column = "PID"
        app.sort_ascending = True
        sorted_items = app._sort_items(items)
        self.assertEqual([x.pid for x in sorted_items], [50, 100, 200])

        # 4. PID Descending
        app.sort_ascending = False
        sorted_items = app._sort_items(items)
        self.assertEqual([x.pid for x in sorted_items], [200, 100, 50])

        # 5. Process Name Ascending
        app.sort_column = "PROCESS NAME"
        app.sort_ascending = True
        sorted_items = app._sort_items(items)
        self.assertEqual([x.process_name for x in sorted_items], ["node.exe", "postgres.exe", "python.exe"])

        # 6. Memory Descending
        app.sort_column = "MEMORY"
        app.sort_ascending = False
        sorted_items = app._sort_items(items)
        self.assertEqual([x.memory_mb for x in sorted_items], [120.0, 80.0, 50.0])

if __name__ == "__main__":
    unittest.main()
