import psutil
import logging
from queue import Queue
from .abstract_module import AbstractModule

class MonitorProcessAndCommands(AbstractModule):
    FORBIDDEN_COMMANDS = ["nmap", "ssh"]
    WHITELISTED_COMMANDS = ["docker", "apache2", "nginx", "haproxy", "sudo"]
    MEMORY_THRESHOLD = 500 * 1024 * 1024  # 500 MB

    def __init__(self, logger: Queue):
        super().__init__(logger)
        self.logger = logger
        self.log("Monitor Process and Commands module started", logging.INFO)

    def _run(self):
        self.log("Monitoring processes and commands", logging.INFO)
        while not self.stop_event.is_set():
            try:
                self.monitor_processes()
                self.stop_event.wait(5)  # Check every 5 seconds
            except Exception as e:
                self.log(f"Error monitoring processes: {e}", logging.ERROR)

    def monitor_processes(self):
        for process in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if process.info['name'] in self.FORBIDDEN_COMMANDS:
                    self.log(f"Terminating forbidden process: {process.info['name']} (PID: {process.info['pid']})", logging.WARNING)
                    process.terminate()
                elif process.info['name'] in self.WHITELISTED_COMMANDS and process.info['memory_info'].rss > self.MEMORY_THRESHOLD:
                    self.log(f"Terminating process exceeding memory threshold: {process.info['name']} (PID: {process.info['pid']})", logging.WARNING)
                    process.terminate()
            except psutil.NoSuchProcess:
                continue
            except Exception as e:
                self.log(f"Error processing process {process.info['name']} (PID: {process.info['pid']}): {e}", logging.ERROR)
