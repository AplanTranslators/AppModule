import logging
import pytest
import sys
import os
from io import StringIO


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logger import Logger, LoggerManager


# --------------------------
# Logger tests
# --------------------------
@pytest.fixture
def logger_instance() -> Logger:
    logger_manager = LoggerManager()
    logger: Logger = logger_manager.getLogger("LoggerTest")
    #logger.activate()  # ensure active before each test
    return logger


@pytest.fixture
def log_capture(logger_instance, monkeypatch):
    """Capture log output from the logger's stream handler."""
    stream = StringIO()
    for handler in logger_instance.logger.handlers:
        logger_instance.logger.removeHandler(handler)

    handler = logging.StreamHandler(stream)
    logger_instance.logger.addHandler(handler)
    logger_instance.logger.setLevel(logging.DEBUG)
    yield stream
    logger_instance.logger.removeHandler(handler)


@pytest.mark.parametrize("method", ["debug", "info", "warning", "error", "critical"])
def test_logger_methods_write_output(logger_instance, log_capture, method):
    """
    Test that logger methods write output to the log.
    """
    getattr(logger_instance, method)("Test message")
    output = log_capture.getvalue()
    assert "Test message" in output


def test_logger_activate_deactivate(logger_instance, log_capture):
    """
    Test that logger can be activated and deactivated.
    """
    logger_instance.deactivate()
    logger_instance.info("Should not appear")
    assert log_capture.getvalue() == ""

    logger_instance.activate()
    logger_instance.info("Should appear")
    assert "Should appear" in log_capture.getvalue()


def test_logger_activate_deactivate_cycle(logger_instance, log_capture):
    """
    Test that logger can be activated and deactivated multiple times.
    """
    logger_instance.deactivate()
    logger_instance.info("Should not appear")
    assert log_capture.getvalue() == ""
    logger_instance.activate()
    logger_instance.deactivate()
    logger_instance.activate()
    logger_instance.info("Should appear")
    assert "Should appear" in log_capture.getvalue()
