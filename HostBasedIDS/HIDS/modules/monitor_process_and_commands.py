import os
import psutil
from .abstract_module import AbstractModule

class MonitorProcessAndCommands(AbstractModule):
    forbidden = ["nmap", "nmap -iL", "nmap -iR", "ssh", "ssh -g", "ssh -n", "ssh -p"]
    whitelist = ["docker", "apache2", "nginx", "haproxy", "sudo"]
    threshold_memory = 500 * 1024 * 1024

    def __init__(self, logger: Queue):
        super().__init__(logger)
        self.log("Monitoring has been started", "INFO")

    def run(self):
        while True:
            self.check_processes()

    def check_processes(self):
        for process in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                name = process.info['name']
                pid = process.info['pid']
                memory = process.info['memory_info'].rss

                if name in self.forbidden:
                    self.log(f"Unusual behaviour has been identified. Name: {name}, ID: {pid}", "WARNING")
                    process.terminate()

                if name in self.whitelist and memory > self.threshold_memory:
                    self.log(f"Excessive memory consumption has been identified. Name: {name}, ID: {pid}", "WARNING")
                    process.terminate()

            except Exception as e:
                self.log(f"Error: {str(e)}", "ERROR")
