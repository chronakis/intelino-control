from typing import Union
from abc import ABC, abstractmethod
from enums import CommandId


class Drivable(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def execute(self, command: CommandId, arg: Union[int, str] = None):
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass