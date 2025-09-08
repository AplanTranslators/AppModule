import pytest
from ..classes.action_precondition import ActionPrecondition, ActionPreconditionArray


# -----------------------
# Tests for ActionPrecondition
# -----------------------

def test_action_precondition_init_sets_precondition():
    # When initialized, the precondition string should be stored correctly
    obj = ActionPrecondition("a <= b")
    assert obj.precondition == "a <= b"


def test_action_precondition_inherits_identifier_from_basic():
    # ActionPrecondition inherits from Basic
    # Its identifier is set to an empty string by default
    obj = ActionPrecondition("a > 0")
    assert obj.identifier == ""

def test_action_precondition_inherits_source_interval_from_basic():
    # ActionPrecondition inherits from Basic
    # Its source_interval is set to (0, 0) by default
    obj = ActionPrecondition("a > 0")
    assert obj.source_interval == (0, 0)

def test_action_precondition_str_returns_precondition():
    # Converting the object to str should return only the precondition string
    obj = ActionPrecondition("b >= a")
    assert str(obj) == "b >= a"


def test_action_precondition_repr_format():
    # repr() should display class name, identifier (empty), and precondition
    obj = ActionPrecondition("b == 0")
    expected = "ActionPrecondition('', 'b == 0')\n"
    assert repr(obj) == expected


# -----------------------
# Tests for ActionPreconditionArray
# -----------------------

@pytest.fixture
def precondition_array():
    """
    Fixture: provides a pre-filled ActionPreconditionArray
    with two conditions ("a != 0" and "b == 0").
    """
    arr = ActionPreconditionArray()
    arr.addElement(ActionPrecondition("a != 0"))
    arr.addElement(ActionPrecondition("b == 0"))
    return arr


def test_action_precondition_array_init_sets_type():
    # The array must be configured to only hold ActionPrecondition objects
    arr = ActionPreconditionArray()
    assert arr.element_type is ActionPrecondition


def test_action_precondition_array_str_single_element():
    # String conversion with one element should return that element only
    arr = ActionPreconditionArray()
    arr.addElement(ActionPrecondition("c <= b"))
    assert str(arr) == "c <= b"


def test_action_precondition_array_repr(precondition_array):
    # repr() should include the class name and internal list of elements
    result = repr(precondition_array)
    assert result.startswith("ActionPreconditionArray(")
    assert "ActionPrecondition('', 'a != 0')" in result


def test_action_precondition_array_str_multiple_elements():
    # Multiple preconditions should be joined with semicolons
    arr = ActionPreconditionArray()
    precondition1 = ActionPrecondition("x > 0")
    precondition2 = ActionPrecondition("y < 10")
    arr.addElement(precondition1)
    arr.addElement(precondition2)
    assert str(arr) == "x > 0;y < 10"


def test_action_precondition_array_iteration(precondition_array):
    # Iteration should yield ActionPrecondition objects
    elements = [e for e in precondition_array]
    assert all(isinstance(e, ActionPrecondition) for e in elements)


def test_action_precondition_array_indexing(precondition_array):
    # Indexing should return an ActionPrecondition
    first = precondition_array[0]
    assert isinstance(first, ActionPrecondition)
    assert str(first) == "a != 0"


def test_action_precondition_array_copy_independence(precondition_array):
    # Copying should create an independent copy
    copied = precondition_array.copy()
    copied.addElement(ActionPrecondition("c < 10"))
    # Copy has one more element than original
    assert len(copied) == len(precondition_array) + 1
    # Original remains unchanged
    assert len(precondition_array) == 2


def test_action_precondition_array_str_empty():
    # When no elements are added, the string representation should be empty.
    arr = ActionPreconditionArray()
    assert str(arr) == ""

def test_action_precondition_array_get_elements_length(precondition_array):
    # getElements() should return two elements
    elements = precondition_array.getElements()
    assert len(elements) == 2

def test_action_precondition_array_get_elements_first(precondition_array):
    # The first element in getElements() should be "a != 0"
    elements = precondition_array.getElements()
    assert str(elements[0]) == "a != 0"

def test_action_precondition_array_invalid_index_raises():
    # Accessing an index that does not exist should raise IndexError.
    arr = ActionPreconditionArray()
    with pytest.raises(IndexError):
        _ = arr[0]

def test_action_precondition_array_add_invalid_element_is_ignored():
    # Adding an invalid type should not increase the array size
    arr = ActionPreconditionArray()
    arr.addElement("not_a_precondition")
    assert len(arr) == 0
