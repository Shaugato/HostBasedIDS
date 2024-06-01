# loader.py
from HIDS.modules.application_log_monitor import ApplicationLogMonitor
from HIDS.modules.authentication_log import AuthenticationLog
from HIDS.modules.logging_module import LoggingModule
from HIDS.modules.monitor_process_and_commands import MonitorProcessAndCommands
from HIDS.modules.system_log_monitor_module import SystemLogMonitorModule

class Loader:
    def __init__(self):
        self.modules = [
            ApplicationLogMonitor(),
            AuthenticationLog(),
            LoggingModule(),
            MonitorProcessAndCommands(),
            SystemLogMonitorModule()
        ]

    def run(self):
        for module in self.modules:
            module.start()

