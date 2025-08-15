# utils_test.py
import time as pytime
import sys
import os
import logging
import pytest
import re
from io import StringIO
from types import SimpleNamespace

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ..utils.singleton import SingletonMeta
from ..utils.time import TimeUtils
from ..utils.counters import Counters, CounterTypes
from ..utils.logger import Logger
from ..utils.string_formater import StringFormater


# --------------------------
# SingletonMeta tests
# --------------------------
def test_singleton_meta_behavior():
    class A(metaclass=SingletonMeta):
        pass

    a1 = A()
    a2 = A()
    assert a1 is a2, "SingletonMeta should return the same instance for multiple calls"

    # Different class => different singleton
    class B(metaclass=SingletonMeta):
        pass

    b1 = B()
    assert a1 is not b1


# --------------------------
# TimeUtils tests
# --------------------------
def test_format_time_m_s():
    tu = TimeUtils()
    assert tu.format_time_m_s(75) == "1 m 15 s"
    assert tu.format_time_m_s(59) == "59 s"
    assert tu.format_time_m_s(120) == "2 m 0 s"
    assert tu.format_time_m_s(3599) == "59 m 59 s"
    assert tu.format_time_m_s(3600) == "60 m 0 s", "Large value should handle hours"
    assert tu.format_time_m_s(0) == "0 s", "Zero should be '0 s'"

def test_format_time_date_h_m_s(mocker):
    tu = TimeUtils()
    ts = 1672531200  # 2023-01-01 00:00:00 UTC
    mocker.patch('time.localtime', return_value=pytime.gmtime(ts))
    formatted = tu.format_time_date_h_m_s(ts)
    assert len(formatted) == 19
    assert formatted.count(":") == 2
    assert formatted.count("-") == 2

def test_format_time_h_m_s():
    tu = TimeUtils()
    ts = 1672531200  # 2023-01-01 00:00:00 UTC
    formatted = tu.format_time_h_m_s(ts)
    assert len(formatted) == 8
    assert formatted.count(":") == 2


# --------------------------
# Counters tests
# --------------------------
@pytest.fixture
def counters():
    c = Counters()
    c.reinit()
    return c

def test_counters_initial_values(counters):
    assert counters.get(CounterTypes.ASSIGNMENT_COUNTER) == 1
    assert counters.get(CounterTypes.CASE_COUNTER) == 0

def test_incriese(counters):
    """
    Test that the incriese method correctly increments a counter.
    """
    initial = counters.get(CounterTypes.ASSIGNMENT_COUNTER)
    counters.incriese(CounterTypes.ASSIGNMENT_COUNTER)
    assert counters.get(CounterTypes.ASSIGNMENT_COUNTER) == initial + 1

def test_decriese(counters):
    """
    Test that the decriese method correctly decrements a counter.
    """
    counters.incriese(CounterTypes.CASE_COUNTER)
    initial = counters.get(CounterTypes.CASE_COUNTER)
    counters.decriese(CounterTypes.CASE_COUNTER)
    assert counters.get(CounterTypes.CASE_COUNTER) == initial - 1

def test_decriese_not_below_zero(counters):
    """
    Test that the decriese method does not decrement a counter below 0.
    """
    counters.decriese(CounterTypes.CASE_COUNTER)  # already at 0
    assert counters.get(CounterTypes.CASE_COUNTER) == 0
    
def test_get_invalid_counter_type(counters):
    with pytest.raises(ValueError):
        counters.get(CounterTypes.SEQUENCE_COUNTER)  # initially present but test removal
        counters.counters.pop(CounterTypes.SEQUENCE_COUNTER.value)
        counters.get(CounterTypes.SEQUENCE_COUNTER)

def test_get_invalid_counter_type(counters):
    with pytest.raises(ValueError, match="Unhandled counter type: NONE_COUNTER"):
        counters.get(CounterTypes.NONE_COUNTER)

def test_incriese_invalid_type(counters):
    class FakeEnum:
        value = 9999
        name = "FAKE"

    with pytest.raises(ValueError):
        counters.incriese(FakeEnum)

