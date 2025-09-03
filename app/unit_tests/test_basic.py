import pytest
import copy
from unittest.mock import MagicMock
from ..classes.basic import Basic, BasicArray
from ..classes.element_types import ElementsTypes
from ..utils.counters import Counters
from ..utils.logger import Logger
from ..utils.string_formater import StringFormater
from ..utils.unsorted import UnsortedUnils


@pytest.fixture
def basic_instance():
    Basic.counters = Counters()
    Basic.logger = Logger()
    Basic.utils = UnsortedUnils()
    Basic.string_formater = StringFormater()
    return Basic(
        identifier="test_basic",
        source_interval=(10, 20),
        element_type=ElementsTypes.ASSERT_ELEMENT,
    )


# Fixture for a BasicArray object
@pytest.fixture
def basic_array_instance():
    BasicArray.counters = Counters()
    BasicArray.logger = Logger()
    BasicArray.utils = UnsortedUnils()
    BasicArray.string_formater = StringFormater()
    return BasicArray()


# Fixture for a filled BasicArray
@pytest.fixture
def filled_basic_array(basic_array_instance):
    element1 = Basic("elem1", element_type=ElementsTypes.ASSERT_ELEMENT)
    element2 = Basic("elem2", element_type=ElementsTypes.IF_STATEMENT_ELEMENT)
    element3 = Basic("elem3", element_type=ElementsTypes.ASSERT_ELEMENT)
    basic_array_instance.addElement(element1)
    basic_array_instance.addElement(element2)
    basic_array_instance.addElement(element3)
    return basic_array_instance


# Reset counters after each test to ensure test isolation
@pytest.fixture(autouse=True)
def reset_counters():
    Counters().deinit()
    yield
    Counters().deinit()


class TestBasic:
    """Tests for the Basic class."""

    # ---- Initialization ----
    def test_init_sets_identifier(self, basic_instance):
        """Test that Basic initializes identifier correctly."""
        assert basic_instance.identifier == "test_basic"

    def test_init_sets_source_interval(self, basic_instance):
        """Test that Basic initializes source_interval correctly."""
        assert basic_instance.source_interval == (10, 20)

    def test_init_sets_element_type(self, basic_instance):
        """Test that Basic initializes element_type correctly."""
        assert basic_instance.element_type == ElementsTypes.ASSERT_ELEMENT

    def test_init_defaults_number_to_none(self, basic_instance):
        """Test that the 'number' attribute defaults to None."""
        assert basic_instance.number is None

    
    # ---- Copy & deepcopy ----
    def test_copy_creates_new_object(self, basic_instance):
        """Test that the copy() method returns a new object instance."""
        copied_obj = basic_instance.copy()
        assert copied_obj is not basic_instance

    def test_copy_duplicates_identifier(self, basic_instance):
        """Tests that the copy() method correctly duplicates the identifier."""
        copied_obj = basic_instance.copy()
        assert copied_obj.identifier == basic_instance.identifier

    def test_copy_duplicates_source_interval(self, basic_instance):
        """Tests that the copy() method correctly duplicates the source interval."""
        copied_obj = basic_instance.copy()
        assert copied_obj.source_interval == basic_instance.source_interval

    def test_copy_duplicates_element_type(self, basic_instance):
        """Tests that the copy() method correctly duplicates the element type."""
        copied_obj = basic_instance.copy()
        assert copied_obj.element_type == basic_instance.element_type

    def test_copy_duplicates_sequence(self, basic_instance):
        """Tests that the copy() method duplicates the sequence number."""
        basic_instance.number = 5
        copied_obj = basic_instance.copy()
        assert copied_obj.sequence == basic_instance.sequence

    def test_copy_duplicates_number(self, basic_instance):
        """Tests that the copy() method duplicates the number attribute."""
        basic_instance.number = 5
        copied_obj = basic_instance.copy()
        assert copied_obj.number == basic_instance.number

    def test_deepcopy_creates_new_object(self, basic_instance):
        """Test that deepcopy creates a new Basic object."""
        deep_copied_obj = copy.deepcopy(basic_instance)
        assert deep_copied_obj is not basic_instance

    def test_deepcopy_delegates_to_copy_method(self, mocker, basic_instance):
        """Tests that deepcopy() correctly calls the object's copy method."""
        mocker.patch.object(Basic, "copy", return_value=basic_instance.copy())
        copy.deepcopy(basic_instance)
        Basic.copy.assert_called_once()

    
    # ---- getName ----
    def test_getName_returns_identifier_when_no_number(self, basic_instance):
        """Tests that getName() returns the identifier when number is None."""
        assert basic_instance.getName() == "test_basic"

    def test_getName_returns_formatted_name_with_number(self, basic_instance):
        """Tests that getName() returns a formatted name when a number is set."""
        basic_instance.number = 99
        assert basic_instance.getName() == "test_basic_99"


    # ---- __repr__ ----
    def test_repr_includes_all_key_attributes(self, basic_instance):
        """Tests that the __repr__ string includes all key attributes."""
        expected_repr = (
            "Basic(identifier='test_basic', sequence=0, "
            "source_interval=(10, 20), element_type='ASSERT_ELEMENT', "
            "number=None)"
        )
        assert repr(basic_instance) == expected_repr

    def test_repr_handles_none_number_correctly(self, basic_instance):
        """Tests that the __repr__ method correctly represents a None number."""
        basic_instance.number = None
        expected_repr = (
            "Basic(identifier='test_basic', sequence=0, "
            "source_interval=(10, 20), element_type='ASSERT_ELEMENT', "
            "number=None)"
        )
        assert repr(basic_instance) == expected_repr


