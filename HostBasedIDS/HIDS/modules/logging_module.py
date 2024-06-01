import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from queue import Queue
import threading
import json
import requests
from .abstract_module import AbstractModule

class LoggingModule(AbstractModule):
    def __init__(self, logger: Queue, log_file_path: str = "/var/log/hids.log"):
        super().__init__(logger)
        self.logger = logger
        self.log_file_path = log_file_path

    def _run(self):
        self.log("Logging module started", logging.INFO)
        while not self.stop_event.is_set():
            try:
                if not self.logger.empty():
                    entry = self.logger.get()
                    self.process_log_entry(entry)
                else:
                    self.stop_event.wait(1)
            except Exception as e:
                self.log(f"Error processing log entry: {e}", logging.ERROR)

    def process_log_entry(self, entry):
        try:
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(f"{entry['timestamp']} - {entry['level']} - {entry['message']}\n")

            if entry['level'] == logging.ERROR:
                self.alert_contacts(entry['message'])
        except Exception as e:
            self.log(f"Failed to write log entry: {e}", logging.ERROR)

    def alert_contacts(self, message):
        self.alert_email(message)
        self.alert_slack(message)

    def alert_email(self, message):
        try:
            sender_email = "your-email@example.com"
            receiver_email = "admin@example.com"
            smtp_server = "smtp.example.com"
            smtp_port = 587  # Usually 587 for TLS, 465 for SSL
            smtp_user = "your-email@example.com"
            smtp_password = "your-email-password"

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = "HIDS - Error Alert"

            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())

            self.log(f"Email alert sent: {message}", logging.INFO)
        except Exception as e:
            self.log(f"Failed to send email alert: {e}", logging.ERROR)

    def alert_slack(self, message):
        try:
            webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            slack_data = {'text': f"An error has been flagged by the HIDS: `{message}`"}
            response = requests.post(
                webhook_url, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                raise ValueError(
                    f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
                )
            self.log(f"Slack alert sent: {message}", logging.INFO)
        except Exception as e:
            self.log(f"Failed to send Slack alert: {e}", logging.ERROR)