def test_deinit_resets_values(counters):
    """
    Test that deinit resets all counters to their initial values.
    """
    counters.incriese(CounterTypes.ASSIGNMENT_COUNTER)
    counters.incriese(CounterTypes.CASE_COUNTER)
    assert counters.get(CounterTypes.ASSIGNMENT_COUNTER) == 2
    assert counters.get(CounterTypes.CASE_COUNTER) == 1

    counters.deinit()

    assert counters.get(CounterTypes.ASSIGNMENT_COUNTER) == 1
    assert counters.get(CounterTypes.CASE_COUNTER) == 0


def test_get_returns_correct_value(counters):
    """
    Test that the get method returns the correct value.
    """
    counters.incriese(CounterTypes.MODULE_COUNTER)
    assert counters.get(CounterTypes.MODULE_COUNTER) == 2


# --------------------------
# Logger tests
# --------------------------
@pytest.fixture
def logger_instance():
    logger = Logger()
    logger.activate()  # ensure active before each test
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
    getattr(logger_instance, method)("Test message")
    output = log_capture.getvalue()
    assert "Test message" in output


def test_logger_temp_color_usage(logger_instance, log_capture):
    # Color is optional, but we pass one to trigger temp color logic
    logger_instance.info("Colored message", color="red")
    output = log_capture.getvalue()
    assert "Colored message" in output  # We don't assert color codes, just presence


def test_logger_activate_deactivate(logger_instance, log_capture):
    logger_instance.deactivate()
    logger_instance.info("Should not appear")
    assert log_capture.getvalue() == ""

    logger_instance.activate()
    logger_instance.info("Should appear")
    assert "Should appear" in log_capture.getvalue()

def test_logger_activate_deactivate_cycle(logger_instance, log_capture):
    logger_instance.deactivate()
    logger_instance.info("Should not appear")
    assert log_capture.getvalue() == ""
    logger_instance.activate()
    logger_instance.deactivate()
    logger_instance.activate()
    logger_instance.info("Should appear")
    assert "Should appear" in log_capture.getvalue()

def test_logger_delimetr_without_text(logger_instance, log_capture):
    logger_instance.delimetr(size=5, color="blue")
    output = log_capture.getvalue()
    assert "=====" in output

def test_logger_delimetr_with_text(logger_instance, log_capture):
    logger_instance.delimetr(size=3, color="green", text="Hello")
    output = log_capture.getvalue()
    assert "===" in output
    assert "Hello" in output

def test_logger_delimetr_long_text(logger_instance, log_capture):
    logger_instance.delimetr(size=2, text="VeryLongText")
    output = log_capture.getvalue()
    assert "VeryLongText" in output  # Should handle overflow


# --------------------------
# String Formater tests
# --------------------------
@pytest.fixture
def sf():
    return StringFormater()


def test_remove_trailing_comma(sf):
    assert sf.removeTrailingComma("test,") == "test"
    assert sf.removeTrailingComma("test") == "test"
    assert sf.removeTrailingComma("test,,") == "test"
    assert sf.removeTrailingComma("test, with, commas,") == "test, with, commas"
    assert sf.removeTrailingComma("") == ""


def test_addEqueToBGET(sf):
    """Test addEqueToBGET method."""
    assert sf.addEqueToBGET("BGET(x)") == "BGET(x) == 1"
    assert sf.addEqueToBGET("BGET(x,y)") == "BGET(x,y) == 1"
    assert sf.addEqueToBGET("text") == "text"
    assert sf.addEqueToBGET("") == ""


def test_replaceValueParametrsCalls(sf):
    """Test replaceValueParametrsCalls method."""
    param_array = SimpleNamespace(elements=[
        SimpleNamespace(identifier="foo", value=42),
        SimpleNamespace(identifier="bar", value=7)
    ])
    assert sf.replaceValueParametrsCalls(param_array, "foo + bar") == "42 + 7"
    assert sf.replaceValueParametrsCalls(param_array, "z + bar") == "z + 7"
    assert sf.replaceValueParametrsCalls(param_array, "foo + y") == "42 + y"
    assert sf.replaceValueParametrsCalls(param_array, "") == ""


def test_addSpacesAroundOperators(sf):
    """Test addSpacesAroundOperators method."""
    assert sf.addSpacesAroundOperators("a+b") == "a + b"
    assert sf.addSpacesAroundOperators("a+b*c==d") == "a + b * c == d"
    assert sf.addSpacesAroundOperators("a>=b") == "a >= b"
    assert sf.addSpacesAroundOperators("") == ""


