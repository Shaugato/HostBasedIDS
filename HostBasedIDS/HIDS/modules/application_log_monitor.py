import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .abstract_module import AbstractModule

class ApplicationLogMonitor(AbstractModule):
    def __init__(self, logger: Queue, log_file_path: str):
        super().__init__(logger)
        self.log_file_path = log_file_path
        self.observer = Observer()
        self.log("Application log monitoring started", "INFO")

    def run(self):
        event_handler = self.LogFileChangeHandler(self)
        self.observer.schedule(event_handler, os.path.dirname(self.log_file_path), recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    class LogFileChangeHandler(FileSystemEventHandler):
        def __init__(self, monitor):
            self.monitor = monitor

        def on_modified(self, event):
            if event.src_path == self.monitor.log_file_path:
                self.monitor.handle_log_file_change()

    def handle_log_file_change(self):
        try:
            new_log_entry = self.read_new_log_entries()
            if self.is_error(new_log_entry):
                self.log("Alert: Error detected in the application log.", "WARNING")
                self.forward_log_to_reports(new_log_entry)
                self.kill_associated_processes(new_log_entry)
        except Exception as e:
            self.log(f"WARNING!: Error: {str(e)}", "ERROR")

    def read_new_log_entries(self):
        with open(self.log_file_path, 'r') as file:
            log_entries = file.readlines()
        return log_entries[-1] if log_entries else None

    def is_error(self, log_entry):
        return log_entry and ("error" in log_entry.lower() or "exception" in log_entry.lower())

    def forward_log_to_reports(self, log_entry):
        self.send_email_to_sysadmin("Suspicious Activity Detected in the application log", f"Log File: {self.log_file_path}\nLog Entry: {log_entry}")

    def send_email_to_sysadmin(self, subject, body):
        msg = MIMEMultipart()
        msg['From'] = 'sysadmin@example.com'
        msg['To'] = 'moderator@hids.com'
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login('sysadmin@example.com', 'password')
        server.sendmail('sysadmin@example.com', 'moderator@hids.com', msg.as_string())
        server.quit()

    def kill_associated_processes(self, log_entry):
        match = re.search(r"ProcessID=(\d+)", log_entry)
        if match:
            process_id = int(match.group(1))
            try:
                os.kill(process_id, 9)
                self.log(f"Killed Process ID {process_id} that was associated with the error.", "INFO")
            except Exception as e:
                self.log(f"WARNING!: Error: {str(e)}", "ERROR")
