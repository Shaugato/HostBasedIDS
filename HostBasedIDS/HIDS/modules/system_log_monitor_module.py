import os
import re
from .abstract_module import AbstractModule

class SystemLogMonitorModule(AbstractModule):
    def __init__(self, logger: Queue):
        super().__init__(logger)
        self.log("Syslog monitoring module loaded", "INFO")

    def run(self):
        while True:
            self.check_logs()

    def check_logs(self):
        syslog_entries = self.read_log_entries('/var/log/syslog')
        kernlog_entries = self.read_log_entries('/var/log/kern.log')

        for entry in syslog_entries + kernlog_entries:
            self.analyze_log_entry(entry)

    def read_log_entries(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r') as file:
            return file.readlines()

    def analyze_log_entry(self, entry):
        if "error" in entry.lower() or "fail" in entry.lower() or "warn" in entry.lower():
            self.log(entry.strip(), "WARNING")
        elif "kernel panic" in entry.lower() or "out of memory" in entry.lower():
            self.log(entry.strip(), "ERROR")
        else:
            self.log(entry.strip(), "INFO")
