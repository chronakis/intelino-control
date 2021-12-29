from typing import Union
from abc import ABC, abstractmethod
from enums import Command


class Drivable(ABC):
    @abstractmethod
    def execute(self, command: Command, arg: Union[int, str] = None):
        pass
