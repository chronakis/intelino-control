from controlller import Controller
from enums import Command


class KeyController(Controller):
    def run(self):
        print("Starting Keyboard Controller Thread")
        while not self.is_stopped():
            str_cmd = input("Next command (start, stop, quit):").lower()
            cmd: Command = None
            if str_cmd == "quit":
                self.driver.execute(Command.EXIT)
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

        print("Stop received. Exiting keyboard controller thread")
