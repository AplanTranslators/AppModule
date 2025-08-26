import pytest
from ..utils.unsorted import UnsortedUnils


@pytest.fixture
def uu():
    return UnsortedUnils()


# ---------------------------
# Tests for is_interval_contained
# ---------------------------
def test_is_interval_contained_true(uu):
    """
    Test if the first interval is contained within the second interval.
    """
    assert uu.is_interval_contained((2, 5), (1, 10)) is True


def test_is_interval_contained_false(uu):
    """
    Test if the first interval is not contained within the second interval.
    Interval1 is outside Interval2 → should return False.
    """
    assert uu.is_interval_contained((0, 11), (1, 10)) is False


# ---------------------------
# Tests for isNumericString
# ---------------------------
def test_isNumericString_valid(uu):
    """
    Test if the string is a valid numeric string.  
    String with only digits should return the same string.     
    """
    assert uu.isNumericString("12345") == "12345"


def test_isNumericString_invalid(uu):
    """
    Test if the string is not a valid numeric string.
    String with non-digit characters should return None.
    """
    assert uu.isNumericString("12a45") is None


# ---------------------------
# Tests for containsOnlyPipe
# ---------------------------
def test_containsOnlyPipe_true(uu):
    """
    Test if the string contains only a single pipe character.
    Single pipe should return True.
    """
    assert uu.containsOnlyPipe("|") is True


def test_containsOnlyPipe_false(uu):
    """
    Test if the string does not contain only a single pipe character.
    String with multiple pipes or other characters should return None.
    """
    assert uu.containsOnlyPipe("||") is None


# ---------------------------
# Tests for isVariablePresent
# ---------------------------
@pytest.mark.parametrize(
    "expr, variable, expected",
    [
        ("a + b", "a", True),
        ("foo(bar)", "bar", True),
        ("foo(bar)", "baz", False),
        ("", "x", False),
        ("x + y", "", False),
    ],
)
def test_isVariablePresent(uu, expr, variable, expected):
    """
    Test checks if variable presence in expression is correctly detected.
    """
    assert uu.isVariablePresent(expr, variable) == expected


# ---------------------------
# Tests for extractFunctionName
# ---------------------------
@pytest.mark.parametrize(
    "expression, expected",
    [
        ("myFunc(123)", "myFunc"),
        ("_hidden$func(arg)", "_hidden$func"),
        ("noFunctionHere", None),
    ],
)
def test_extractFunctionName(uu, expression, expected):
    """
    Test checks if function name extraction from expression works correctly.
    Extract function names correctly, or return None if not found.
    """
    assert uu.extractFunctionName(expression) == expected


# ---------------------------
# Tests for vectorSize2AplanVectorSize
# ---------------------------
def test_vectorSize2AplanVectorSize_normal(uu):
    """ 
    Test that the vectorSize2AplanVectorSize function correctly calculates the vector size.
    It shouldNormal case: left=8, right=4 → result [4, 4].
    """
    assert uu.vectorSize2AplanVectorSize("8", "4") == [4, 4]


def test_vectorSize2AplanVectorSize_right_zero(uu):
    """
    Test that the vectorSize2AplanVectorSize function handles right being "0".
    Right is "0" → left is incremented by 1, right is set to 0.
    """
    assert uu.vectorSize2AplanVectorSize("7", "0") == [8, 0]


def test_vectorSize2AplanVectorSize_raises(uu):
    """ 
    Test that the vectorSize2AplanVectorSize function raises ValueError for None inputs.
    """
    with pytest.raises(ValueError):
        uu.vectorSize2AplanVectorSize(None, "1")


# ---------------------------
# Tests for extractVectorSize
# ---------------------------
def test_evaluateExpression_basic(uu):
    """ 
    Test that the evaluateExpression function evaluates a basic arithmetic expression.
    """
    assert uu.evaluateExpression("2+3*4") == 14


def test_evaluateExpression_with_variables(uu):
    """ 
    Test that the evaluateExpression function evaluates an expression with variables.
    Expressions with variables should use provided mapping.
    """
    assert uu.evaluateExpression("a*b", {"a": 2, "b": 5}) == 10


# ---------------------------
# Tests for extractVectorSize
# ---------------------------
def test_extractVectorSize_valid(uu):
    """
    Test that the extractVectorSize function extracts vector size from a valid string.
    Valid case: "[3:1]" → should return ["3", "1"].
    """
    s = "[3:1]"
    result = uu.extractVectorSize(s)
    assert result == ["3", "1"]


def test_extractVectorSize_none(uu):
    """
    Test that the extractVectorSize function returns None for a string with no match.
    String with no vector size should return None.
    """
    assert uu.extractVectorSize("no match") is None


# ---------------------------
# Tests for extractDimentionSize
# ---------------------------
def test_extractDimentionSize_vector_case(uu):
    """
    Test that the extractDimentionSize function extracts dimension size from a vector size.
    Vector size "[3:1]" → should return 2 (3-1=2).
    """
    assert uu.extractDimentionSize("[3:1]") == 2  # (3-1=2)


def test_extractDimentionSize_single_value(uu):
    """
    Test that the extractDimentionSize function extracts dimension size from a single value.
    Single value "[5]" → should return 5.
    """
    assert uu.extractDimentionSize("[5]") == 5


def test_extractDimentionSize_dollar_case(uu):
    """
    Test that the extractDimentionSize function handles the special case of "$".
    Special case "[$]" → should return None.
    """
    assert uu.extractDimentionSize("[$]") is None


# ---------------------------
# Tests for containsOperator
# ---------------------------
@pytest.mark.parametrize(
    "s, expected",
    [
        ("a+b", "+"),
        ("c&d", "&"),
        ("no_ops", None),
    ],
)
def test_containsOperator(uu, s, expected):
    """
    Test that the containsOperator function detects operators in a string.
    It should return the operator if present, or None if not.
    """
    assert uu.containsOperator(s) == expected


# ---------------------------
# Tests for generate_unique_short_id
# ---------------------------
def test_generate_unique_short_id_length(uu):
    """
    Test that the generate_unique_short_id function generates a unique ID of length 4.
    """
    result = uu.generate_unique_short_id("test_string")
    assert isinstance(result, str)
    assert len(result) == 4


def test_generate_unique_short_id_same_input_same_output(uu):
    """
    Test that the generate_unique_short_id function returns the same ID for the same input.
    """
    assert uu.generate_unique_short_id("abc") == uu.generate_unique_short_id("abc")


def test_generate_unique_short_id_non_string_raises(uu):
    """
    Test that the generate_unique_short_id function raises TypeError for non-string input.
    """
    with pytest.raises(TypeError):
        uu.generate_unique_short_id(123)
