import pytest
import sys
import os
from types import SimpleNamespace


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ..utils.string_formater import StringFormater


# --------------------------
# String Formater tests
# --------------------------
@pytest.fixture
def sf():
    return StringFormater()

# --- removeTrailingComma tests ---
def test_remove_trailing_comma_single(sf):
    """Test that removeTrailingComma removes a single trailing comma."""
    assert sf.removeTrailingComma("test,") == "test"

def test_remove_trailing_comma_multiple(sf):
    """Test that removeTrailingComma removes multiple trailing commas."""
    assert sf.removeTrailingComma("test,,") == "test"

def test_remove_trailing_comma_no_comma(sf):
    """Test that removeTrailingComma does not change a string without a trailing comma."""
    assert sf.removeTrailingComma("test") == "test"

def test_remove_trailing_comma_internal_commas(sf):
    """Test that removeTrailingComma only removes the trailing comma and leaves internal commas."""
    assert sf.removeTrailingComma("test, with, commas,") == "test, with, commas"

def test_remove_trailing_comma_empty_string(sf):
    """Test that removeTrailingComma handles an empty string correctly."""
    assert sf.removeTrailingComma("") == ""


# --- addEqueToBGET tests ---
def test_add_equal_to_bget_single_arg(sf):
    """Test that addEqueToBGET adds '== 1' to a BGET with one argument."""
    assert sf.addEqueToBGET("BGET(x)") == "BGET(x) == 1"

def test_add_equal_to_bget_multiple_args(sf):
    """Test that addEqueToBGET adds '== 1' to a BGET with multiple arguments."""
    assert sf.addEqueToBGET("BGET(x,y)") == "BGET(x,y) == 1"

def test_add_equal_to_bget_other_string(sf):
    """Test that addEqueToBGET does not change a non-BGET string."""
    assert sf.addEqueToBGET("text") == "text"

def test_add_equal_to_bget_empty_string(sf):
    """Test that addEqueToBGET handles an empty string correctly."""
    assert sf.addEqueToBGET("") == ""


# --- replaceValueParametrsCalls tests ---
@pytest.fixture
def param_array():
    """Provides a mock parameter array for testing."""
    return SimpleNamespace(
        elements=[
            SimpleNamespace(identifier="foo", value=42),
            SimpleNamespace(identifier="bar", value=7),
        ]
    )

def test_replace_value_parameters_calls_both(sf, param_array):
    """Test that replaceValueParametrsCalls replaces all known parameters."""
    assert sf.replaceValueParametrsCalls(param_array, "foo + bar") == "42 + 7"

def test_replace_value_parameters_calls_one(sf, param_array):
    """Test that replaceValueParametrsCalls replaces one known parameter."""
    assert sf.replaceValueParametrsCalls(param_array, "z + bar") == "z + 7"

def test_replace_value_parameters_calls_one_other_order(sf, param_array):
    """Test that replaceValueParametrsCalls replaces one known parameter in a different position."""
    assert sf.replaceValueParametrsCalls(param_array, "foo + y") == "42 + y"

def test_replace_value_parameters_calls_empty_string(sf, param_array):
    """Test that replaceValueParametrsCalls handles an empty string correctly."""
    assert sf.replaceValueParametrsCalls(param_array, "") == ""


# --- addSpacesAroundOperators tests ---
def test_add_spaces_around_operators_simple(sf):
    """Test that addSpacesAroundOperators adds spaces around a simple operator."""
    assert sf.addSpacesAroundOperators("a+b") == "a + b"

def test_add_spaces_around_operators_multiple(sf):
    """Test that addSpacesAroundOperators adds spaces around multiple operators."""
    assert sf.addSpacesAroundOperators("a+b*c==d") == "a + b * c == d"

def test_add_spaces_around_operators_with_symbols(sf):
    """Test that addSpacesAroundOperators handles operators with symbols correctly."""
    assert sf.addSpacesAroundOperators("a>=b") == "a >= b"

def test_add_spaces_around_operators_empty(sf):
    """Test that addSpacesAroundOperators handles an empty string."""
    assert sf.addSpacesAroundOperators("") == ""