# -------------------
# Tests for BasicArray
# -------------------
class TestBasicArray:
    """Tests for the BasicArray class."""

    # ---- Initialization ----
    def test_init_creates_empty_list(self, basic_array_instance):
        """Tests that a new BasicArray instance has an empty elements list."""
        assert basic_array_instance.elements == []

    def test_init_sets_default_element_type(self, basic_array_instance):
        """Tests that the default element type is correctly set to Basic."""
        assert basic_array_instance.element_type == Basic

    
    # ---- __len__, __iter__, __getitem__ ----
    def test_len_returns_correct_count(self, filled_basic_array):
        """Tests that the __len__ method returns the correct number of elements."""
        assert len(filled_basic_array) == 3

    def test_len_returns_zero_for_empty_array(self, basic_array_instance):
        """Tests that the __len__ method returns zero for an empty BasicArray."""
        assert len(basic_array_instance) == 0

    def test_iter_allows_iteration(self, filled_basic_array):
        """Tests that the BasicArray is iterable."""
        identifiers = [elem.identifier for elem in filled_basic_array]
        assert identifiers == ["elem1", "elem2", "elem3"]

    def test_getitem_accesses_element_by_index(self, filled_basic_array):
        """Tests that __getitem__ correctly accesses elements by index."""
        assert filled_basic_array[0].identifier == "elem1"

    
    # ---- addElement ----
    def test_addElement_adds_element_to_list(self, basic_array_instance):
        """Tests that addElement() correctly adds a new element to the list."""
        element = Basic("new_elem")
        basic_array_instance.addElement(element)
        assert len(basic_array_instance) == 1
        assert basic_array_instance[0] is element

    def test_addElement_returns_correct_index(self, basic_array_instance):
        """Tests that addElement() returns the correct index of the new element."""
        element = Basic("new_elem")
        index = basic_array_instance.addElement(element)
        assert index == 0

    def test_addElement_warns_on_type_mismatch(self, basic_array_instance):
        """Tests that a warning is logged when adding an element of an incorrect type."""
        mock_logger = MagicMock()
        basic_array_instance.logger = mock_logger
        basic_array_instance.element_type = ElementsTypes
        mismatched_element = "not a Basic object"
        basic_array_instance.addElement(mismatched_element)
        mock_logger.warning.assert_called_once()
        assert "Object should be of type ElementsTypes" in mock_logger.warning.call_args[0][0]

    
     # ---- checkSourceInteval ----
    def test_checkSourceInteval_returns_false_if_contained(
        self, filled_basic_array, mocker
    ):
        """Tests that checkSourceInteval() returns False if the interval is contained."""
        mocker.patch.object(
            filled_basic_array.utils, "is_interval_contained", return_value=True
        )
        # Mock is_interval_contained to always return True to simulate a match
        assert filled_basic_array.checkSourceInteval((1, 2)) is False

    def test_checkSourceInteval_returns_true_if_not_contained(
        self, filled_basic_array, mocker
    ):
        """Tests that checkSourceInteval() returns True if the interval is not contained."""
        mocker.patch.object(
            filled_basic_array.utils, "is_interval_contained", return_value=False
        )
        assert filled_basic_array.checkSourceInteval((1, 2)) is True

    
    # ---- Copy & deepcopy ----
    def test_copy_creates_new_BasicArray_object(self, filled_basic_array):
        """Tests that the copy() method returns a new BasicArray instance."""
        copied_array = filled_basic_array.copy()
        assert copied_array is not filled_basic_array

    def test_copy_creates_shallow_copies_of_elements(self, filled_basic_array):
        """Tests that the copy() method creates new instances for each element."""
        copied_array = filled_basic_array.copy()
        assert len(copied_array) == len(filled_basic_array)
        assert copied_array[0] is not filled_basic_array[0]

    def test_deepcopy_creates_new_BasicArray_object(self, filled_basic_array):
        """Tests that deepcopy() returns a new BasicArray instance."""
        deep_copied_array = copy.deepcopy(filled_basic_array)
        assert deep_copied_array is not filled_basic_array

    def test_deepcopy_creates_deep_copies_of_elements(self, filled_basic_array):
        """Tests that deepcopy() creates new instances for each element."""
        deep_copied_array = copy.deepcopy(filled_basic_array)
        assert len(deep_copied_array) == len(filled_basic_array)
        assert deep_copied_array[0] is not filled_basic_array[0]

    
    # ---- reverse & reverse_copy ----
    def test_reverse_modifies_array_in_place(self, filled_basic_array):
        """Tests that the reverse() method modifies the array in place."""
        original_order = [e.identifier for e in filled_basic_array]
        filled_basic_array.reverse()
        reversed_order = [e.identifier for e in filled_basic_array]
        assert reversed_order == ["elem3", "elem2", "elem1"]
        assert original_order != reversed_order

    def test_reverse_copy_returns_new_array_with_reversed_elements(
        self, filled_basic_array
    ):
        """Tests that reverse_copy() returns a new reversed array without modifying the original."""
        original_order_before = [e.identifier for e in filled_basic_array]
        reversed_copy = filled_basic_array.reverse_copy()
        original_order_after = [e.identifier for e in filled_basic_array]
        reversed_order = [e.identifier for e in reversed_copy]

        assert reversed_order == ["elem3", "elem2", "elem1"]
        assert original_order_before == original_order_after

    
    # ---- insert ----
    def test_insert_adds_element_at_specified_index(self, basic_array_instance):
        """Tests that insert() adds an element at the correct index."""
        basic_array_instance.addElement(Basic("first"))
        basic_array_instance.addElement(Basic("third"))
        new_element = Basic("second")
        basic_array_instance.insert(1, new_element)
        assert basic_array_instance[1] is new_element

    def test_insert_allows_out_of_range_index(self, basic_array_instance):
        """Negative test: inserting at out-of-range index appends to the end (Python list behavior)."""
        basic_array_instance.addElement(Basic("only"))
        new_elem = Basic("appended")
        basic_array_instance.insert(99, new_elem)
        assert basic_array_instance[-1] is new_elem

    
    # ---- getElementsIE ----
    def test_getElementsIE_with_no_filters_returns_copy(self, filled_basic_array):
        """Tests that getElementsIE() returns a copy of the elements when no filters are used."""
        filtered_array = filled_basic_array.getElementsIE()
        assert filtered_array is not filled_basic_array
        assert len(filtered_array) == len(filled_basic_array)
        assert filtered_array[0] is not filled_basic_array[0]

    def test_getElementsIE_includes_by_element_type(self, filled_basic_array):
        """Tests that getElementsIE() can filter by including a specific element type."""
        filtered_array = filled_basic_array.getElementsIE(
            include=ElementsTypes.ASSERT_ELEMENT
        )
        assert len(filtered_array) == 2
        assert all(
            e.element_type == ElementsTypes.ASSERT_ELEMENT for e in filtered_array
        )

    def test_getElementsIE_excludes_by_element_type(self, filled_basic_array):
        """Tests that getElementsIE() can filter by excluding a specific element type."""
        filtered_array = filled_basic_array.getElementsIE(
            exclude=ElementsTypes.ASSERT_ELEMENT
        )
        assert len(filtered_array) == 1
        assert filtered_array[0].element_type == ElementsTypes.IF_STATEMENT_ELEMENT

    def test_getElementsIE_includes_by_identifier(self, filled_basic_array):
        """Tests that getElementsIE() can filter by including a specific identifier."""
        filtered_array = filled_basic_array.getElementsIE(include_identifier="elem2")
        assert len(filtered_array) == 1
        assert filtered_array[0].identifier == "elem2"

    def test_getElementsIE_excludes_by_identifier(self, filled_basic_array):
        """Tests that getElementsIE() can filter by excluding a specific identifier."""
        filtered_array = filled_basic_array.getElementsIE(
            exclude_identifier="elem2"
        )
        assert len(filtered_array) == 2
        assert all(e.identifier != "elem2" for e in filtered_array)

    def test_getElementsIE_combines_filters(self, filled_basic_array):
        """Tests that getElementsIE() can combine both include and exclude filters."""
        filtered_array = filled_basic_array.getElementsIE(
            include=ElementsTypes.ASSERT_ELEMENT, exclude_identifier="elem3"
        )
        assert len(filtered_array) == 1
        assert filtered_array[0].identifier == "elem1"

    
    # ---- Operator overloading (+=) ----
    def test_iadd_adds_another_BasicArray(self):
        """Tests that the += operator correctly adds another BasicArray's elements."""
        array1 = BasicArray()
        array1.addElement(Basic("one"))
        array2 = BasicArray()
        array2.addElement(Basic("two"))

        array1 += array2
        assert len(array1) == 2
        assert array1[1].identifier == "two"

    def test_iadd_adds_single_Basic_element(self):
        """Tests that the += operator correctly adds a single Basic element."""
        array = BasicArray()
        array += Basic("single_elem")
        assert len(array) == 1
        assert array[0].identifier == "single_elem"

    def test_iadd_raises_TypeError_for_invalid_type(self, basic_array_instance):
        """Tests that the += operator raises TypeError for invalid types."""
        with pytest.raises(TypeError):
            basic_array_instance += "invalid"

    
    # ---- Element lookup ----
    def test_getElement_returns_correct_element(self, filled_basic_array):
        """Tests that getElement() returns the correct element by its identifier."""
        element = filled_basic_array.getElement("elem2")
        assert element is filled_basic_array[1]

    def test_getElement_returns_none_if_not_found(self, filled_basic_array):
        """Tests that getElement() returns None if the identifier is not found."""
        element = filled_basic_array.getElement("non_existent")
        assert element is None

    def test_getElementIndex_returns_correct_index(self, filled_basic_array):
        """Tests that getElementIndex() returns the correct index for a given identifier."""
        index = filled_basic_array.getElementIndex("elem2")
        assert index == 1

    def test_getElementIndex_returns_none_if_not_found(self, filled_basic_array):
        """Tests that getElementIndex() returns None if the identifier is not found."""
        index = filled_basic_array.getElementIndex("non_existent")
        assert index is None

    def test_getElementByIndex_returns_correct_element(self, filled_basic_array):
        """Tests that getElementByIndex() returns the correct element by index."""
        element = filled_basic_array.getElementByIndex(0)
        assert element is filled_basic_array[0]

    def test_getLastElement_returns_last_element(self, filled_basic_array):
        """Tests that getLastElement() returns the last element in the array."""
        last_element = filled_basic_array.getLastElement()
        assert last_element.identifier == "elem3"

    def test_getLastElement_returns_none_for_empty_array(self, basic_array_instance):
        """Tests that getLastElement() returns None for an empty BasicArray."""
        assert basic_array_instance.getLastElement() is None

    
    # --- Element removal ----
    def test_removeElement_removes_correct_element(self, filled_basic_array):
        """Tests that removeElement() removes the specified element from the array."""
        element_to_remove = filled_basic_array[1]
        filled_basic_array.removeElement(element_to_remove)
        assert len(filled_basic_array) == 2
        assert "elem2" not in [e.identifier for e in filled_basic_array]

    def test_removeElementByIndex_removes_element_at_index(self, filled_basic_array):
        """Tests that removeElementByIndex() removes the element at the specified index."""
        filled_basic_array.removeElementByIndex(1)
        assert len(filled_basic_array) == 2
        assert "elem2" not in [e.identifier for e in filled_basic_array]

    def test_removeElementByIndex_handles_invalid_index(self, filled_basic_array):
        """Tests that removeElementByIndex() does not modify the array for an invalid index."""
        original_len = len(filled_basic_array)
        filled_basic_array.removeElementByIndex(99)
        assert len(filled_basic_array) == original_len

    
    # ---- getElements & __repr__ ----
    def test_getElements_returns_elements_list(self, filled_basic_array):
        """Tests that getElements() returns the internal elements list."""
        elements_list = filled_basic_array.getElements()
        assert isinstance(elements_list, list)
        assert len(elements_list) == 3

    def test_repr_includes_type_and_count(self, filled_basic_array):
        """Tests that the __repr__ string includes the array's type and element count."""
        repr_str = repr(filled_basic_array)
        assert "BasicArray(element_type=Basic, count=3)" in repr_str

    def test_repr_includes_element_representations(self, filled_basic_array):
        """Tests that the __repr__ string includes the representations of its elements."""
        repr_str = repr(filled_basic_array)
        assert "identifier='elem1'" in repr_str
        assert "identifier='elem2'" in repr_str
        assert "identifier='elem3'" in repr_str