from abc import ABC, abstractmethod


class Reporter(ABC):
    @abstractmethod
    def logn(self, message: str):
        pass

    @abstractmethod
    def log(self, message: str):
        pass


class ConsoleReporter(Reporter):
    def logn(self, message: str):
        print(message, end='')

    def log(self, message: str):
        print(message)
