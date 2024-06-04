import os
import re
from queue import Queue
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .abstract_module import AbstractModule
import psutil

class ApplicationLogMonitor(AbstractModule):
    def __init__(self, logger: Queue, log_file_path: str):
        super().__init__(logger)
        self.log_file_path = log_file_path
        self.observer = Observer()

    def _run(self):
        event_handler = self.LogFileHandler(self)
        self.observer.schedule(event_handler, os.path.dirname(self.log_file_path), recursive=False)
        self.observer.start()
        self.log("Application log monitoring started", logging.INFO)
        try:
            while not self.stop_event.is_set():
                self.stop_event.wait(1)
        finally:
            self.observer.stop()
            self.observer.join()

    class LogFileHandler(FileSystemEventHandler):
        def __init__(self, monitor):
            self.monitor = monitor

        def on_modified(self, event):
            if event.src_path == self.monitor.log_file_path:
                self.monitor.process_log()

    def process_log(self):
        with open(self.log_file_path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip() if lines else ""
            if self.is_error(last_line):
                self.log(f"Alert: Error detected in the application log: {last_line}", logging.ERROR)
                self.forward_log_to_reports(last_line)
                self.kill_associated_processes(last_line)
            elif self.is_warning(last_line):
                self.log(f"Log entry: {last_line}", logging.WARNING)
            else:
                self.log(f"Log entry: {last_line}", logging.INFO)

    def is_error(self, log_entry: str) -> bool:
        return "error" in log_entry.lower()

    def is_warning(self, log_entry: str) -> bool:
        return "warning" in log_entry.lower()

    def forward_log_to_reports(self, log_entry: str):
        self.send_email_to_sysadmin("Suspicious Activity Detected in Application Log", f"Log Entry: {log_entry}")

    def send_email_to_sysadmin(self, subject: str, body: str):
        try:
            sender_email = "your-email@example.com"
            receiver_email = "sysadmin@example.com"
            smtp_server = "smtp.example.com"
            smtp_port = 587  # Usually 587 for TLS, 465 for SSL
            smtp_user = "your-email@example.com"
            smtp_password = "your-email-password"

            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(sender_email, receiver_email, message.as_string())

            self.log(f"Email sent to sysadmin: {subject} - {body}", logging.INFO)
        except Exception as e:
            self.log(f"Failed to send email: {e}", logging.ERROR)

    def kill_associated_processes(self, log_entry: str):
        match = re.search(r'ProcessID=(\d+)', log_entry)
        if match:
            process_id = int(match.group(1))
            try:
                process = psutil.Process(process_id)
                process.terminate()
                self.log(f"Killed process with ID {process_id} associated with error log.", logging.INFO)
            except Exception as e:
                self.log(f"Failed to kill process {process_id}: {e}", logging.ERROR)

    def log_file_changed(self, log_file_path):
        new_log_entry = self.read_new_log_entries(log_file_path)
        if self.is_error(new_log_entry):
            self.log("Alert: Error detected in the application log.", logging.ERROR)
            self.forward_log_to_reports(new_log_entry)
            self.kill_associated_processes(new_log_entry)
        elif self.is_warning(new_log_entry):
            self.log(f"Log entry: {new_log_entry}", logging.WARNING)
        else:
            self.log(f"Log entry: {new_log_entry}", logging.INFO)

    def read_new_log_entries(self, log_file_path):
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
            return lines[-1].strip() if lines else ""
