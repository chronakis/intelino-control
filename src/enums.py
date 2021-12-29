from enum import IntEnum, IntFlag


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
    EXIT = 100

    def __str__(self):
        return "{0}".format(self.name)
