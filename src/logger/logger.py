from datetime import datetime
from pathlib import Path
from typing import Dict, Literal, Optional
import logging
from ..singleton.singleton import SingletonMeta
import colorlog

"""
The following escape codes are made available for use in the format string:

{color}, fg_{color}, bg_{color}: Foreground and background colors.
bold, bold_{color}, fg_bold_{color}, bg_bold_{color}: Bold/bright colors.
thin, thin_{color}, fg_thin_{color}: Thin colors (terminal dependent).
reset: Clear all formatting (both foreground and background colors).
The available color names are:

black
red
green
yellow
blue,
purple
cyan
white
You can also use "bright" colors. These aren't standard ANSI codes, and support for these varies wildly across different terminals.

light_black
light_red
light_green
light_yellow
light_blue
light_purple
light_cyan
light_white

"""


LOG_COLORS = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "purple",
    "cyan",
    "white",
    "reset",
    # ================== LOGHT ====================
    "light_black",
    "light_red",
    "light_green",
    "light_yellow",
    "light_blue",
    "light_purple",
    "light_cyan",
    "light_white",
    # ================== BOLD ====================
    "bold_black",
    "bold_red",
    "bold_green",
    "bold_yellow",
    "bold_blue",
    "bold_purple",
    "bold_cyan",
    "bold_white",
    # ================== THIN ====================
    "thin_black",
    "thin_red",
    "thin_green",
    "thin_yellow",
    "thin_blue",
    "thin_purple",
    "thin_cyan",
    "thin_white",
    # ================== FG ====================
    "fg_black",
    "fg_red",
    "fg_green",
    "fg_yellow",
    "fg_blue",
    "fg_purple",
    "fg_cyan",
    "fg_white",
    # ================== BG ====================
    "bg_black",
    "bg_red",
    "bg_green",
    "bg_yellow",
    "bg_blue",
    "bg_purple",
    "bg_cyan",
    "bg_white",
]


class LogAplanFileHandler(logging.FileHandler):
    """
    A custom handler for logs that writes them to a .act file
    """

    def __init__(self, directory: str, name: str, level: int = logging.NOTSET) -> None:
        log_directory = Path(directory)

        final_path = log_directory / name

        final_path.parent.mkdir(parents=True, exist_ok=True)

        super().__init__(final_path, encoding="utf-8")

        self.setLevel(level)


class LogFileHandler(logging.FileHandler):
    """
    A custom handler for logs that writes them to a file
    with a dynamic name that includes a timestamp.
    """

    def __init__(self, full_path: str, level: int = logging.NOTSET) -> None:
        file_path = Path(full_path)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename_with_timestamp = f"{file_path.stem}_{timestamp}{file_path.suffix}"

        final_path = file_path.parent / filename_with_timestamp

        final_path.parent.mkdir(parents=True, exist_ok=True)

        super().__init__(final_path, encoding="utf-8")

        self.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.setFormatter(formatter)


class LogElementHandler(logging.Handler):
    """A logging handler that emits messages to a log element."""

    def __init__(self, element, level: int = logging.NOTSET) -> None:
        self.element = element
        super().__init__(level)
        formatter = logging.Formatter("%(asctime)s | %(message)s")
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.element.push(msg)
        except Exception:
            self.handleError(record)