def test_valuesToAplanStandart(sf):
    """Test valuesToAplanStandart method."""
    assert sf.valuesToAplanStandart("4'b1010") == "10"   # binary
    assert sf.valuesToAplanStandart("2'hf") == "15"      # hex
    assert sf.valuesToAplanStandart("'123") == "123"     # decimal


def test_addBracketsAfterNegation(sf):
    """Test addBracketsAfterNegation method."""
    assert sf.addBracketsAfterNegation("!x") == "!(x)"
    assert sf.addBracketsAfterNegation("y && !z") == "y && !(z)"
    assert sf.addBracketsAfterNegation("!!c") == "!(!c)"
    assert sf.addBracketsAfterNegation("") == ""


def test_addLeftValueForUnaryOrOperator(sf):
    """Test addLeftValueForUnaryOrOperator method."""
    assert sf.addLeftValueForUnaryOrOperator("out = |x") == "out = out|x"
    assert sf.addLeftValueForUnaryOrOperator("out = x|b") == "out = x|b"
    assert sf.addLeftValueForUnaryOrOperator("out = |y|z") == "out = out|y|z"


def test_addBracketsAfterTilda(sf):
    assert sf.addBracketsAfterTilda("~x") == "~(x)"
    assert sf.addBracketsAfterTilda("a + ~b") == "a + ~(b)"
    assert sf.addBracketsAfterNegation("") == ""


def test_parallelAssignment2Assignment(sf):
    assert sf.parallelAssignment2Assignment("a <= 1") == "a = 1"


def test_doubleOperators2Aplan(sf):
    assert sf.doubleOperators2Aplan("x++") == "x = x + 1"
    assert sf.doubleOperators2Aplan("x--") == "x = x - 1"
    assert sf.doubleOperators2Aplan("c++; d--") == "c = c + 1; d = d - 1"
    assert sf.addBracketsAfterNegation("") == ""


def test_notConcreteIndex2AplanStandart_with_dimension(sf):
    mock_decl = SimpleNamespace()
    mock_decl.findDeclWithDimentionByName = lambda name: object()
    mock_design_unit = SimpleNamespace(declarations=mock_decl)
    expr = "foo.bar[i]"
    assert sf.notConcreteIndex2AplanStandart(expr, mock_design_unit) == "foo.bar(i)"


def test_notConcreteIndex2AplanStandart_without_dimension(sf):
    mock_decl = SimpleNamespace()
    mock_decl.findDeclWithDimentionByName = lambda name: None
    mock_design_unit = SimpleNamespace(declarations=mock_decl)
    expr = "foo.bar[i]"
    assert sf.notConcreteIndex2AplanStandart(expr, mock_design_unit) == "BGET(foo.bar, i)"


def test_vectorSizes2AplanStandart_single(sf):
    assert sf.vectorSizes2AplanStandart("signal[7]") == "signal(7)"
    assert sf.vectorSizes2AplanStandart("signal[4:0]") == "signal(0,4)"
    assert sf.vectorSizes2AplanStandart("") == ""


def test_generatePythonStyleTernary(sf):
    assert sf.generatePythonStyleTernary("(x > 0) ? 1 : 0") == "(1 if x > 0 else 0)"
    assert sf.generatePythonStyleTernary("(x)?y:z") == "(y if x else z)"
    # Should remain unchanged if no ternary match
    assert sf.generatePythonStyleTernary("a + b") == "a + b"
    assert sf.generatePythonStyleTernary("") == ""


def test_replace_cpp_operators(sf):
    expr = "a && b || !c / d ++ true false"
    out = sf.replace_cpp_operators(expr)
    # Check replacements individually
    assert "and" in out
    assert "or" in out
    assert "not" in out
    assert "//" in out
    assert "+= 1" in out
    assert "True" in out
    assert "False" in out
    assert sf.replace_cpp_operators("x / y") == "x // y"
    assert sf.replace_cpp_operators("true && false") == " True  and  False "
    assert sf.replace_cpp_operators("x++") == "x += 1"
    assert sf.replace_cpp_operators("x && y || !z") == "x  and  y  or  not  z"
    assert sf.replace_cpp_operators("") == ""