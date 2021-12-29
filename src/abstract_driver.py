from enums import Command


class AbstractDriver:
    def execute(self, command: Command):
        pass
