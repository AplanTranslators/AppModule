# utils_test.py
import time as pytime
import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ..utils.singleton import SingletonMeta
from ..utils.time import TimeUtils
from ..utils.counters import Counters, CounterTypes

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
@pytest.fixture
def time_utils():
    """Provides a fresh instance of TimeUtils for each test."""
    return TimeUtils()

# --- Tests for format_time_m_s ---
def test_format_time_m_s_normal_case(time_utils):
    """Test formatting for a time with both minutes and seconds."""
    assert time_utils.format_time_m_s(75) == "1 m 15 s"

def test_format_time_m_s_less_than_minute(time_utils):
    """Test formatting for a time less than one minute."""
    assert time_utils.format_time_m_s(59) == "59 s"

def test_format_time_m_s_exact_minutes(time_utils):
    """Test formatting for a time that's an exact multiple of a minute."""
    assert time_utils.format_time_m_s(120) == "2 m 0 s"

def test_format_time_m_s_large_value(time_utils):
    """Test formatting for a large time value."""
    assert time_utils.format_time_m_s(3599) == "59 m 59 s"
    assert time_utils.format_time_m_s(3600) == "60 m 0 s"

def test_format_time_m_s_zero(time_utils):
    """Test formatting for zero seconds."""
    assert time_utils.format_time_m_s(0) == "0 s"

# --------------------------
# Tests for format_time_date_h_m_s
# --------------------------

def test_format_time_date_h_m_s(mocker):
    """
    Test that format_time_date_h_m_s correctly formats a timestamp into 'YYYY-MM-DD HH:MM:SS' format.
    Should handle various timestamps and ensure the format is consistent
    """
    tu = TimeUtils()
    ts = 1672531200  # 2023-01-01 00:00:00 UTC
    mocker.patch('time.localtime', return_value=pytime.gmtime(ts))
    formatted = tu.format_time_date_h_m_s(ts)
    assert len(formatted) == 19
    assert formatted.count(":") == 2
    assert formatted.count("-") == 2
    assert formatted == "2023-01-01 00:00:00", "Should format to 'YYYY-MM-DD HH:MM:SS'"

def test_format_time_h_m_s():
    """
    Test that format_time_h_m_s correctly formats a timestamp into 'HH:MM:SS' format.
    The output depends on local timezone, so only check the format.
    """
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

def test_counters_initial_assignment_counter(counters):
    """Test that the assignment counter is initialized to 1."""
    assert counters.get(CounterTypes.ASSIGNMENT_COUNTER) == 1

def test_counters_initial_case_counter(counters):
    """Test that the case counter is initialized to 0."""
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
    """
    Test that the get method raises ValueError for an unhandled counter type.
    """
    with pytest.raises(ValueError):
        counters.get(CounterTypes.SEQUENCE_COUNTER)  # initially present but test removal
        counters.counters.pop(CounterTypes.SEQUENCE_COUNTER.value)
        counters.get(CounterTypes.SEQUENCE_COUNTER)

def test_get_invalid_counter_type(counters):
    with pytest.raises(ValueError, match="Unhandled counter type: NONE_COUNTER"):
        counters.get(CounterTypes.NONE_COUNTER)

def test_incriese_invalid_type(counters):
    """ Test that incriese raises ValueError for an unhandled counter type.
    """
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