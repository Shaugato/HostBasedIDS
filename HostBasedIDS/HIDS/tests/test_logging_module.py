import unittest
from unittest.mock import patch, mock_open, MagicMock
from queue import Queue
from HIDS.modules.logging_module import LoggingModule
import logging
import json

class TestLoggingModule(unittest.TestCase):
    def setUp(self):
        self.logger = Queue()
        self.logging_module = LoggingModule(self.logger, "/var/log/test_hids.log")

    @patch("builtins.open", new_callable=mock_open)
    def test_process_log_entry(self, mock_file):
        entry = {'timestamp': '2023-01-01 12:00:00', 'level': logging.ERROR, 'message': 'Test error message'}
        self.logging_module.process_log_entry(entry)
        mock_file().write.assert_called_once_with("2023-01-01 12:00:00 - 40 - Test error message\n")

    @patch("HIDS.modules.logging_module.LoggingModule.alert_email")
    @patch("HIDS.modules.logging_module.LoggingModule.alert_slack")
    @patch("builtins.open", new_callable=mock_open)
    def test_process_log_entry_error(self, mock_file, mock_alert_slack, mock_alert_email):
        entry = {'timestamp': '2023-01-01 12:00:00', 'level': logging.ERROR, 'message': 'Test error message'}
        self.logging_module.process_log_entry(entry)
        mock_alert_email.assert_called_once_with('Test error message')
        mock_alert_slack.assert_called_once_with('Test error message')

    @patch("smtplib.SMTP")
    def test_alert_email(self, mock_smtp):
        self.logging_module.alert_email("Test email message")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Email alert sent", log_entry['message'])

    @patch("smtplib.SMTP")
    def test_alert_email_failure(self, mock_smtp):
        mock_smtp.side_effect = Exception("SMTP error")
        self.logging_module.alert_email("Test email message")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.ERROR)
        self.assertIn("Failed to send email alert", log_entry['message'])

    @patch("requests.post")
    def test_alert_slack(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.logging_module.alert_slack("Test Slack message")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Slack alert sent", log_entry['message'])

    @patch("requests.post")
    def test_alert_slack_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_post.return_value = mock_response

        self.logging_module.alert_slack("Test Slack message")
        self.assertFalse(self.logger.empty())
        log_entry = self.logger.get()
        self.assertEqual(log_entry['level'], logging.ERROR)
        self.assertIn("Failed to send Slack alert", log_entry['message'])

if __name__ == "__main__":
    unittest.main()
