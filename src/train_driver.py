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
from abstract_driver import AbstractDriver
from enums import Command


class TrainDriver(AbstractDriver):
    """The train driving class that has state and high level methods"""
    def __init__(self):
        self.train: Train = None
        self._controllers: list(Controller) = list()

        # Below is the state of the train
        self._speed: SpeedLevel = SpeedLevel.STOP
        self._steering: SteeringDecision = SteeringDecision.STRAIGHT
        self._direction: MovementDirection = MovementDirection.FORWARD

    def add_controller(self, controller: Controller):
        controller.set_train_driver(self)
        self._controllers.append(controller)

    def drive(self):
        with TrainScanner() as train:
            self.train = train
            self.train.set_snap_command_execution(False)
            self.train.add_split_decision_listener(self.split_decision_callback)

            for c in self._controllers:
                c.start()

            # Now just wait for them to terminate
            for c in self._controllers:
                c.join()

            self.cleanup()

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

    def execute(self, command: Command):
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
            self.next_steering(SteeringDecision.LEFT)
        elif command == Command.NEXT_RIGHT:
            self.next_steering(SteeringDecision.RIGHT)
        elif command == Command.NEXT_STRAIGHT:
            self.next_steering(SteeringDecision.STRAIGHT)

    def start(self):
        print("Starting")
        self._speed = SpeedLevel.LEVEL2
        self.train.drive_at_speed_level(self._speed, self._direction, True)

    def stop(self):
        print("Stopping")
        self._speed = SpeedLevel.STOP
        self.train.drive_at_speed_level(self._speed, self._direction, True)

    def next_steering(self, steering: SteeringDecision):
        print(f"Next steering {steering.name}")
        self.train.set_next_split_steering_decision(steering)

    def set_state_steering(self, steering: SteeringDecision):
        print(f"Set base steering {steering.name}")
        self._steering = steering
        self.train.set_next_split_steering_decision(self._steering)

    def split_decision_callback(self, train: Train, msg: TrainMsgEventSplitDecision):
        print(f"Split decision callback. Last: { msg.decision.name}, Next: {self.train.next_split_decision.name}")
        self.train.set_next_split_steering_decision(self._steering)
