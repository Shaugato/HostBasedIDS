import os
import re
import logging
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict
from .abstract_module import AbstractModule

class AuthenticationLog(AbstractModule):
    def __init__(self, logger: Queue, log_file_path: str = "/var/log/auth.log"):
        super().__init__(logger)
        self.log_file_path = log_file_path
        self.failed_login_attempts = defaultdict(int)
        self.observer = Observer()

    def _run(self):
        event_handler = self.LogFileHandler(self)
        self.observer.schedule(event_handler, os.path.dirname(self.log_file_path), recursive=False)
        self.observer.start()
        self.log("Authentication log monitoring started", logging.INFO)
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
            self.monitor_authentication(last_line)

    def monitor_authentication(self, log_entry: str):
        pattern = r"(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+)\[\d+\]:\s+(.*)"
        match = re.match(pattern, log_entry)
        if match:
            timestamp, host, process, message = match.groups()
            if "Failed password" in message or "Invalid user" in message:
                ip_address = self.extract_ip(message)
                self.failed_login_attempts[ip_address] += 1
                self.log(f"Failed login attempt from {ip_address}. Count: {self.failed_login_attempts[ip_address]}", logging.WARNING)
                self.check_failed_attempts(ip_address)

    def extract_ip(self, message: str) -> str:
        pattern = r"(\d+\.\d+\.\d+\.\d+)"
        match = re.search(pattern, message)
        return match.group(1) if match else "Unknown IP"

    def check_failed_attempts(self, ip_address=None):
        for ip, count in self.failed_login_attempts.items():
            if count >= 5:
                self.log_alert(f"Too many failed login attempts from IP: {ip}. Taking action.")
                if ip_address and ip == ip_address:
                    self.failed_login_attempts[ip] = 0
                    self.block_ip(ip)

    def block_ip(self, ip_address: str):
        try:
            os.system(f"sudo iptables -A INPUT -s {ip_address} -j DROP")
            self.log(f"Blocked IP {ip_address} due to excessive failed login attempts.", logging.INFO)
        except Exception as e:
            self.log(f"Failed to block IP {ip_address}: {e}", logging.ERROR)

    def log_alert(self, message):
        self.log(message, logging.WARNING)
    
    def log_file_changed(self, log_file_path):
        self.process_log()
