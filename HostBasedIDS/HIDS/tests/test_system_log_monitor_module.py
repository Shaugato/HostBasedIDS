import unittest
from unittest.mock import patch, mock_open
from queue import Queue
from HIDS.modules.system_log_monitor_module import SystemLogMonitorModule
from HIDS.utils.synchronous_interval_scheduler import SynchronousIntervalScheduler
import logging

class TestSystemLogMonitorModule(unittest.TestCase):
    def setUp(self):
        self.logger = Queue()
        self.monitor = SystemLogMonitorModule(self.logger, syslog_path="/var/log/test_syslog.log", kernlog_path="/var/log/test_kern.log")

    @patch("builtins.open", new_callable=mock_open, read_data="Jan  1 12:00:00 localhost kernel: [Hardware Error]: Machine check events logged\n")
    def test_parse_log_file(self, mock_file):
        entries = self.monitor.parse_log_file("/var/log/test_kern.log")
        self.assertEqual(len(entries), 1)
        self.assertIn("Hardware Error", entries[0]['message'])

    @patch("HIDS.modules.system_log_monitor_module.SystemLogMonitorModule.parse_log_file")
    def test_check_logs(self, mock_parse_log_file):
        mock_parse_log_file.side_effect = [
            [{'timestamp': 'Jan  1 12:00:00', 'level': logging.WARNING, 'message': 'syslog message'}],
            [{'timestamp': 'Jan  1 12:00:00', 'level': logging.WARNING, 'message': 'kernlog message'}]
        ]
        self.monitor.check_logs()
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertIn("syslog message", log_entry['message'])

    def test_is_unusual_activity(self):
        self.assertTrue(self.monitor.is_unusual_activity("error: something went wrong"))
        self.assertTrue(self.monitor.is_unusual_activity("fail: operation failed"))
        self.assertFalse(self.monitor.is_unusual_activity("normal operation message"))

    def test_extract_timestamp(self):
        log_entry = "Jan  1 12:00:00 localhost kernel: [Hardware Error]: Machine check events logged\n"
        timestamp = self.monitor.extract_timestamp(log_entry)
        self.assertEqual(timestamp, "Jan  1 12:00:00")

if __name__ == '__main__':
    unittest.main()
