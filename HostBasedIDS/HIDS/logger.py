import logging
from queue import Queue

class Logger:
    def __init__(self):
        self.queue = Queue()
        self.logs = []

    def log(self, message, level=logging.INFO):
        log_entry = (level, message)
        self.queue.put(log_entry)
        self.logs.append(log_entry)
        print(f"{logging.getLevelName(level)}: {message}")

    def get_logs(self):
        return list(self.logs)

    def clear_logs(self):
        self.logs.clear()

    def process_log_entry(self, entry):
        level, message = entry
        # Here we print the log entry, but in a real system, we might write it to a file or database.
        print(f"{logging.getLevelName(level)}: {message}")
        if level == logging.ERROR:
            self.alert_contacts(message)

    def alert_contacts(self, message):
        # Send alerts via email or other communication channels
        self.alert_email(message)
        self.alert_slack(message)

    def alert_email(self, message):
        try:
            import smtplib
            from email.mime.text import MIMEText

            # Replace with your SMTP server details
            smtp_server = "smtp.example.com"
            smtp_port = 587
            smtp_username = "your_username"
            smtp_password = "your_password"
            from_address = "alert@example.com"
            to_address = "admin@example.com"

            msg = MIMEText(message)
            msg["Subject"] = "HIDS Alert"
            msg["From"] = from_address
            msg["To"] = to_address

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(from_address, to_address, msg.as_string())

            self.log("Email alert sent successfully.", logging.INFO)
        except Exception as e:
            self.log(f"Failed to send email alert: {e}", logging.ERROR)

    def alert_slack(self, message):
        try:
            import requests

            webhook_url = "https://hooks.slack.com/services/your/webhook/url"
            payload = {"text": message}
            response = requests.post(webhook_url, json=payload)

            if response.status_code == 200:
                self.log("Slack alert sent successfully.", logging.INFO)
            else:
                self.log(f"Failed to send Slack alert: {response.status_code} {response.text}", logging.ERROR)
        except Exception as e:
            self.log(f"Failed to send Slack alert: {e}", logging.ERROR)
