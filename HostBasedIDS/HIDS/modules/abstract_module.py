from concurrent.futures import ThreadPoolExecutor
import logging
from queue import Queue
from threading import Event

class AbstractModule:
    def __init__(self, logger: Queue):
        self.logger = logger
        self.stop_event = Event()
        self.executor = ThreadPoolExecutor(max_workers=1)

    def run(self):
        self.executor.submit(self._run)

    def _run(self):
        raise NotImplementedError("Subclasses must implement this method")

    def log(self, message: str, level: int):
        log_entry = {'message': message, 'level': level}
        self.logger.put(log_entry)

    def stop(self):
        self.stop_event.set()
        self.executor.shutdown(wait=True)
