from typing import List, Literal, Optional
import logging
from app.utils.singleton import SingletonMeta
import colorlog
import sys

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


class Logger(metaclass=SingletonMeta):
    active = False
    _temp_log_color: Optional[str] = None  # Для тимчасового кольору

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()

        # Зберігаємо початкові log_colors
        self._initial_log_colors = {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }

        # Кастомний форматувальник для обробки temp_log_color
        class CustomColoredFormatter(colorlog.ColoredFormatter):
            def format(self, record):
                original_level_color = self.log_colors.get(record.levelname)
                original_message_color = self.log_colors.get("message")

                if hasattr(record, "temp_log_color") and record.temp_log_color:
                    temp_color = record.temp_log_color
                    self.log_colors[record.levelname] = temp_color
                    self.log_colors["message"] = temp_color

                # ТУТ ТАКОЖ ПОТРІБНО ПЕРЕВІРЯТИ І ВІДНОВЛЮВАТИ `secondary_log_colors`
                # Якщо ви використовуєте `secondary_log_colors`, то кольори для `asctime` та `name`
                # також можуть бути змінені, якщо ви їх визначаєте у `secondary_log_colors`.
                # Однак, якщо secondary_log_colors не змінюються динамічно, то цей блок не потрібен.
                # Якщо ж ви все-таки використовуєте `secondary_log_colors`
                # і вони можуть змінюватися, то треба зберігати їх оригінальні значення.

                # Для поточного сценарію, де secondary_log_colors є статичними
                # і ви їх не змінюєте через temp_log_color,
                # цей CustomColoredFormatter достатньо лише для log_colors.

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

    def _log_with_temp_color(self, level, msg: str, color: Optional[str] = None):
        extra_kwargs = {}
        if color:
            extra_kwargs["extra"] = {"temp_log_color": color}
        self.logger.log(level, msg, **extra_kwargs)

    def debug(self, msg: str, color: Optional[LOG_COLORS] = None):
        self._log_with_temp_color(logging.DEBUG, msg, color)

    def info(self, msg: str, color: Optional[LOG_COLORS] = None):
        self._log_with_temp_color(logging.INFO, msg, color)

    def warning(self, msg: str, color: Optional[LOG_COLORS] = None):
        self._log_with_temp_color(logging.WARNING, msg, color)

    def error(self, msg: str, color: Optional[LOG_COLORS] = None):
        self._log_with_temp_color(logging.ERROR, msg, color)

    def critical(self, msg: str, color: Optional[LOG_COLORS] = None):
        self._log_with_temp_color(logging.CRITICAL, msg, color)

    def delimetr(self, size: int = 100, color: LOG_COLORS = "white", text: str = ""):
        delimiter_char = "="
        base_delimiter_string = delimiter_char * size

        if text:
            self.info(base_delimiter_string, color)
            self.info(text, color)
            self.info(base_delimiter_string, color)
        else:
            self.info(base_delimiter_string, color)
