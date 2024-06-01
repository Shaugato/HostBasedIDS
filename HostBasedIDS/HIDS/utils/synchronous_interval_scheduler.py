import threading
import time

class SynchronousIntervalScheduler:
    def __init__(self, task, interval=60):
        self.task = task
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run)

    def run(self):
        while not self.stop_event.is_set():
            self.task()
            self.stop_event.wait(self.interval)

    def run_forever(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

