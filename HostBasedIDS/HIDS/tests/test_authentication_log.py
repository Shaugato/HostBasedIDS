import unittest
from queue import Queue
from unittest.mock import patch, mock_open
from HIDS.modules.authentication_log import AuthenticationLog
import logging

class TestAuthenticationLog(unittest.TestCase):
    def setUp(self):
        self.logger = Queue()
        self.auth_log = AuthenticationLog(self.logger)

    @patch("builtins.open", new_callable=mock_open, read_data="Jan  1 12:00:00 localhost sshd[12345]: Failed password for invalid user from 192.168.0.1 port 22 ssh2\nJan  1 12:01:00 localhost sshd[12345]: Accepted password for user from 192.168.0.2 port 22 ssh2\n")
    def test_monitor_authentication(self, mock_file):
        test_line = "Jan  1 12:00:00 localhost sshd[12345]: Failed password for invalid user from 192.168.0.1 port 22 ssh2"
        self.auth_log.monitor_authentication(test_line)
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.WARNING)
        self.assertIn("Failed password", log_entry['message'])

        test_line = "Jan  1 12:01:00 localhost sshd[12345]: Accepted password for user from 192.168.0.2 port 22 ssh2"
        self.auth_log.monitor_authentication(test_line)
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Accepted password", log_entry['message'])

    def test_check_failed_attempts(self):
        self.auth_log.failed_login_attempts["192.168.0.1"] = 5
        self.auth_log.check_failed_attempts()
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertIn("Too many failed login attempts", log_entry['message'])

    def test_log_alert(self):
        self.auth_log.log_alert("Test Alert")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.WARNING)
        self.assertIn("Test Alert", log_entry['message'])

    @patch("builtins.open", new_callable=mock_open, read_data="Jan  1 12:00:00 localhost sshd[12345]: Failed password for invalid user from 192.168.0.1 port 22 ssh2\n")
    def test_on_changed(self, mock_file):
        self.auth_log.on_changed(None, None)
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.WARNING)
        self.assertIn("Failed password", log_entry['message'])

if __name__ == '__main__':
    unittest.main()