# --- valuesToAplanStandart tests ---
def test_values_to_aplan_standart_binary(sf):
    """Test that valuesToAplanStandart converts binary format."""
    assert sf.valuesToAplanStandart("4'b1010") == "10"

def test_values_to_aplan_standart_hex(sf):
    """Test that valuesToAplanStandart converts hexadecimal format."""
    assert sf.valuesToAplanStandart("2'hf") == "15"

def test_values_to_aplan_standart_decimal(sf):
    """Test that valuesToAplanStandart converts decimal format."""
    assert sf.valuesToAplanStandart("'123") == "123"


# --- addBracketsAfterNegation tests ---
def test_add_brackets_after_negation_simple(sf):
    """Test that addBracketsAfterNegation adds brackets to a simple negation."""
    assert sf.addBracketsAfterNegation("!x") == "!(x)"

def test_add_brackets_after_negation_complex(sf):
    """Test that addBracketsAfterNegation works within a larger expression."""
    assert sf.addBracketsAfterNegation("y && !z") == "y && !(z)"

def test_add_brackets_after_negation_double(sf):
    """Test that addBracketsAfterNegation handles chained negations."""
    assert sf.addBracketsAfterNegation("!!c") == "!(!c)"

def test_add_brackets_after_negation_empty(sf):
    """Test that addBracketsAfterNegation handles an empty string."""
    assert sf.addBracketsAfterNegation("") == ""


# --- addLeftValueForUnaryOrOperator tests ---
def test_add_left_value_for_unary_or_operator_simple(sf):
    """Test that addLeftValueForUnaryOrOperator adds the left value for a simple unary OR."""
    assert sf.addLeftValueForUnaryOrOperator("out = |x") == "out = out|x"

def test_add_left_value_for_unary_or_operator_binary(sf):
    """Test that addLeftValueForUnaryOrOperator does not change a binary OR operation."""
    assert sf.addLeftValueForUnaryOrOperator("out = x|b") == "out = x|b"

def test_add_left_value_for_unary_or_operator_multiple(sf):
    """Test that addLeftValueForUnaryOrOperator handles multiple unary ORs."""
    assert sf.addLeftValueForUnaryOrOperator("out = |y|z") == "out = out|y|z"


# --- addBracketsAfterTilda tests ---
def test_add_brackets_after_tilda_simple(sf):
    """Test that addBracketsAfterTilda adds brackets to a simple tilde expression."""
    assert sf.addBracketsAfterTilda("~x") == "~(x)"

def test_add_brackets_after_tilda_complex(sf):
    """Test that addBracketsAfterTilda works within a larger expression."""
    assert sf.addBracketsAfterTilda("a + ~b") == "a + ~(b)"

def test_add_brackets_after_tilda_empty(sf):
    """Test that addBracketsAfterTilda handles an empty string."""
    assert sf.addBracketsAfterTilda("") == ""

# --- parallelAssignment2Assignment tests ---
def test_parallelAssignment2Assignment(sf):
    """
    Test parallelAssignment2Assignment method.
    Ensure it replaces the "<=" operator with "=" .
    """
    assert sf.parallelAssignment2Assignment("a <= 1") == "a = 1"


# --- doubleOperators2Aplan tests ---
def test_double_operators_to_aplan_increment(sf):
    """Test that doubleOperators2Aplan converts '++' to '= x + 1'."""
    assert sf.doubleOperators2Aplan("x++") == "x = x + 1"

def test_double_operators_to_aplan_decrement(sf):
    """Test that doubleOperators2Aplan converts '--' to '= x - 1'."""
    assert sf.doubleOperators2Aplan("x--") == "x = x - 1"

def test_double_operators_to_aplan_multiple(sf):
    """Test that doubleOperators2Aplan converts multiple operators in one string."""
    assert sf.doubleOperators2Aplan("c++; d--") == "c = c + 1; d = d - 1"

def test_double_operators_to_aplan_empty(sf):
    """Test that doubleOperators2Aplan handles an empty string."""
    assert sf.doubleOperators2Aplan("") == ""


