import unittest
from unittest.mock import patch, MagicMock
from queue import Queue
from HIDS.modules.monitor_process_and_commands import MonitorProcessAndCommands
import logging

class TestMonitorProcessAndCommands(unittest.TestCase):
    def setUp(self):
        self.logger = Queue()
        self.monitor = MonitorProcessAndCommands(self.logger)

    @patch("psutil.process_iter")
    def test_monitor_processes(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.info = {'name': 'nmap', 'pid': 1234, 'memory_info': MagicMock(rss=1000000)}
        mock_process_iter.return_value = [mock_process]
        
        with patch.object(mock_process, 'terminate') as mock_terminate:
            self.monitor.monitor_processes()
            mock_terminate.assert_called_once()
            self.assertFalse(self.logger.empty())
            log_entry = self.logger.get()
            self.assertIn("Terminating forbidden process", log_entry['message'])

    @patch("psutil.process_iter")
    def test_monitor_processes_memory_threshold(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.info = {'name': 'docker', 'pid': 1234, 'memory_info': MagicMock(rss=600 * 1024 * 1024)}
        mock_process_iter.return_value = [mock_process]

        with patch.object(mock_process, 'terminate') as mock_terminate:
            self.monitor.monitor_processes()
            mock_terminate.assert_called_once()
            self.assertFalse(self.logger.empty())
            log_entry = self.logger.get()
            self.assertIn("Terminating process exceeding memory threshold", log_entry['message'])

if __name__ == '__main__':
    unittest.main()
