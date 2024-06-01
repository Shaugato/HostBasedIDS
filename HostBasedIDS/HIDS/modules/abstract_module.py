from abc import ABC, abstractmethod
from queue import Queue
from typing import Type
from logging import Logger

class AbstractModule(ABC):
    def __init__(self, logger: Queue):
        self.logger = logger

    @abstractmethod
    def run(self):
        pass

    def log(self, message: str, level: str = "INFO"):
        self.logger.put({"message": message, "level": level, "source": self.__class__.__name__})

