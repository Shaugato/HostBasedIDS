import unittest
from queue import Queue
from unittest.mock import patch
from HIDS.modules.logging_module import LoggingModule
import logging
import smtplib
import requests

class TestLoggingModule(unittest.TestCase):
    def setUp(self):
        self.logger_queue = Queue()
        self.logging_module = LoggingModule(self.logger_queue)

    @patch("HIDS.modules.logging_module.LoggingModule.alert_email")
    @patch("HIDS.modules.logging_module.LoggingModule.alert_slack")
    def test_process_log_entry(self, mock_alert_slack, mock_alert_email):
        entry = {'level': logging.ERROR, 'message': "test error message"}
        self.logging_module.process_log_entry(entry)
        mock_alert_email.assert_called_once_with("test error message")
        mock_alert_slack.assert_called_once_with("test error message")

        entry = {'level': logging.INFO, 'message': "test info message"}
        self.logging_module.process_log_entry(entry)
        mock_alert_email.assert_not_called()
        mock_alert_slack.assert_not_called()

    @patch("smtplib.SMTP")
    def test_alert_email(self, mock_smtp):
        self.logging_module.alert_email("test email message")
        self.assertFalse(self.logger_queue.empty())
        log_entry = self.logger_queue.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Sending email to sysadmin", log_entry['message'])
        mock_smtp.assert_called_once()

    @patch("requests.post")
    def test_alert_slack(self, mock_post):
        self.logging_module.alert_slack("test slack message")
        self.assertFalse(self.logger_queue.empty())
        log_entry = self.logger_queue.get()
        self.assertEqual(log_entry['level'], logging.INFO)
        self.assertIn("Sending alert to Slack", log_entry['message'])
        mock_post.assert_called_once()

    @patch("smtplib.SMTP")
    def test_alert_email_failure(self, mock_smtp):
        mock_smtp.side_effect = smtplib.SMTPException("SMTP error")
        with self.assertRaises(smtplib.SMTPException):
            self.logging_module.alert_email("test email message")
        self.assertFalse(self.logger_queue.empty())
        log_entry = self.logger_queue.get()
        self.assertEqual(log_entry['level'], logging.ERROR)
        self.assertIn("Failed to send email", log_entry['message'])

    @patch("requests.post")
    def test_alert_slack_failure(self, mock_post):
        mock_post.side_effect = requests.RequestException("Request error")
        with self.assertRaises(requests.RequestException):
            self.logging_module.alert_slack("test slack message")
        self.assertFalse(self.logger_queue.empty())
        log_entry = self.logger_queue.get()
        self.assertEqual(log_entry['level'], logging.ERROR)
        self.assertIn("Failed to send alert to Slack", log_entry['message'])

if __name__ == '__main__':
    unittest.main()

