from train_driver import TrainDriver
from abc import ABC, abstractmethod


class Controller(ABC):
    def __init__(self, driver: TrainDriver = None):
        self.driver: TrainDriver = driver
        self._connected: bool = False

    def set_train_driver(self, driver: TrainDriver):
        self.driver = driver

    @abstractmethod
    def control(self):
        pass

    @abstractmethod
    def stop_control(self):
        pass