# --- notConcreteIndex2AplanStandart tests ---
def test_notConcreteIndex2AplanStandart_with_dimension(sf):
    """
    Test notConcreteIndex2AplanStandart method when a declaration with dimension exists.
    The method should replace array-style indexing `foo.bar[i]`
    with function-style syntax `foo.bar(i)`.
    """
    mock_decl = SimpleNamespace()
    mock_decl.findDeclWithDimentionByName = lambda name: object()
    mock_design_unit = SimpleNamespace(declarations=mock_decl)
    expr = "foo.bar[i]"
    assert sf.notConcreteIndex2AplanStandart(expr, mock_design_unit) == "foo.bar(i)"


# --- notConcreteIndex2AplanStandart tests ---
def test_notConcreteIndex2AplanStandart_without_dimension(sf):
    """
    Test notConcreteIndex2AplanStandart method when no declaration with dimension exists.
    The method should replace array-style indexing `foo.bar[i]`
    with a call to `BGET(foo.bar, i)`.
    """
    mock_decl = SimpleNamespace()
    mock_decl.findDeclWithDimentionByName = lambda name: None
    mock_design_unit = SimpleNamespace(declarations=mock_decl)
    expr = "foo.bar[i]"
    assert (
        sf.notConcreteIndex2AplanStandart(expr, mock_design_unit) == "BGET(foo.bar, i)"
    )


# --- vectorSizes2AplanStandart tests ---
def test_vector_sizes_to_aplan_standart_single_index(sf):
    """Test that vectorSizes2AplanStandart converts a single index to a function call."""
    assert sf.vectorSizes2AplanStandart("signal[7]") == "signal(7)"

def test_vector_sizes_to_aplan_standart_range_index(sf):
    """Test that vectorSizes2AplanStandart converts a range index to a function call."""
    assert sf.vectorSizes2AplanStandart("signal[4:0]") == "signal(0,4)"

def test_vector_sizes_to_aplan_standart_empty(sf):
    """Test that vectorSizes2AplanStandart handles an empty string."""
    assert sf.vectorSizes2AplanStandart("") == ""


# --- generatePythonStyleTernary tests ---
def test_generate_python_style_ternary_with_condition(sf):
    """Test that generatePythonStyleTernary converts a standard ternary operation."""
    assert sf.generatePythonStyleTernary("(x > 0) ? 1 : 0") == "(1 if x > 0 else 0)"

def test_generate_python_style_ternary_simple(sf):
    """Test a simplified ternary conversion."""
    assert sf.generatePythonStyleTernary("(x)?y:z") == "(y if x else z)"

def test_generate_python_style_ternary_no_ternary(sf):
    """Test that generatePythonStyleTernary does not change a non-ternary expression."""
    assert sf.generatePythonStyleTernary("a + b") == "a + b"

def test_generate_python_style_ternary_empty(sf):
    """Test that generatePythonStyleTernary handles an empty string."""
    assert sf.generatePythonStyleTernary("") == ""


# --- replace_cpp_operators tests ---
def test_replace_cpp_operators_and(sf):
    """Test that '&&' is replaced with 'and'."""
    assert sf.replace_cpp_operators("a && b") == "a and b"

def test_replace_cpp_operators_or(sf):
    """Test that '||' is replaced with 'or'."""
    assert sf.replace_cpp_operators("a || b") == "a or b"

def test_replace_cpp_operators_not(sf):
    """Test that '!' is replaced with 'not'."""
    assert sf.replace_cpp_operators("!c") == "not c"

def test_replace_cpp_operators_divide(sf):
    """Test that '/' is replaced with '//' for integer division."""
    assert sf.replace_cpp_operators("x / y") == "x // y"

def test_replace_cpp_operators_increment(sf):
    """Test that '++' is replaced with '+= 1'."""
    assert sf.replace_cpp_operators("x++") == "x += 1"

def test_replace_cpp_operators_booleans(sf):
    """Test that 'true' and 'false' are replaced with 'True' and 'False'."""
    assert sf.replace_cpp_operators("true && false") == "True and False"

def test_replace_cpp_operators_all_together(sf):
    """Test that all replacements work within a single expression."""
    assert sf.replace_cpp_operators("x&&y||!z") == "x and y or not z"

def test_replace_cpp_operators_empty(sf):
    """Test that an empty string remains empty."""
    assert sf.replace_cpp_operators("") == ""
