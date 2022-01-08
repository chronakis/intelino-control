from controlller import Controller
from reporter import Reporter
from enums import CommandId
import tkinter as tk
import queue as q
from queue import Queue

from src.util import Command, CommandFormatException, Program, ColorSequence


class GuiKeyController(Controller, Reporter):
    _QUIT_SEQUENCE = "jfjehorupowqif[psdjlhweoieuro3ifjnlc"

    def __init__(self):
        print("Starting GUI Keyboard Controller Thread")
        self.root = tk.Tk()
        self.root.title("GUI Train Controller")

        self.label_input = tk.Label(text="Enter commands bellow")
        self.label_input.pack()

        self.text_command = tk.Entry()
        self.text_command.bind("<Return>", (lambda event: self._process_command(event, self.text_command)))
        self.text_command.pack()

        self.label_output = tk.Label(text="Status reports")
        self.label_output.pack()

        self.text_output = tk.Text()
        self.text_output.pack()

        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self._log_queue = Queue()
        self.root.after(100, self._process_log_queue())

        self._connected = False
        super().__init__()

    def log(self, message: str):
        self._log_queue.put(f"{message}\n")

    def logn(self, message: str):
        self._log_queue.put(message)

    def control(self):
        self.driver.execute(Command(CommandId.CONNECT, self.connect_callback, self.disconnect_callback))
        self.root.mainloop()

    def stop_control(self):
        self._log_queue.put(GuiKeyController._QUIT_SEQUENCE)

    def _process_command(self, event: tk.Event, source: tk.Widget):
        text = source.get()
        source.delete(0, tk.END)
        self.log(f"*** Command: {text}")

        cmd: Command = None
        str_cmd: str = text.lower()
        try:
            if str_cmd == "quit":
                self.driver.execute(Command(CommandId.DISCONNECT))
                self._quit()
            elif str_cmd.startswith("program "):
                prog_text = str_cmd.removeprefix("program ")
                parts = prog_text.split(" when ")
                cmd_text = parts[0]
                seq_text = parts[1]
                cmd = self._text_to_command(cmd_text, self)
                seq = ColorSequence().from_string_csv(seq_text)
                prog = Program(seq, cmd)
                self.driver.program_command(prog)
            else:
                cmd = self._text_to_command(str_cmd, self)
                self.driver.execute(cmd)
        except CommandFormatException as e:
            self.log(e)

    @staticmethod
    def _text_to_command(text, callback_target) -> Command:
        """
        Converts a text to a command. It does not work with "program"
        Args:
            text: The text

        Returns: A command including the arguments
        """
        str_cmd = text.lower()
        cmd = None

        if str_cmd == "connect":
            cmd = Command(CommandId.CONNECT, callback_target.connect_callback, callback_target.disconnect_callback)
        elif str_cmd == "disconnect":
            cmd = Command(CommandId.DISCONNECT)
        elif str_cmd == "start":
            cmd = Command(CommandId.START)
        elif str_cmd == "stop":
            cmd = Command(CommandId.STOP)
        elif str_cmd == "keep_straight":
            cmd = Command(CommandId.KEEP_STRAIGHT)
        elif str_cmd == "keep_left":
            cmd = Command(CommandId.KEEP_LEFT)
        elif str_cmd == "keep_right":
            cmd = Command(CommandId.KEEP_RIGHT)
        elif str_cmd == "next_straight":
            cmd = Command(CommandId.NEXT_STRAIGHT)
        elif str_cmd == "next_left":
            cmd = Command(CommandId.NEXT_LEFT)
        elif str_cmd == "next_right":
            cmd = Command(CommandId.NEXT_RIGHT)
        elif str_cmd == "speed_slow":
            cmd = Command(CommandId.SPEED_SLOW)
        elif str_cmd == "speed_medium":
            cmd = Command(CommandId.SPEED_MEDIUM)
        elif str_cmd == "speed_fast":
            cmd = Command(CommandId.SPEED_FAST)
        elif str_cmd.startswith("speed "):
            val_str = str_cmd.removeprefix("speed ")
            if val_str.isnumeric():
                val = int(val_str)
                cmd = Command(CommandId.SPEED_FINE, val)
            else:
                raise CommandFormatException("Malformed command. Usage: speed 1|2|3|4|5")
        elif str_cmd == "reverse":
            cmd = Command(CommandId.REVERSE)
        elif str_cmd == "forward":
            cmd = Command(CommandId.FORWARD)
        elif str_cmd == "backwards":
            cmd = Command(CommandId.BACKWARD)
        else:
            raise CommandFormatException(f"Command not recognised: {str_cmd}")

        return cmd

    def _write_to_output(self, text: str):
        self.text_output.insert(tk.END, f"{text}\n")
        self.text_output.see(tk.END)

    def _log(self, message: str):
        self._logn(f"{message}\n")

    def _logn(self, message: str):
        self.text_output.insert(tk.END, message)
        self.text_output.see(tk.END)

    def _process_log_queue(self):
        try:
            while True:
                msg = self._log_queue.get_nowait()
                if msg == GuiKeyController._QUIT_SEQUENCE:
                    self.root.quit()
                else:
                    self.text_output.insert(tk.END, msg)
                    self.text_output.see(tk.END)
        except q.Empty:
            self.root.after(10, self._process_log_queue)

    def connect_callback(self, connected: bool, train_id_or_msg: str = "", train_name: str = None):
        if connected:
            self.log(f"Connected: {connected}. Train id: {train_id_or_msg}, name: {train_name}")
            self._connected = connected
        else:
            self.log(f"Failed to connect. Message: {train_id_or_msg}")

    def disconnect_callback(self, connected: bool, train_id_or_msg: str = "", train_name: str = None):
        self._connected = False
        self.log(f"Disconnected: {connected}. Train id: {train_id_or_msg}, name: {train_name}")

    def _quit(self):
        if self._connected:
            self.driver.execute(Command(CommandId.DISCONNECT))
        self.root.quit()
