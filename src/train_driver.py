import threading
import time
from threading import Thread, Lock
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
from enums import CommandId, Speed, JunctionMark
from util import ColorCommand, TestData, ColorSequence, Program, Command


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
        self._color_sequence: ColorSequence = ColorSequence()
        self._last_color_command = None

        # For overriding
        # self._next_snap_following_: bool
        # self._next_snap_following_count: int
        self._next_steering: SteeringDecision = None
        self._next_steering_count: int = 0
        self._programs: dict() = dict()

        self._lock = threading.Lock()

        # self._test_list_y: list(TestData) = list()
        # self._test_list_m: list(TestData) = list()

    def connect(self, connect_callback=None, disconnect_callback=None):
        """
        Args:
            connect_callback: callback(success: bool = True, train_id: str, train_name: str)
                              callback(success: bool = False, error_message)
            disconnect_callback:  callback(success: bool, train_id: str, train_name: str)
        Returns:
            Immediately.
        """
        if self._driver_thread is not None:
            if self._driver_thread.is_alive():
                self.log("The train driver seems to be already connected")
                return
            else:
                del self._driver_thread

        self._driver_thread = Thread(target=self._do_drive, args=(connect_callback, disconnect_callback, ))
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

    def _do_drive(self, connect_callback, disconnect_callback):
        if not self._lock.acquire(False):
            raise Exception("Driver awaiting to connect or already connected")

        try:
            with TrainScanner() as self.train:
                train_id = self.train.id
                train_name = self.train.name

                self.log("Train Driver Connected")
                if connect_callback is not None:
                    connect_callback(True, train_id, train_name)

                self._init_train()
                self._driving = True
                while self._driving:
                    time.sleep(0.01)
                self._cleanup_train()

                self.log("Train Driver Disconnected")
                if disconnect_callback is not None:
                    disconnect_callback(True, train_id, train_name)
        except Exception as error:
            connect_callback(False, str(error), None)
        finally:
            self._lock.release()

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
        # Don't call disconnect. It's done at the with/__exit

    def execute(self, command: Command):
        if command.cmd_id == CommandId.CONNECT:
            self.connect(command.args[0], command.args[1])
        elif command.cmd_id == CommandId.DISCONNECT:
            self.disconnect()
        elif command.cmd_id == CommandId.START:
            self.start()
        elif command.cmd_id == CommandId.STOP:
            self.stop()
        elif command.cmd_id == CommandId.KEEP_LEFT:
            self.set_state_steering(SteeringDecision.LEFT)
        elif command.cmd_id == CommandId.KEEP_RIGHT:
            self.set_state_steering(SteeringDecision.RIGHT)
        elif command.cmd_id == CommandId.KEEP_STRAIGHT:
            self.set_state_steering(SteeringDecision.STRAIGHT)
        elif command.cmd_id == CommandId.NEXT_LEFT:
            self.next_steering(SteeringDecision.LEFT, command.args[0])
        elif command.cmd_id == CommandId.NEXT_RIGHT:
            self.next_steering(SteeringDecision.RIGHT, command.args[0])
        elif command.cmd_id == CommandId.NEXT_STRAIGHT:
            self.next_steering(SteeringDecision.STRAIGHT, command.args[0])
        elif command.cmd_id == CommandId.SNAPS_FOLLOW:
            self.next_steering(SteeringDecision.STRAIGHT)
        elif command.cmd_id == CommandId.SNAPS_IGNORE:
            self.next_steering(SteeringDecision.STRAIGHT)
        elif command.cmd_id == CommandId.SPEED_FAST:
            self.set_speed(Speed.FOUR)
        elif command.cmd_id == CommandId.SPEED_MEDIUM:
            self.set_speed(Speed.THREE)
        elif command.cmd_id == CommandId.SPEED_SLOW:
            self.set_speed(Speed.TWO)
        elif command.cmd_id == CommandId.SPEED_FINE:
            if Speed.MIN.value <= command.args[0] <= Speed.MAX.value:
                self.set_speed(Speed(command.args[0]))
            else:
                self.log(f"Invalid speed file value {command.args[0]}. Must be between {Speed.MIN} and {Speed.MAX}")
        elif command.cmd_id == CommandId.REVERSE:
            self.reverse()
        elif command.cmd_id == CommandId.FORWARD:
            self.forward()
        elif command.cmd_id == CommandId.BACKWARD:
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
                seq = ColorSequence(self._color_sequence)
                self._color_sequence.clear()
                # Determine if it is a junction mark or a command sequence
                junction_mark = False
                if len(seq) == 2 and seq[0] == C.CYAN and seq[1] == C.RED:
                    self.handle_junction_mark(JunctionMark.LEFT, train.distance_cm)
                elif len(seq) == 2 and seq[0] == C.CYAN and seq[1] == C.BLUE:
                    self.handle_junction_mark(JunctionMark.RIGHT, train.distance_cm)
                elif len(seq) == 2 and seq[1] == C.CYAN and seq[0] == C.RED:
                    self.handle_merge_mark(JunctionMark.RIGHT, train.distance_cm)
                elif len(seq) == 2 and seq[1] == C.CYAN and seq[0] == C.BLUE:
                    self.handle_merge_mark(JunctionMark.LEFT, train.distance_cm)
                else:
                    self.handle_color_command(seq, train.distance_cm)
            else:
                self._color_sequence.append(msg.color)

    def handle_color_command(self, seq: ColorSequence, distance: int):
        """
        Handles a color sequence followed by a "black".
        This is fired up for every sequence, except of the junction marks.
        Look at the handle_junction_mark instead

        Args:
            seq: The color sequence or otherwise command id
            distance: The distance in cm that this was found

        Returns: Nothing

        """
        command = ColorCommand(seq, distance, time.perf_counter())
        # self._last_color_command = command
        self.log(f"Color command: {command}")
        program = self._programs.get(command.seq.identity())
        if program is not None:
            self.log(f"Executing program: {program}")
            self.execute(program.command)
        else:
            self.log("No program found")

    def handle_junction_mark(self, towards: JunctionMark, distance: int):
        """
        Fired up when a junction mark is found.
        See merge marks when crossinga junction after a merge

        Args:
            towards: Left or right junction
            distance: The travel distance of the train

        Returns: Nothing

        """
        self.log(f"Junction Mark: {towards.name} at {distance}")

        # The roundtrip from the color sensor to this code and back to the train
        # is very slow for this to work, so no point really.
        if self._last_color_command is not None:
            velocity = self.train.speed_cmps
            delta_time = time.perf_counter() - self._last_color_command.timestamp
            delta_dist = velocity * delta_time

            # self.log(f"Test: {self._last_color_command.seq} -- Gap: {dd}")
            # if self._last_color_command.seq[0] == C.YELLOW:
            #     self._test_list_y.append(TestData(s, t, d, dd))
            # elif self._last_color_command.seq[0] == C.MAGENTA:
            #     self._test_list_m.append(TestData(s, t, d, dd))
            if delta_dist < 9.0:
                junction_id = self._last_color_command.seq
                self.handle_junction_id(junction_id, self.train.distance_cm)

    def handle_merge_mark(self, coming: JunctionMark, distance: int):
        """
        Fired up when merging after a junction

        Args:
            coming : Left or right junction
            distance: The travel distance of the train

        Returns: Nothing

        """
        self.log(f"Merging Mark: {coming.name} at {distance}")

    def handle_junction_id(self, junction_id: list(C), distance: int):
        """
        The loop from the train and back is way too slow for this trick to work
        """
        self.log(f"Junction ID {junction_id} @ {distance}")

    def program_command(self, program: Program):
        self._programs[program.seq.identity()] = program
        self.log(f"Program added: {program}")
