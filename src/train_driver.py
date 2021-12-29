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
from controlller import Controller
from drivable import Drivable
from enums import Command


class TrainDriver(Drivable):
    """The train driving class that has state and high level methods"""
    def __init__(self):
        self.train: Train = None
        self._controllers: list(Controller) = list()

        # Below is the state of the train
        self._snap_following: bool = False
        self._speed_level: SpeedLevel = SpeedLevel.STOP
        self._steering: SteeringDecision = SteeringDecision.STRAIGHT
        self._direction: MovementDirection = MovementDirection.FORWARD

        # For overriding
        #self._next_snap_following_: bool
        #self._next_snap_following_count: int
        self._next_steering: SteeringDecision = None
        self._next_steering_count: int = 0

    def add_controller(self, controller: Controller):
        controller.set_train_driver(self)
        self._controllers.append(controller)

    def drive(self):
        with TrainScanner() as self.train:

            for c in self._controllers:
                c.start()

            # Now just wait for them to terminate
            for c in self._controllers:
                c.join()

            self.cleanup()

    def init_train_behaviour(self):
        self.train.stop_driving()
        self.train.set_snap_command_execution(self._snap_following)
        self.train.add_split_decision_listener(self.split_decision_callback)

    def cleanup(self):
        self.train.set_snap_command_execution(True)
        self.train.remove_split_decision_listener(self.split_decision_callback)
        for c in self._controllers:
            t = Controller()

    def quit(self):
        # Stop all controllers
        # Disconnect and clean up
        print("Quiting. Waiting for controllers to stop")
        for c in self._controllers:
            c.stop()

    def execute(self, command: Command, arg: Union[int, str] = None):
        if command == Command.EXIT:
            self.quit()
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

    def start(self):
        print("Starting")
        self._speed_level = SpeedLevel.LEVEL2
        self.train.drive_at_speed_level(self._speed_level, self._direction, True)

    def stop(self):
        print("Stopping")
        self._speed_level = SpeedLevel.STOP
        self.train.drive_at_speed_level(self._speed_level, self._direction, True)

    def set_state_steering(self, steering: SteeringDecision):
        print(f"Set base steering {steering.name}")
        self._steering = steering
        self.train.set_next_split_steering_decision(self._steering)

    def set_snap_following(self, follow: bool):
        print(f"Setting snap following to {bool}")
        self._snap_following = follow
        self.train.set_snap_command_execution(follow)

    def next_steering(self, steering: SteeringDecision, count: int = 1):
        if count is None:
            count = 1
        print(f"Next steering: {steering.name}, count: {count}")
        self._next_steering_count = count - 1
        self._next_steering = steering
        self.train.set_next_split_steering_decision(steering)

    def set_speed(self, speed_level: SpeedLevel):
        self.train.drive_at_speed()

    def split_decision_callback(self, train: Train, msg: TrainMsgEventSplitDecision):
        if self._next_steering_count > 0:
            steering = self._next_steering
            self._next_steering_count -= 1
        else:
            steering = self._steering
        print("Split decision callback.")
        print("  Last            : ", msg.decision.name)
        print("  Train's next    : ", self.train.next_split_decision.name)
        print("  Driver's default: ", self._steering)
        print("  Actual          : ", steering)
        print("  Is overridden   : ", self._next_steering_count > 0)
        if self._next_steering_count > 0:
            print("  Overrides left  : ", self._next_steering_count)
        self.train.set_next_split_steering_decision(steering)
