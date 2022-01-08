from typing import Union
from intelino.trainlib.enums import SnapColorValue
from intelino.trainlib.enums import SnapColorValue as C
from enums import CommandId


class ColorSequence(list):
    def __init__(self, seq: list = ()):
        super().__init__(seq)

    def identity(self) -> str:
        return str.join('-', map(lambda c: c.name, self))

    color_map = {
            "red": SnapColorValue.RED,
            "yellow": SnapColorValue.YELLOW,
            "blue": SnapColorValue.BLUE,
            "black": SnapColorValue.BLACK,
            "magenta": SnapColorValue.MAGENTA,
            "cyan": SnapColorValue.CYAN,
            "green": SnapColorValue.GREEN,
            "white": SnapColorValue.WHITE
        }

    def from_string_csv(self, csv: str):
        parts = csv.split(',')
        return self.from_strings(map(lambda i: i.strip().lower(), parts))

    def from_strings(self, strings: list()):
        for s in strings:
            s2 = self.color_map[s]
            if s2 is None:
                raise Exception(f"There is no such color in the map {s}")
            self.append(s2)
        return self

    def __str__(self):
        return self.identity()


class Command:
    def __init__(self, cmd_id: CommandId, *args):
        self.cmd_id = cmd_id
        self.args = args

    def __str__(self):
        args_str = str.join(', ', map(lambda a: str(a), self.args))
        return f"{self.cmd_id}({args_str})"


class Program:
    def __init__(self, seq: ColorSequence, command: Command):
        self.seq = seq
        self.command = command

    def __str__(self):
        return f"{self.seq} -> {self.command}"


class ColorCommand:
    def __init__(self, seq: ColorSequence, distance: int, timestamp: float):
        self.seq: ColorSequence = ColorSequence(seq)
        self.distance: int = distance
        self.timestamp: float = timestamp

    def __str__(self):
        return f"{self.seq} at {self.distance} cm / {self.timestamp} sec"


class TestData:
    def __init__(self, s: float, t: float, d: int, dd: float):
        self.d = d
        self.t = t
        self.s = s
        self.dd = dd

    def __str__(self):
        return f"{self.s}, {self.t}, {self.d}, {self.dd}"


class CommandFormatException(Exception):
    pass
