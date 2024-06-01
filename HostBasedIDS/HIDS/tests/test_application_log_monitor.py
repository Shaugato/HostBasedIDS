import unittest
from queue import Queue
from unittest.mock import patch, mock_open, call
from HIDS.modules.application_log_monitor import ApplicationLogMonitor
import logging
import smtplib

class TestApplicationLogMonitor(unittest.TestCase):
    def setUp(self):
        self.logger = Queue()
        self.monitor = ApplicationLogMonitor(self.logger, "/var/log/test_application.log")

    @patch("builtins.open", new_callable=mock_open, read_data="Error: something went wrong\nWarning: potential issue detected\n")
    def test_log_file_changed(self, mock_file):
        self.monitor.log_file_changed("/var/log/test_application.log")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.WARNING)
        self.assertIn("Error detected in the application log", log_entry['message'])
        
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Warning: potential issue detected", log_entry['message'])

    def test_is_error(self):
        self.assertTrue(self.monitor.is_error("error: something failed"))
        self.assertFalse(self.monitor.is_error("all is good"))

    @patch("smtplib.SMTP")
    def test_send_email_to_sysadmin(self, mock_smtp):
        self.monitor.send_email_to_sysadmin("Test Subject", "Test Body")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Sending email to sysadmin", log_entry['message'])
        mock_smtp.assert_called_once()

    @patch("psutil.Process.terminate")
    @patch("psutil.Process", autospec=True)
    def test_kill_associated_processes(self, mock_process, mock_terminate):
        log_entry = "ProcessID=1234"
        mock_process.return_value = mock_process
        self.monitor.kill_associated_processes(log_entry)
        mock_process.assert_called_once_with(1234)
        mock_terminate.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data="Error: something went wrong\n")
    def test_read_new_log_entries(self, mock_file):
        new_entries = self.monitor.read_new_log_entries("/var/log/test_application.log")
        self.assertEqual(new_entries, "Error: something went wrong")

    def test_forward_log_to_reports(self):
        with patch.object(self.monitor, 'send_email_to_sysadmin') as mock_send_email:
            self.monitor.forward_log_to_reports("Error: something went wrong")
            mock_send_email.assert_called_once_with("Suspicious Activity Detected in the application log", "Log File: /var/log/test_application.log\nLog Entry: Error: something went wrong")

if __name__ == '__main__':
    unittest.main()

