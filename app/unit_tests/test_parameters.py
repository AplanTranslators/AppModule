import pytest
from ..classes.parametrs import Parametr, ParametrArray


# ==========================================================
# Tests for Parametr
# ==========================================================

# --- Initialization ---

def test_parametr_initialization_identifier():
    # Parametr should store the identifier
    p = Parametr("WIDTH", "integer")
    assert p.identifier == "WIDTH"


def test_parametr_initialization_source_interval_default():
    # Default source_interval should be (0, 0)
    p = Parametr("WIDTH", "integer")
    assert p.source_interval == (0, 0)


def test_parametr_initialization_source_interval_custom():
    # Custom source_interval should be preserved
    p = Parametr("WIDTH", "integer", source_interval=(5, 10))
    assert p.source_interval == (5, 10)


def test_parametr_initialization_param_type():
    # Parametr should store param_type
    p = Parametr("WIDTH", "integer")
    assert p.param_type == "integer"


def test_parametr_unique_identifier_without_action_name():
    # unique_identifier should equal identifier when no action_name is given
    p = Parametr("clk", "input")
    assert p.unique_identifier == "clk"


def test_parametr_unique_identifier_with_action_name():
    # unique_identifier should prefix identifier with action_name if given
    p = Parametr("clk", "input", action_name="action")
    assert p.unique_identifier == "action_clk"


def test_parametr_default_number_is_none():
    # number should be None by default
    p = Parametr("data", "logic")
    assert p.number is None


# --- Copy behavior ---

def test_parametr_copy_preserves_source_interval():
    # copy() should preserve source_interval
    p = Parametr("WIDTH", "integer", source_interval=(3, 7))
    copy_p = p.copy()
    assert copy_p.source_interval == (3, 7)


def test_parametr_copy_preserves_identifier():
    # copy() should preserve identifier
    p = Parametr("clk", "input")
    copy_p = p.copy()
    assert copy_p.identifier == "clk"


def test_parametr_copy_preserves_param_type():
    # copy() should preserve param_type
    p = Parametr("clk", "input")
    copy_p = p.copy()
    assert copy_p.param_type == "input"


def test_parametr_copy_preserves_unique_identifier():
    # copy() should preserve unique_identifier
    p = Parametr("clk", "input", action_name="foo")
    copy_p = p.copy()
    assert copy_p.unique_identifier == "foo_clk"


def test_parametr_copy_preserves_design_unit_name():
    # copy() should preserve design_unit_name
    p = Parametr("clk", "input")
    p.design_unit_name = "unit1"
    copy_p = p.copy()
    assert copy_p.design_unit_name == "unit1"


def test_parametr_copy_preserves_number():
    # copy() should preserve number
    p = Parametr("clk", "input")
    p.number = 42
    copy_p = p.copy()
    assert copy_p.number == 42


# --- String and repr ---

def test_parametr_str_var_type():
    # __str__ should return only identifier if param_type contains "var"
    p = Parametr("myVar", "var")
    assert str(p) == "myVar"


def test_parametr_str_non_var_type():
    # __str__ should return unique_identifier:param_type otherwise
    p = Parametr("clk", "input", action_name="foo")
    assert str(p) == "foo_clk:input"


def test_parametr_repr_contains_identifier():
    # __repr__ should contain identifier for debugging
    p = Parametr("WIDTH", "integer")
    r = repr(p)
    assert "WIDTH" in r


# ==========================================================
# Tests for ParametrArray
# ==========================================================

# --- Initialization and basic operations ---

def test_parametrarray_initially_empty():
    # New ParametrArray should be empty
    arr = ParametrArray()
    assert len(arr) == 0


def test_parametrarray_add_element_success():
    # addElement should add a new Parametr
    arr = ParametrArray()
    p = Parametr("WIDTH", "integer")
    result, index = arr.addElement(p)
    assert result is True


def test_parametrarray_add_element_index():
    # addElement should return the correct index
    arr = ParametrArray()
    p = Parametr("WIDTH", "integer")
    _, index = arr.addElement(p)
    assert index == 0


