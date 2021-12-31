from controlller import Controller
from reporter import Reporter
from enums import Command
import tkinter as tk
import queue as q
from queue import Queue


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
        self._connect()
        self.root.mainloop()

    def stop_control(self):
        self._log_queue.put(GuiKeyController._QUIT_SEQUENCE)

    def _process_command(self, event: tk.Event, source: tk.Widget):
        text = source.get()
        source.delete(0, tk.END)
        self.log(f"*** Command: {text}")

        str_cmd = text.lower()
        if str_cmd == "quit":
            self._disconnect()
            self._quit()
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
        else:
            self.log("    -> Not recognised")

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

    def _connect(self):
        self.driver.connect(self._connect_callback)

    def _connect_callback(self, connected: bool, message: str = ""):
        self.log(f"Connected: {connected}, Message: {message}")
        self._connected = connected

    def _disconnect(self):
        self._connected = False
        self.driver.disconnect()

    def _quit(self):
        if self._connected:
            self._disconnect()
        self.root.quit()
