import re
from collections import defaultdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .abstract_module import AbstractModule

class AuthenticationLogMonitor(AbstractModule):
    def __init__(self, logger: Queue):
        super().__init__(logger)
        self.auth_log_path = "/var/log/auth.log"
        self.failed_login_attempts = defaultdict(int)
        self.observer = Observer()
        self.log("AuthenticationLog module loaded", "INFO")

    def run(self):
        event_handler = self.LogFileChangeHandler(self)
        self.observer.schedule(event_handler, os.path.dirname(self.auth_log_path), recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
                self.check_failed_attempts()
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    class LogFileChangeHandler(FileSystemEventHandler):
        def __init__(self, monitor):
            self.monitor = monitor

        def on_modified(self, event):
            if event.src_path == self.monitor.auth_log_path:
                self.monitor.monitor_authentication()

    def monitor_authentication(self):
        last_line = self.read_last_line(self.auth_log_path)
        if last_line:
            self.parse_log_line(last_line)

    def read_last_line(self, file_path):
        with open(file_path, 'r') as file:
            return file.readlines()[-1]

    def parse_log_line(self, line):
        regex = re.compile(r"(\w+\s+\d+\s+\d+:\d+:\d+) (\w+) (\w+)\[\d+\]: (.+)")
        match = regex.match(line)
        if match:
            date_time, host, process, message = match.groups()
            if "fatal:" in message or "Invalid user" in message or "authentication failure" in message:
                self.failed_login_attempts[host] += 1
            self.log_alert(f"DateTime: {date_time}, Host: {host}, Process: {process}, Message: {message}")

    def check_failed_attempts(self):
        for host, count in self.failed_login_attempts.items():
            if count >= 5:
                self.log_alert(f"Too many failed login attempts from host: {host}. Taking action.")
                self.failed_login_attempts[host] = 0

    def log_alert(self, message):
        self.log(message, "WARNING")
