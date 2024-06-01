import os
import logging
from queue import Queue
from .abstract_module import AbstractModule
from .utils.synchronous_interval_scheduler import SynchronousIntervalScheduler
import re
from datetime import datetime

class SystemLogMonitorModule(AbstractModule):
    def __init__(self, logger: Queue, syslog_path: str = "/var/log/syslog", kernlog_path: str = "/var/log/kern.log"):
        super().__init__(logger)
        self.logger = logger
        self.syslog_path = syslog_path
        self.kernlog_path = kernlog_path
        self.log("Syslog monitoring module loaded", logging.INFO)

    def _run(self):
        self.log("Starting syslog and kernlog monitoring", logging.INFO)
        sched = SynchronousIntervalScheduler(self.check_logs, interval=60)
        sched.run_forever()

    def check_logs(self):
        self.log("Checking system logs", logging.INFO)
        syslog_entries = self.parse_log_file(self.syslog_path)
        kernlog_entries = self.parse_log_file(self.kernlog_path)
        
        for entry in syslog_entries + kernlog_entries:
            self.logger.put(entry)

    def parse_log_file(self, file_path: str):
        if not os.path.exists(file_path):
            self.log(f"Log file {file_path} does not exist", logging.WARNING)
            return []
        
        entries = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if self.is_unusual_activity(line):
                        timestamp = self.extract_timestamp(line)
                        entry = {'timestamp': timestamp, 'level': logging.WARNING, 'message': line.strip()}
                        entries.append(entry)
        except Exception as e:
            self.log(f"Failed to read log file {file_path}: {e}", logging.ERROR)
        
        return entries

    def is_unusual_activity(self, log_entry: str):
        """
        Identify unusual activities based on log patterns. This function can be
        expanded to include more sophisticated checks, such as regex patterns
        for known malicious activities or anomalies.
        """
        suspicious_keywords = ["error", "fail", "unauthorized", "denied", "illegal", "invalid", "attack", "compromise"]
        log_entry_lower = log_entry.lower()

        for keyword in suspicious_keywords:
            if keyword in log_entry_lower:
                return True

        # Additional check for known malicious patterns
        if re.search(r'failed \w+ attempt', log_entry_lower) or re.search(r'suspicious \w+ activity', log_entry_lower):
            return True

        return False

    def extract_timestamp(self, log_entry: str):
        """
        Extract the timestamp from the log entry. The format of the log entry is assumed
        to be in a standard syslog format. Adjust the parsing logic based on the actual
        log format.
        """
        try:
            # Example of a syslog timestamp format: "Jan 1 12:00:00"
            match = re.match(r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', log_entry)
            if match:
                timestamp_str = match.group(1)
                current_year = datetime.now().year
                timestamp = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
                return timestamp.isoformat()
            else:
                self.log(f"Failed to extract timestamp from log entry: {log_entry}", logging.WARNING)
                return None
        except Exception as e:
            self.log(f"Error extracting timestamp: {e}", logging.ERROR)
            return None
