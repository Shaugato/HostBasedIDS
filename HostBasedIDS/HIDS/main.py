import threading
import time
from queue import Queue
from modules.application_log_monitor import ApplicationLogMonitor
from modules.authentication_log import AuthenticationLogMonitor
from modules.logging_module import LoggingModule
from modules.monitor_process_and_commands import MonitorProcessAndCommands
from modules.system_log_monitor_module import SystemLogMonitorModule

def main():
    logger_queue = Queue()
    logging_module = LoggingModule(logger_queue)

    app_log_monitor = ApplicationLogMonitor(logger_queue, "/var/log/ApplicationLogMonitor.log")
    auth_log_monitor = AuthenticationLogMonitor(logger_queue)
    proc_cmd_monitor = MonitorProcessAndCommands(logger_queue)
    sys_log_monitor = SystemLogMonitorModule(logger_queue)

    modules = [
        app_log_monitor,
        auth_log_monitor,
        proc_cmd_monitor,
        sys_log_monitor
    ]

    for module in modules:
        module_thread = threading.Thread(target=module.run)
        module_thread.daemon = True
        module_thread.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
