import unittest
from unittest.mock import patch, MagicMock
from queue import Queue
from HIDS.modules.monitor_process_and_commands import MonitorProcessAndCommands
import logging
import psutil

class TestMonitorProcessAndCommands(unittest.TestCase):
    def setUp(self):
        self.logger = Queue()
        self.monitor = MonitorProcessAndCommands(self.logger)

    @patch("psutil.process_iter")
    def test_monitor_processes_forbidden(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.info = {'pid': 1234, 'name': 'nmap', 'memory_info': MagicMock(rss=100 * 1024 * 1024)}
        mock_process_iter.return_value = [mock_process]
        
        with patch.object(mock_process, 'terminate') as mock_terminate:
            self.monitor.monitor_processes()
            mock_terminate.assert_called_once()
            self.assertFalse(self.logger.empty())
            log_entry = self.logger.get()
            self.assertEqual(log_entry[1], logging.WARNING)
            self.assertIn("Terminating forbidden process: nmap", log_entry[0])

    @patch("psutil.process_iter")
    def test_monitor_processes_whitelisted_exceed_memory(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.info = {'pid': 1234, 'name': 'docker', 'memory_info': MagicMock(rss=600 * 1024 * 1024)}
        mock_process_iter.return_value = [mock_process]

        with patch.object(mock_process, 'terminate') as mock_terminate:
            self.monitor.monitor_processes()
            mock_terminate.assert_called_once()
            self.assertFalse(self.logger.empty())
            log_entry = self.logger.get()
            self.assertEqual(log_entry[1], logging.WARNING)
            self.assertIn("Terminating process exceeding memory threshold: docker", log_entry[0])

    @patch("psutil.process_iter")
    def test_monitor_processes_no_action(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.info = {'pid': 1234, 'name': 'safe_process', 'memory_info': MagicMock(rss=100 * 1024 * 1024)}
        mock_process_iter.return_value = [mock_process]

        with patch.object(mock_process, 'terminate') as mock_terminate:
            self.monitor.monitor_processes()
            mock_terminate.assert_not_called()
            self.assertTrue(self.logger.empty())

    @patch("psutil.process_iter")
    def test_monitor_processes_exception_handling(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.info = {'pid': 1234, 'name': 'nmap', 'memory_info': MagicMock(rss=100 * 1024 * 1024)}
        mock_process_iter.side_effect = psutil.NoSuchProcess(1234)

        self.monitor.monitor_processes()
        self.assertTrue(self.logger.empty())

if __name__ == "__main__":
    unittest.main()
