import logging
from queue import Queue
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

class LoggingModule:
    def __init__(self, logger: Queue):
        self.logger = logger
        self.log("Logging module loaded", "INFO")
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while True:
            if not self.logger.empty():
                entry = self.logger.get()
                self.write_log(entry)
                if entry['level'] == 'ERROR':
                    self.alert_email(entry['message'])
                    self.alert_slack(entry['message'])
            else:
                time.sleep(1)

    def log(self, message: str, level: str = "INFO"):
        self.logger.put({"message": message, "level": level, "source": self.__class__.__name__})

    def write_log(self, entry):
        logger = setup_logger('main_logger', 'system.log')
        logger.log(getattr(logging, entry['level']), entry['message'])

    def alert_email(self, entry_message):
        msg = MIMEMultipart()
        msg['From'] = 'sysadmin@example.com'
        msg['To'] = 'moderator@hids.com'
        msg['Subject'] = 'HIDS - Error Alert'
        msg.attach(MIMEText(f"<b>An error has been flagged by the HIDS: </b><br>{entry_message}", 'html'))
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login('sysadmin@example.com', 'password')
        server.sendmail('sysadmin@example.com', 'moderator@hids.com', msg.as_string())
        server.quit()

    def alert_slack(self, entry_message):
        webhook = "https://discord.com/api/webhooks/1152826400693297232/yiU7OLiUlUMGbzkYifAqINS4lk2ubeM7KuaNeDfNF4IKL78pvaYe5YrOVqCAG1XYqjhi/slack"
        payload = {"text": f"An error has been flagged by the HIDS: `{entry_message}`"}
        requests.post(webhook, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

