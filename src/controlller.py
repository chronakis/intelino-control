from threading import Thread
from drivable import Drivable
from enums import Command


class Controller(Thread):
    def __init__(self, driver: Drivable = None):
        self._stopit: bool = False
        self.driver: Drivable = driver
        Thread.__init__(self)

    def set_train_driver(self, driver: Drivable):
        self.driver = driver

    def stop(self):
        self._stopit = True

    def is_stopped(self) -> bool:
        return self._stopit

    def run(self):
        """main loop goes here.
        When the loop interprets an intent/command it calls the drivers execute method
        """
        pass
