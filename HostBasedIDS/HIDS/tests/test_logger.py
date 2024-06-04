import unittest
from unittest.mock import patch, MagicMock, call
import logging
from queue import Queue
from HIDS.logger import Logger

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.logger = Logger()

    def test_log(self):
        self.logger.log("Test message", logging.INFO)
        log_entry = self.logger.queue.get()
        self.assertEqual(log_entry[1], "Test message")
        self.assertEqual(log_entry[0], logging.INFO)

    def test_get_logs(self):
        self.logger.log("Test message", logging.INFO)
        logs = self.logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][1], "Test message")

    def test_clear_logs(self):
        self.logger.log("Test message", logging.INFO)
        self.logger.clear_logs()
        logs = self.logger.get_logs()
        self.assertEqual(len(logs), 0)

    @patch("builtins.print")
    def test_process_log_entry(self, mock_print):
        entry = (logging.INFO, "Test message")
        self.logger.process_log_entry(entry)
        mock_print.assert_called_with("INFO: Test message")

    @patch("HIDS.logger.Logger.alert_email")
    @patch("HIDS.logger.Logger.alert_slack")
    @patch("builtins.print")
    def test_process_log_entry_error(self, mock_print, mock_alert_slack, mock_alert_email):
        entry = (logging.ERROR, "Test error message")
        self.logger.process_log_entry(entry)
        mock_print.assert_called_with("ERROR: Test error message")
        mock_alert_email.assert_called_once_with("Test error message")
        mock_alert_slack.assert_called_once_with("Test error message")

    @patch("smtplib.SMTP")
    def test_alert_email(self, mock_smtp):
        mock_server = mock_smtp.return_value.__enter__.return_value
        self.logger.alert_email("Test email message")
        self.assertFalse(self.logger.queue.empty())
        log_entry = self.logger.queue.get()
        self.assertEqual(log_entry[1], "Email alert sent successfully.")
        self.assertEqual(log_entry[0], logging.INFO)
        mock_server.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_alert_email_failure(self, mock_smtp):
        mock_smtp.side_effect = Exception("SMTP error")
        self.logger.alert_email("Test email message")
        self.assertFalse(self.logger.queue.empty())
        log_entry = self.logger.queue.get()
        self.assertIn("Failed to send email alert", log_entry[1])
        self.assertEqual(log_entry[0], logging.ERROR)

    @patch("requests.post")
    def test_alert_slack(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.logger.alert_slack("Test Slack message")
        self.assertFalse(self.logger.queue.empty())
        log_entry = self.logger.queue.get()
        self.assertEqual(log_entry[1], "Slack alert sent successfully.")
        self.assertEqual(log_entry[0], logging.INFO)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_alert_slack_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_post.return_value = mock_response

        self.logger.alert_slack("Test Slack message")
        self.assertFalse(self.logger.queue.empty())
        log_entry = self.logger.queue.get()
        self.assertIn("Failed to send Slack alert", log_entry[1])
        self.assertEqual(log_entry[0], logging.ERROR)
        mock_post.assert_called_once()

if __name__ == "__main__":
    unittest.main()
