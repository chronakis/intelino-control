from enum import IntEnum, Enum


class CommandId(IntEnum):
    START = 0
    STOP = 1
    NEXT_LEFT = 2
    NEXT_RIGHT = 3
    NEXT_STRAIGHT = 4
    SPEED_SLOW = 5
    SPEED_MEDIUM = 6
    SPEED_FAST = 7
    FORWARD = 8
    BACKWARD = 9
    REVERSE = 10
    KEEP_LEFT = 11
    KEEP_RIGHT = 12
    KEEP_STRAIGHT = 13
    SNAPS_IGNORE = 14
    SNAPS_FOLLOW = 15
    NEXT_SNAP_FOLLOW = 16
    NEXT_SNAP_IGNORE = 17
    SPEED_FINE = 18
    DISCONNECT = 98
    CONNECT = 99
    EXIT = 100

    def __str__(self):
        return "{0}".format(self.name)


class Speed(Enum):
    def __new__(cls, value, speed):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, speed):
        self.speed = speed

    ZERO = 0, 0
    ONE = 1, 15
    TWO = 2, 30
    THREE = 3, 45
    FOUR = 4, 60
    FIVE = 5, 75
    MAX = FIVE
    MIN = ONE

# s = SpeedFine.ONE
# print(s, s.value, s.name, s.speed)
#
# s = SpeedFine(2)
# print(s, s.value, s.name, s.speed)


class JunctionMark(Enum):
    LEFT = 0
    RIGHT = 1

    def __str__(self):
        return self.name
