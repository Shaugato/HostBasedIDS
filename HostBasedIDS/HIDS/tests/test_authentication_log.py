import unittest
from queue import Queue
from unittest.mock import patch, mock_open, MagicMock
from HIDS.modules.authentication_log import AuthenticationLog
import logging

class TestAuthenticationLog(unittest.TestCase):
    def setUp(self):
        self.logger = Queue()
        self.monitor = AuthenticationLog(self.logger, "/var/log/auth.log")

    @patch("builtins.open", new_callable=mock_open, read_data="Jan 1 12:00:00 localhost sshd[12345]: Failed password for invalid user root from 192.168.1.1 port 22 ssh2\n")
    def test_process_log(self, mock_file):
        self.monitor.process_log()
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.WARNING)
        self.assertIn("Failed login attempt from 192.168.1.1. Count: 1", log_entry['message'])

    @patch("os.system")
    def test_block_ip(self, mock_system):
        self.monitor.block_ip("192.168.1.1")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Blocked IP 192.168.1.1 due to excessive failed login attempts", log_entry['message'])
        mock_system.assert_called_with("sudo iptables -A INPUT -s 192.168.1.1 -j DROP")

    def test_extract_ip(self):
        message = "Failed password for invalid user root from 192.168.1.1 port 22 ssh2"
        ip_address = self.monitor.extract_ip(message)
        self.assertEqual(ip_address, "192.168.1.1")

    def test_check_failed_attempts(self):
        self.monitor.failed_login_attempts["192.168.1.1"] = 5
        with patch.object(self.monitor, 'log_alert') as mock_log_alert:
            self.monitor.check_failed_attempts("192.168.1.1")
            mock_log_alert.assert_called_once_with("Too many failed login attempts from IP: 192.168.1.1. Taking action.")
            self.assertEqual(self.monitor.failed_login_attempts["192.168.1.1"], 0)

    @patch("os.system")
    def test_check_failed_attempts_block_ip(self, mock_system):
        self.monitor.failed_login_attempts["192.168.1.1"] = 5
        self.monitor.check_failed_attempts("192.168.1.1")
        mock_system.assert_called_once_with("sudo iptables -A INPUT -s 192.168.1.1 -j DROP")

    @patch("builtins.open", new_callable=mock_open, read_data="Jan 1 12:00:00 localhost sshd[12345]: Invalid user admin from 192.168.1.2\n")
    def test_log_file_changed(self, mock_file):
        self.monitor.log_file_changed("/var/log/auth.log")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.WARNING)
        self.assertIn("Failed login attempt from 192.168.1.2. Count: 1", log_entry['message'])

    @patch("os.system")
    @patch("builtins.open", new_callable=mock_open, read_data="Jan 1 12:00:00 localhost sshd[12345]: Failed password for invalid user root from 192.168.1.1 port 22 ssh2\n")
    def test_monitor_authentication(self, mock_file, mock_system):
        for _ in range(5):
            self.monitor.process_log()
        
        # Verify the warning about too many failed login attempts
        found_alert = False
        while not self.logger.empty():
            log_entry = self.logger.get()
            if log_entry['level'] == logging.WARNING and "Too many failed login attempts from IP: 192.168.1.1. Taking action." in log_entry['message']:
                found_alert = True
                break
        
        self.assertTrue(found_alert)
        mock_system.assert_called_with("sudo iptables -A INPUT -s 192.168.1.1 -j DROP")

if __name__ == '__main__':
    unittest.main()
