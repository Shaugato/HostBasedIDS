# logger.py
import logging

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('HIDSLogger')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def log(self, message):
        self.logger.info(message)

