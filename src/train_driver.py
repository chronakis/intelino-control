import time
from threading import Thread
from typing import Union

from intelino.trainlib_async.enums import SteeringDecision
from intelino.trainlib import TrainScanner, Train
from intelino.trainlib.enums import (
    MovementDirection,
    SnapColorValue as C,
    SpeedLevel,
)
from intelino.trainlib.messages import (
    TrainMsgEventSensorColorChanged,
    TrainMsgEventMovementDirectionChanged,
    TrainMsgEventSplitDecision
)
from reporter import Reporter, ConsoleReporter
from enums import Command, SpeedFine


class TrainDriver:
    """The train driving class that has state and high level methods"""

    def __init__(self, reporter: Reporter = ConsoleReporter()):
        self._driver_thread: Thread = None
        self._driving: bool = None
        self.train: Train = None
        self._reporters: list(Reporter) = list()
        self._reporters.append(reporter)

        # Below is the state of the train
        self._snap_following: bool = False
        self._speed_level: SpeedLevel = SpeedLevel.STOP
        self._steering: SteeringDecision = SteeringDecision.STRAIGHT
        self._direction: MovementDirection = MovementDirection.FORWARD

        # For overriding
        # self._next_snap_following_: bool
        # self._next_snap_following_count: int
        self._next_steering: SteeringDecision = None
        self._next_steering_count: int = 0

    def connect(self, callback):
        if self._driver_thread is not None:
            if self._driver_thread.is_alive():
                raise Exception("The driver is already driving")
            else:
                del self._driver_thread

        self._driver_thread = Thread(target=self._do_drive, args=(callback,))
        self._driver_thread.start()

    def disconnect(self):
        self._driving = False

    def is_driving(self) -> bool:
        return self._driving

    def log(self, msg):
        for r in self._reporters:
            r.log(msg)

    def logn(self, msg):
        for r in self._reporters:
            r.logn(msg)

    def add_reporter(self, reporter: Reporter):
        self._reporters.append(reporter)

    def _do_drive(self, callback):
        try:
            with TrainScanner() as self.train:
                callback(True, self.train.name)
                self._init_train()
                self._driving = True
                while self._driving:
                    time.sleep(0.01)
                self._driving = False
                self._cleanup_train()
        except Exception as error:
            callback(False, str(error))

    def _init_train(self):
        self.train.stop_driving()
        self.train.set_snap_command_execution(self._snap_following)
        self.train.add_split_decision_listener(self.split_decision_callback)

    def _cleanup_train(self):
        self.train.stop_driving()
        self.train.set_snap_command_execution(True)
        self.train.remove_split_decision_listener(self.split_decision_callback)

    def execute(self, command: Command, arg: Union[int, str] = None):
        if command == Command.CONNECT:
            self.connect()
        elif command == Command.DISCONNECT:
            self.disconnect()
        elif command == Command.START:
            self.start()
        elif command == Command.STOP:
            self.stop()
        elif command == Command.KEEP_LEFT:
            self.set_state_steering(SteeringDecision.LEFT)
        elif command == Command.KEEP_RIGHT:
            self.set_state_steering(SteeringDecision.RIGHT)
        elif command == Command.KEEP_STRAIGHT:
            self.set_state_steering(SteeringDecision.STRAIGHT)
        elif command == Command.NEXT_LEFT:
            self.next_steering(SteeringDecision.LEFT, arg)
        elif command == Command.NEXT_RIGHT:
            self.next_steering(SteeringDecision.RIGHT, arg)
        elif command == Command.NEXT_STRAIGHT:
            self.next_steering(SteeringDecision.STRAIGHT, arg)
        elif command == Command.SNAPS_FOLLOW:
            self.next_steering(SteeringDecision.STRAIGHT)
        elif command == Command.SNAPS_IGNORE:
            self.next_steering(SteeringDecision.STRAIGHT)
        elif command == Command.SPEED_FAST:
            self.set_speed_level(SpeedLevel.LEVEL3)
        elif command == Command.SPEED_MEDIUM:
            self.set_speed_level(SpeedLevel.LEVEL2)
        elif command == Command.SPEED_SLOW:
            self.set_speed_level(SpeedLevel.LEVEL1)

    def start(self):
        self.logn("Starting")
        self._speed_level = SpeedLevel.LEVEL2
        self.train.drive_at_speed_level(self._speed_level, self._direction, True)

    def stop(self):
        self.log("Stopping")
        self._speed_level = SpeedLevel.STOP
        self.train.drive_at_speed_level(self._speed_level, self._direction, True)

    def set_state_steering(self, steering: SteeringDecision):
        self.log(f"Set base steering {steering.name}")
        self._steering = steering
        self.train.set_next_split_steering_decision(self._steering)

    def set_snap_following(self, follow: bool):
        self.log(f"Setting snap following to {follow}")
        self._snap_following = follow
        self.train.set_snap_command_execution(follow)

    def next_steering(self, steering: SteeringDecision, count: int = 1):
        if count is None:
            count = 1
        self.log(f"Next steering: {steering.name}, count: {count}")
        self._next_steering_count = count - 1
        self._next_steering = steering
        self.train.set_next_split_steering_decision(steering)

    def set_speed_level(self, speed_level: SpeedLevel):
        self.log(f"Setting speed to {speed_level.name}")
        self.train.drive_at_speed_level(speed_level, self._driving, True)

    def set_speed_fine(self, speed_fine: SpeedFine):
        self.log(f"Setting speed to {speed_fine.name}")
        self.train.drive_at_speed(speed_fine, self._direction, True)

    def split_decision_callback(self, train: Train, msg: TrainMsgEventSplitDecision):
        if self._next_steering_count > 0:
            steering = self._next_steering
            self._next_steering_count -= 1
        else:
            steering = self._steering
        self.log("Split decision callback.")
        self.log(f"  Last            : {msg.decision.name}")
        self.log(f"  Train's next    : {self.train.next_split_decision.name}")
        self.log(f"  Driver's default: {self._steering.name}")
        self.log(f"  Actual          : {steering.name}")
        self.log(f"  Is overridden   : {self._next_steering_count > 0}")
        if self._next_steering_count > 0:
            self.log(f"  Overrides left  : {self._next_steering_count}")
        self.train.set_next_split_steering_decision(steering)
