from controlller import Controller
from enums import Command


class KeyController(Controller):
    def __init__(self):
        self._running = True

    def stop_control(self):
        self._running = False

    def control(self):
        self.driver.log("Starting Keyboard Controller")
        self._connect()
        while self._running:
            try:
                str_cmd = input("Next command (start, stop, quit):").lower()
                if str_cmd == "quit":
                    raise EOFError
                elif str_cmd == "connect":
                    self._connect()
                elif str_cmd == "disconnect":
                    self.driver.disconnect()
                elif str_cmd == "start":
                    self.driver.execute(Command.START)
                elif str_cmd == "stop":
                    self.driver.execute(Command.STOP)
                elif str_cmd == "keep_straight":
                    self.driver.execute(Command.KEEP_STRAIGHT)
                elif str_cmd == "keep_left":
                    self.driver.execute(Command.KEEP_LEFT)
                elif str_cmd == "keep_right":
                    self.driver.execute(Command.KEEP_RIGHT)
                elif str_cmd == "next_straight":
                    self.driver.execute(Command.NEXT_STRAIGHT)
                elif str_cmd == "next_left":
                    self.driver.execute(Command.NEXT_LEFT)
                elif str_cmd == "next_right":
                    self.driver.execute(Command.NEXT_RIGHT)
                elif str_cmd == "speed_slow":
                    self.driver.execute(Command.SPEED_SLOW)
                elif str_cmd == "speed_medium":
                    self.driver.execute(Command.SPEED_MEDIUM)
                elif str_cmd == "speed_fast":
                    self.driver.execute(Command.SPEED_FAST)
            except EOFError:
                print("Quiting key controller")
                self._running = False

        print("Stop received. Exiting keyboard controller thread")
        self.driver.disconnect()

    def _connect(self):
        self.driver.connect(self._connect_callback)

    def _connect_callback(self, connected: bool, message: str = ""):
        self.driver.log(f"Connected: {connected}, Message: {message}")
        self._connected = connected
