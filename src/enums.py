from enum import IntEnum


class Command(IntEnum):
    START = 0
    STOP = 1
    NEXT_LEFT = 2
    NEXT_RIGHT = 3
    NEXT_STRAIGHT = 4
    SPEED_SLOW = 5
    SPEED_FAST = 6
    SPEED_FASTER = 7
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
    EXIT = 100

    def __str__(self):
        return "{0}".format(self.name)


class Speed(IntEnum):
    ZERO = 0
    ONE = 15
    TWO = 30
    THREE = 45
    FOUR = 60
    FIVE = 75
    MAX = FIVE
    MIN = ONE

    def __str__(self):
        return "{0}".format(self.name)

    def __init__(self):
        self.max = Speed.MAX
        self.min = Speed.MIN