class Logger:
    active = False
    _temp_log_color: Optional[str] = None

    def __init__(self, name):
        self.active = True
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()

        self._initial_log_colors = {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }

        class CustomColoredFormatter(colorlog.ColoredFormatter):
            def format(self, record):
                original_level_color = self.log_colors.get(record.levelname)
                original_message_color = self.log_colors.get("message")

                if hasattr(record, "temp_log_color") and record.temp_log_color:
                    temp_color = record.temp_log_color
                    self.log_colors[record.levelname] = temp_color
                    self.log_colors["message"] = temp_color

                result = super().format(record)

                if hasattr(record, "temp_log_color") and record.temp_log_color:
                    if original_level_color:
                        self.log_colors[record.levelname] = original_level_color
                    else:
                        self.log_colors.pop(record.levelname, None)

                    if original_message_color:
                        self.log_colors["message"] = original_message_color
                    else:
                        self.log_colors.pop("message", None)

                return result

        self.formatter = CustomColoredFormatter(
            "%(time_log_color)s%(asctime)s%(reset)s %(light_cyan)s|%(reset)s %(module_log_color)s%(name)s%(reset)s %(light_cyan)s|%(reset)s %(level_log_color)s%(levelname)s%(reset)s %(light_cyan)s|%(reset)s %(log_color)s%(message)s%(reset)s",
            log_colors=self._initial_log_colors,
            secondary_log_colors={
                "level": {
                    "DEBUG": "blue",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                },
                "time": {
                    "DEBUG": "blue",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                },
                "module": {
                    "DEBUG": "light_cyan",
                    "INFO": "light_cyan",
                    "WARNING": "light_cyan",
                    "ERROR": "light_cyan",
                    "CRITICAL": "light_cyan",
                },
            },
            style="%",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def _log_with_temp_color(self, level, msg: str, color: Optional[str] = None):
        extra_kwargs = {}
        if color:
            extra_kwargs["extra"] = {"temp_log_color": color}
        self.logger.log(level, msg, **extra_kwargs)

    def nonset(self, msg: str, color: Optional[LOG_COLORS] = None):
        if self.active:
            self._log_with_temp_color(logging.NOTSET, msg, color)

    def debug(self, msg: str, color: Optional[LOG_COLORS] = None):
        if self.active:
            self._log_with_temp_color(logging.DEBUG, msg, color)

    def info(self, msg: str, color: Optional[LOG_COLORS] = None):
        if self.active:
            self._log_with_temp_color(logging.INFO, msg, color)

    def warning(self, msg: str, color: Optional[LOG_COLORS] = None):
        if self.active:
            self._log_with_temp_color(logging.WARNING, msg, color)

    def error(self, msg: str, color: Optional[LOG_COLORS] = None):
        if self.active:
            self._log_with_temp_color(logging.ERROR, msg, color)

    def critical(self, msg: str, color: Optional[LOG_COLORS] = None):
        if self.active:
            self._log_with_temp_color(logging.CRITICAL, msg, color)

    def delimetr(self, size: int = 100, color: LOG_COLORS = "white", text: str = ""):
        if not self.active:
            return

        delimiter_char = "="
        base_delimiter_string = delimiter_char * size

        if text:
            self.info(base_delimiter_string, color)
            self.info(text, color)
            self.info(base_delimiter_string, color)
        else:
            self.info(base_delimiter_string, color)


class LoggerManager(metaclass=SingletonMeta):
    """
    Керує створенням та налаштуванням усіх логерів в додатку.
    """

    def __init__(self):
        self._loggers: Dict[str, Logger] = {}
        self._is_setup = False

    def getLogger(self, name: str) -> Logger:
        """
        Повертає логер для вказаного імені.
        Якщо логер не існує, він створюється і додається до масиву.
        """

        if name not in self._loggers:
            self._loggers[name] = Logger(name)
            self._loggers[name].activate()

        return self._loggers[name]

    # CRITICAL = 50
    # FATAL = CRITICAL
    # ERROR = 40
    # WARNING = 30
    # WARN = WARNING
    # INFO = 20
    # DEBUG = 10
    # NOTSET = 0
    def setLevelForAll(self, level: int):
        """
        Встановлює рівень логування для всіх логерів.
        """
        for logger_obj in self._loggers.values():
            logger_obj.logger.setLevel(level)

    def setLevelFor(self, name: str, level: int):
        """
        Встановлює рівень логування для конкретного логера.
        """
        if name in self._loggers:
            self._loggers[name].logger.setLevel(level)

    def activate(self, name: str):
        if name in self._loggers:
            self._loggers[name].activate()

    def deactivate(self, name: str):
        if name in self._loggers:
            self._loggers[name].deactivate()
