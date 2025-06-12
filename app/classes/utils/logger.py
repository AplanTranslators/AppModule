from typing import List, Literal
from app.classes.utils.singleton import SingletonMeta


LOG_COLOR = Literal[
    "purple",
    "cyan",
    "orange",
    "darkcyan",
    "blue",
    "green",
    "yellow",
    "red",
    "bold",
    "underline",
    "end",
]

LOG_COLOR_END = "\033[0m"

LOG_COLOR_DICT = {
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "orange": "\033[38;5;208m",
    "darkcyan": "\033[36m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "end": LOG_COLOR_END,
}


class MessagePart:
    text = ""
    color = None

    def __init__(self, text: str, color: LOG_COLOR):
        self.text = text
        self.color = LOG_COLOR_DICT.get(color, LOG_COLOR_END)

    def __str__(self) -> str:
        return print(self.color + self.text + LOG_COLOR_END)


class Message:
    _parts: List[MessagePart] = []

    def __init__(self, parts: List[MessagePart]):
        self._parts = parts

    def __str__(self) -> str:
        result = ""
        for part in self._parts:
            result += part.color + part.text + LOG_COLOR_END


class Logger(metaclass=SingletonMeta):
    active = False

    def __init__(self):
        pass

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def isActivate(self):
        if self.active:
            return True

    def log(self, message: Message):
        print(message)


# def log(self,msg,)