def test_parametrarray_add_element_duplicate_returns_false():
    # Adding a duplicate element should return False
    arr = ParametrArray()
    p1 = Parametr("WIDTH", "integer")
    p2 = Parametr("WIDTH", "integer")
    arr.addElement(p1)
    result, index = arr.addElement(p2)
    assert result is False


def test_parametrarray_add_element_invalid_type_raises():
    # addElement should raise if element is not Parametr
    arr = ParametrArray()
    with pytest.raises(TypeError):
        arr.addElement("not_a_parametr")


def test_parametrarray_get_elements_returns_list():
    # getElements should return the list of added elements
    arr = ParametrArray()
    p = Parametr("WIDTH", "integer")
    arr.addElement(p)
    elems = arr.getElements()
    assert elems[0].identifier == "WIDTH"


# --- Copy behavior ---

def test_parametrarray_copy_creates_new_instance():
    # copy() should return a new ParametrArray
    arr = ParametrArray()
    p = Parametr("clk", "input")
    arr.addElement(p)
    arr_copy = arr.copy()
    assert isinstance(arr_copy, ParametrArray)


def test_parametrarray_copy_has_same_element_identifier():
    # copy() should preserve element identifiers
    arr = ParametrArray()
    p = Parametr("clk", "input")
    arr.addElement(p)
    arr_copy = arr.copy()
    assert arr_copy[0].identifier == "clk"


# --- Name generation ---

def test_generate_parametr_name_by_index_zero():
    # Index 0 should map to "a"
    arr = ParametrArray()
    name = arr.generateParametrNameByIndex(0)
    assert name == "a"


def test_generate_parametr_name_by_index_25():
    # Index 25 should map to "z"
    arr = ParametrArray()
    name = arr.generateParametrNameByIndex(25)
    assert name == "z"


def test_generate_parametr_name_by_index_26():
    # Index 26 should map to "aa"
    arr = ParametrArray()
    name = arr.generateParametrNameByIndex(26)
    assert name == "aa"


# --- Identifier list string ---

def test_get_identifiers_list_string_with_elements():
    # Should return identifiers in parentheses, comma-separated
    arr = ParametrArray()
    arr.addElement(Parametr("a", "integer"))
    arr.addElement(Parametr("b", "integer"))
    result = arr.getIdentifiersListString(2)
    assert result == "(a, b)"


def test_get_identifiers_list_string_empty_array_returns_empty_string():
    # Empty array should return an empty string
    arr = ParametrArray()
    result = arr.getIdentifiersListString(0)
    assert result == ""


def test_get_identifiers_list_string_raises_if_count_exceeds_elements():
    # Should raise ValueError if parametrs_count > number of elements
    arr = ParametrArray()
    arr.addElement(Parametr("a", "integer"))
    with pytest.raises(ValueError):
        arr.getIdentifiersListString(2)


# --- Unique identifier assignment ---

def test_generate_uniq_names_for_paramets_changes_unique_identifier():
    # generateUniqNamesForParamets should assign alphabetic names
    arr = ParametrArray()
    arr.addElement(Parametr("x", "integer"))
    arr.generateUniqNamesForParamets()
    assert arr[0].unique_identifier == "a"


# --- String and repr ---

def test_parametrarray_str_representation():
    # __str__ should include string representation of elements
    arr = ParametrArray()
    arr.addElement(Parametr("x", "integer"))
    s = str(arr)
    assert "x:integer" in s


def test_parametrarray_repr_contains_classname():
    # __repr__ should contain "ParametrArray"
    arr = ParametrArray()
    r = repr(arr)
    assert "ParametrArray" in r


# --- Indexing and iteration ---

def test_parametrarray_getitem_single_element():
    # Should support direct indexing
    arr = ParametrArray()
    p = Parametr("x", "integer")
    arr.addElement(p)
    assert arr[0] == p


def test_parametrarray_getitem_slice():
    # Should support slicing
    arr = ParametrArray()
    p1 = Parametr("x", "integer")
    p2 = Parametr("y", "integer")
    arr.addElement(p1)
    arr.addElement(p2)
    result = arr[0:2]
    assert result == [p1, p2]


def test_parametrarray_iterates_over_elements():
    # Should be iterable
    arr = ParametrArray()
    p = Parametr("x", "integer")
    arr.addElement(p)
    elements = list(iter(arr))
    assert elements[0] == p
