import time
from threading import Thread
from typing import Union

from intelino.trainlib_async.enums import SteeringDecision
from intelino.trainlib import TrainScanner, Train
from intelino.trainlib.enums import (
    MovementDirection,
    SnapColorValue as C,
    SpeedLevel,
    ColorSensor
)
from intelino.trainlib.messages import (
    TrainMsgEventSensorColorChanged,
    TrainMsgEventMovementDirectionChanged,
    TrainMsgEventSplitDecision
)
from reporter import Reporter, ConsoleReporter
from enums import Command, Speed


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
        self._speed_level: Speed = Speed.ZERO
        self._steering: SteeringDecision = SteeringDecision.STRAIGHT
        self._direction: MovementDirection = MovementDirection.FORWARD
        self._color_sequence: list(C) = list()
        self._ignore_default_junction_seq: bool = True

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
        self.train.add_front_color_change_listener(self.handle_color_change)
        self.train.add_back_color_change_listener(self.handle_color_change)

    def _cleanup_train(self):
        self.train.stop_driving()
        self.train.set_snap_command_execution(True)
        self.train.remove_split_decision_listener(self.split_decision_callback)
        self.train.remove_front_color_change_listener(self.handle_color_change)
        self.train.remove_back_color_change_listener(self.handle_color_change)

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
            self.set_speed(Speed.FOUR)
        elif command == Command.SPEED_MEDIUM:
            self.set_speed(Speed.THREE)
        elif command == Command.SPEED_SLOW:
            self.set_speed(Speed.TWO)
        elif command == Command.SPEED_FINE:
            if Speed.MIN.value <= arg <= Speed.MAX.value:
                self.set_speed(Speed(arg))
            else:
                self.log(f"Invalid speed file value {arg}. Must be between {Speed.MIN} and {Speed.MAX}")
        elif command == Command.REVERSE:
            self.reverse()
        elif command == Command.FORWARD:
            self.forward()
        elif command == Command.BACKWARD:
            self.backward()

    def start(self):
        self.logn("Starting")
        self._speed_level = Speed.TWO
        self.train.drive_at_speed(self._speed_level.speed, self._direction, True)

    def stop(self):
        self.log("Stopping")
        self._speed_level = Speed.ZERO
        self.train.drive_at_speed(self._speed_level.speed, self._direction, True)

    def reverse(self):
        self.log("Reversing")
        if self.train.direction == MovementDirection.FORWARD:
            self._direction = MovementDirection.BACKWARD
        else:
            self._direction = MovementDirection.FORWARD
        self.train.drive_at_speed(self._speed_level.speed, self._direction, True)

    def forward(self):
        self.log("Forward")
        self._direction = MovementDirection.FORWARD
        self._speed_level = Speed.TWO
        self.train.drive_at_speed(self._speed_level.speed, self._direction, True)

    def backward(self):
        self.log("Backwards")
        self._direction = MovementDirection.BACKWARD
        self._speed_level = Speed.TWO
        self.train.drive_at_speed(self._speed_level.speed, self._direction, True)

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

    def set_speed(self, speed_level: Speed):
        self.log(f"Setting speed to {speed_level.name}")
        self._speed_level = speed_level
        self.train.drive_at_speed(self._speed_level.speed, self._direction, True)

    def split_decision_callback(self, train: Train, msg: TrainMsgEventSplitDecision):
        if self._next_steering_count > 0:
            steering = self._next_steering
            self._next_steering_count -= 1
        else:
            steering = self._steering
        self.log(f"Split. Last: {msg.decision.name}, Next: {msg.decision.name}, Next: {steering.name} ({self._next_steering_count > 0}), Default: {self.train.next_split_decision.name}")
        self.train.set_next_split_steering_decision(steering)

    def handle_color_change(self, train: Train, msg: TrainMsgEventSensorColorChanged):
        if msg.sensor == ColorSensor.FRONT:
            # self.log(f"Sensor color change {train.distance_cm} -> {msg.sensor.name}: {msg.color}")
            # Sequence detection:
            if msg.color == C.BLACK:
                col_seq = list(self._color_sequence)
                self._color_sequence.clear()
                self.handle_color_command(col_seq, train.distance_cm)
            else:
                self._color_sequence.append(msg.color)

    def handle_color_command(self, seq: list(C), distance: int):
        builtin = False
        if self._ignore_default_junction_seq and len(seq) == 2:
            builtin = builtin or (seq[0] == C.CYAN and (seq[1] == C.RED or seq[1] == C.BLUE))
            builtin = builtin or (seq[1] == C.CYAN and (seq[0] == C.RED or seq[0] == C.BLUE))

        if not builtin:
            self.log(f"Color command at {distance}: {seq}")
