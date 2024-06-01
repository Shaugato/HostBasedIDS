import unittest
from HIDS.logger import Logger

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.logger = Logger()

    def test_log(self):
        self.logger.log("test message", level="INFO")
        self.assertEqual(len(self.logger.logs), 1)
        self.assertIn("test message", self.logger.logs[0]['message'])

    def test_get_logs(self):
        self.logger.log("test message 1", level="INFO")
        self.logger.log("test message 2", level="ERROR")
        logs = self.logger.get_logs()
        self.assertEqual(len(logs), 2)
        self.assertIn("test message 1", logs[0]['message'])
        self.assertIn("test message 2", logs[1]['message'])

    def test_clear_logs(self):
        self.logger.log("test message", level="INFO")
        self.logger.clear_logs()
        self.assertEqual(len(self.logger.logs), 0)

    def test_log_with_different_levels(self):
        self.logger.log("info message", level="INFO")
        self.logger.log("warning message", level="WARNING")
        self.logger.log("error message", level="ERROR")
        logs = self.logger.get_logs()
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0]['level'], "INFO")
        self.assertEqual(logs[1]['level'], "WARNING")
        self.assertEqual(logs[2]['level'], "ERROR")

if __name__ == '__main__':
    unittest.main()

