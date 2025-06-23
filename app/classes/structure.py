from typing import TYPE_CHECKING, Any, Optional, Tuple, List, Union

from ..utils.counters import CounterTypes
from ..classes.parametrs import ParametrArray
from ..classes.basic import Basic, BasicArray
from ..classes.protocols import BodyElement, Protocol
from ..classes.element_types import ElementsTypes


class Structure(Basic):
    """
    Represents a structural block or scope within a larger design,
    such as a Verilog 'always' block, 'initial' block, 'task', 'function',
    or a design_unit-level construct. It can encapsulate a sequence of
    behaviors (Protocols or nested Structures) and manage its own parameters.

    It extends the `Basic` class for fundamental identification and source tracking.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        """
        Initializes a new `Structure` instance.

        Args:
            identifier (str): The name of the structure (e.g., "always_comb", "my_task", "initial").
            source_interval (Tuple[int, int]): A tuple (start_position, end_position)
                                                indicating where this structure appears
                                                in the original source file.
            element_type (ElementsTypes, optional): The classification of this structure's type
                                                    (e.g., ALWAYS_BLOCK, TASK_BLOCK, INITIAL_BLOCK).
                                                    Defaults to `ElementsTypes.NONE_ELEMENT`.
            name_space_level (int, optional): An integer indicating the hierarchical level or
                                             namespace depth of this structure. Used for unique naming.
                                             Defaults to 0.
        """
        super().__init__(identifier, source_interval, element_type)

        # `behavior` holds a list of Protocol or nested Structure objects
        # that define the actions or sub-blocks within this structure.
        self.behavior: List[Union["Protocol", "Structure"]] = []

        # `elements` seems to be a generic BasicArray for other contained basic elements.
        # Its specific use within Structure might need more context, but keeping it as-is for now.
        self.elements: "BasicArray" = BasicArray(Basic)

        # `parametrs` stores parameters directly associated with this structure itself.
        self.parametrs: "ParametrArray" = ParametrArray()

        # `additional_params` stores a raw string of parameters,
        # potentially used for specialized cases where structured ParametrArray isn't desired.
        self.additional_params: Optional[str] = None

        # `number` is set from `name_space_level` and can be updated by `setNumber`.
        # It's used for unique naming in `getName`.
        self.number: int = self.counters.get(self.counters.types.STRUCT_COUNTER)
        self.counters.incriese(self.counters.types.STRUCT_COUNTER)

        # `inside_the_task` flag influences how parameters are handled when adding new protocols.
        self.inside_the_task: bool = False

        # Assuming `self.counters` is an attribute (e.g., a dictionary or object)
        # that manages counters of different types (e.g., for unique naming).
        # It needs to be initialized if used by `addInitProtocol`.
        # self.counters: Any = {} # Placeholder if not inherited/passed

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "Structure":
        """
        Creates a deep copy of the current `Structure` instance.
        It ensures that all mutable nested objects (`behavior`, `elements`, `parametrs`)
        are also deep-copied to maintain independence.

        Returns:
            Structure: A new `Structure` object with copied attributes and nested structures.
        """
        new_structure = Structure(
            self.identifier,
            self.source_interval,
            self.element_type,
            self.number,  # Initialize with current number
        )

        # Deep copy the `behavior` list and its contents
        for element in self.behavior:
            # Assumes both Protocol and Structure classes have a .copy() method
            new_structure.behavior.append(element.copy())

        # Deep copy `elements` and `parametrs`
        new_structure.elements = self.elements.copy()
        new_structure.parametrs = self.parametrs.copy()

        # Copy other attributes
        new_structure.additional_params = self.additional_params
        new_structure.inside_the_task = self.inside_the_task  # Also copy this flag

        return new_structure

    def addBodyElement(self, body_element: "BodyElement") -> None:
        """
        Adds a `BodyElement` to the *last* `Protocol` or `Structure` within this
        Structure's `behavior` list. This implies a nesting behavior where the
        current structure acts as a container for protocols/sub-structures,
        and `BodyElement`s are the lowest-level operations within those.

        Args:
            body_element (BodyElement): The `BodyElement` to be added.
        """
        if self.behavior:  # Ensure there is at least one behavior element to add to
            # The last element in `behavior` is assumed to be a Protocol or Structure
            # that has an `addBodyElement` method.
            # This implicitly assumes a specific hierarchy where a BodyElement
            # always belongs inside a Protocol or a nested Structure that also
            # exposes an `addBodyElement` method.
            self.behavior[-1].addBodyElement(body_element)
        else:
            # Consider logging a warning or raising an error if a BodyElement
            # is added when there's no existing behavior to attach it to.
            # print(f"Warning: Cannot add BodyElement to empty behavior list in Structure '{self.identifier}'")
            pass

    def updateLinks(self, design_unit: Any) -> None:
        """
        Cascades the link-updating process to all contained `Protocol` and
        `Structure` objects within this instance's `behavior` list.
        This is crucial for resolving symbolic references to actual objects
        throughout the design_unit's hierarchy.

        Args:
            design_unit (Any): An object representing the design_unit, passed down to
                          the nested elements' `updateLinks` methods.
        """
        for element in self.behavior:
            # Assumes all elements in `self.behavior` have an `updateLinks` method.
            element.updateLinks(design_unit)

    def getName(self, include_params: bool = True) -> str:
        """
        Generates a formatted name for the structure. It can include a numeric
        suffix (from `self.number`) and a parenthesized list of parameters
        (either `additional_params` string or formatted `parametrs`).

        Args:
            include_params (bool, optional): If True, parameters will be included
                                             in the generated name. Defaults to True.

        Returns:
            str: The formatted name string for the structure.
                 Examples: "my_always_block", "my_task_1", "my_function(arg1, arg2)".
        """
        display_identifier = self.identifier

        # Append numeric suffix if 'number' is set and non-zero
        if self.number:  # Checks for truthiness (0 would be False)
            display_identifier = f"{display_identifier}_{self.number}"

        if include_params:
            if self.additional_params is not None:
                # Use raw string if additional_params is provided
                display_identifier = f"{display_identifier}({self.additional_params})"
            elif self.parametrs and len(self.parametrs) > 0:
                # Otherwise, format from ParametrArray if it has elements
                display_identifier = f"{display_identifier}({str(self.parametrs)})"
        return display_identifier

    def getLastBehaviorIndex(self) -> Optional[Union["Protocol", "Structure"]]:
        """
        Retrieves the last `Protocol` or `Structure` object added to this
        Structure's `behavior` list.

        Returns:
            Optional[Union[Protocol, Structure]]: The last behavior element, or None if the list is empty.
        """
        beh_len = len(self.behavior)
        if beh_len <= 0:
            return None
        return beh_len - 1

    def insertBehavior(
        self, index: int, element: Union["Protocol", "Structure"]
    ) -> None:
        """
        Inserts a `Protocol` or `Structure` object into the `behavior` list
        at a specific index.

        Args:
            index (int): The zero-based index at which to insert the element.
            element (Union[Protocol, Structure]): The `Protocol` or `Structure` object to insert.
        """
        self.behavior.insert(index, element)

    def addProtocol(
        self,
        protocol_identifier: str,
        element_type: Optional[ElementsTypes] = None,
        parametrs: Optional["ParametrArray"] = None,
        inside_the_task: bool = False,
    ) -> int:
        """
        Creates and adds a new `Protocol` object to this Structure's `behavior` list.
        The parameters for the new protocol are determined by a combination of
        this Structure's parameters and the explicitly passed parameters,
        influenced by the `inside_the_task` flag.

        Args:
            protocol_identifier (str): The identifier for the new protocol.
            element_type (Optional[ElementsTypes]): The type of the new protocol. Defaults to None.
            parametrs (Optional[ParametrArray]): Additional parameters for the new protocol.
                                                  Defaults to None.
            inside_the_task (bool, optional): If True, only the explicitly passed `parametrs`
                                              are used for the new protocol. If False,
                                              this Structure's `parametrs` are combined with
                                              the passed `parametrs`. Defaults to False.

        Returns:
            int: The index of the newly added protocol in the `behavior` list.
        """
        final_protocol_params: "ParametrArray" = ParametrArray()

        if not inside_the_task:
            # If not inside a task, combine structure's parameters with new parameters
            if self.parametrs:  # Check if structure has parameters
                final_protocol_params += self.parametrs
            if parametrs:  # Check if new parameters were passed
                final_protocol_params += parametrs
        else:
            # If inside a task, only use the explicitly passed parameters
            if parametrs:
                final_protocol_params = parametrs

        # Create and append the new Protocol
        # Note: source_interval is hardcoded to (0,0) for the new Protocol
        new_protocol = Protocol(
            protocol_identifier,
            (0, 0),  # Default source interval for newly created protocol
            element_type,
            final_protocol_params,
        )
        self.behavior.append(new_protocol)
        return len(self.behavior) - 1

    def addInitProtocol(
        self, counter_type: "CounterTypes" = CounterTypes.STRUCT_COUNTER
    ) -> None:
        """
        Adds a specific "initialization" protocol to this structure's behavior.
        The identifier for this init protocol is derived from the structure's
        identifier and a value obtained from a counter system.

        Args:
            counter_type (CounterTypes, optional): The type of counter to use
                                                   for generating a unique number.
                                                   Defaults to `CounterTypes.STRUCT_COUNTER`.
        """
        # Ensure `self.counters` is available and has a `get` method.
        if not hasattr(self, "counters") or self.counters is None:
            # Consider logging a warning or raising an error
            self.logger.warning(
                f"'counters' attribute not initialized in Structure '{self.identifier}'. Cannot add Init Protocol."
            )
            return

        counter_value = self.counters.get(counter_type)
        if counter_value is None:
            # Handle case where counter_type might not be found
            self.logger.warning(
                f"Warning: Counter type '{counter_type.name}' not found for Structure '{self.identifier}'."
            )
            return

        self.addProtocol(
            protocol_identifier=f"{self.identifier}_{counter_value}",
            element_type=self.element_type,  # Use the structure's element type for the protocol
            parametrs=self.parametrs,  # Use the structure's parameters for the protocol
            inside_the_task=self.inside_the_task,
        )

    def getBehLen(self) -> int:
        """
        Returns the number of elements (Protocols or Structures) currently
        in this Structure's `behavior` list.

        Returns:
            int: The count of behavior elements.
        """
        return len(self.behavior)

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `Structure`'s behavior.
        It concatenates the string representation of all contained `Protocol`
        and `Structure` objects, each on a new line.

        Returns:
            str: The multi-line string representation of the structure's behavior.
        """
        result_parts: List[str] = []
        for element in self.behavior:
            result_parts.append(str(element))

        # Join with newlines. Using .strip() at the very end to ensure no trailing newline
        # if the list is empty or last element also provides a newline.
        return "\n".join(result_parts).strip()

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `Structure` object,
        displaying its key attributes for debugging and introspection.
        Includes the number suffix if present.
        """
        if self.number:  # Check if number is non-zero
            return (
                f"Structure("
                f"identifier='{self.identifier}_{self.number!r}', "  # Number included in identifier string
                f"source_interval={self.source_interval!r}, "
                f"element_type={self.element_type!r}, "
                f"name_space_level={self.number!r}, "  # Use `self.number` which holds name_space_level
                f"behavior={self.behavior!r}, "
                f"elements={self.elements!r}, "
                f"parametrs={self.parametrs!r}, "
                f"additional_params={self.additional_params!r}, "
                f"inside_the_task={self.inside_the_task!r}"
                f")"
            )
        else:
            return (
                f"Structure("
                f"identifier={self.identifier!r}, "
                f"source_interval={self.source_interval!r}, "
                f"element_type={self.element_type!r}, "
                f"name_space_level={self.number!r}, "  # Use self.number
                f"behavior={self.behavior!r}, "
                f"elements={self.elements!r}, "
                f"parametrs={self.parametrs!r}, "
                f"additional_params={self.additional_params!r}, "
                f"inside_the_task={self.inside_the_task!r}"
                f")"
            )


class StructureArray(BasicArray):
    """
    A specialized array for managing a collection of `Structure` objects.
    This class extends `BasicArray` and provides methods for adding, filtering,
    deep copying, and generating various string representations of the contained structures.
    It also offers specific filters to retrieve 'Always' blocks or other non-Always structures.
    """

    def __init__(self):
        """
        Initializes a new `StructureArray` instance, specifically configured
        to store objects of type `Structure`.
        """
        super().__init__(Structure)  # Configure BasicArray to hold Structure objects

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "StructureArray":
        """
        Creates a deep copy of the current `StructureArray` instance.
        It iterates through all contained `Structure` objects and adds their
        deep copies to the new array, ensuring full independence of the copied structures.

        Returns:
            StructureArray: A new `StructureArray` containing deep copies of all
                            original structures.
        """
        new_array = StructureArray()
        for element in self.elements:  # Iterate directly over the internal list
            new_array.addElement(element.copy())  # Use Structure's deep copy method
        return new_array

    def addElement(self, new_element: "Structure") -> Tuple[bool, int]:
        """
        Adds a new `Structure` element to the array.
        This method overrides the base `BasicArray.addElement` to include
        a check for uniqueness based on the element's identifier.

        Args:
            new_element (Structure): The `Structure` object to add.

        Returns:
            Tuple[bool, int]: A tuple where:
                              - The first element (bool) is True if the element was added,
                                False if an element with the same identifier already exists.
                              - The second element (int) is the index of the added or
                                existing element.

        Raises:
            TypeError: If the `new_element` is not an instance of `Structure`.
        """
        # Type validation: Ensure the element is of the expected type.
        if not isinstance(new_element, self.element_type):
            raise TypeError(
                f"Object should be of type {self.element_type.__name__} but "
                f"you passed an object of type {type(new_element).__name__}. "
                f"Object: {new_element!r}"  # Use !r for better representation in error message
            )

        # Check for uniqueness: Prevent adding structures with duplicate identifiers.
        existing_element = self.getElement(new_element.identifier)
        if existing_element is not None:
            # If an element with the same identifier exists, return False and its index.
            return (False, self.getElementIndex(existing_element.identifier))

        # If unique, add the element and return True with its new index.
        self.elements.append(new_element)
        return (True, len(self.elements) - 1)  # Directly return the last index

    def getElementsIE(
        self,
        include_type: Optional["ElementsTypes"] = None,
        exclude_type: Optional["ElementsTypes"] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
    ) -> "StructureArray":
        """
        Filters the structures in the array based on their `element_type`
        and/or `identifier`. This method allows for both inclusion and exclusion criteria.

        Args:
            include_type (Optional[ElementsTypes]): Only include structures with this element type.
            exclude_type (Optional[ElementsTypes]): Exclude structures with this element type.
            include_identifier (Optional[str]): Only include structures with this identifier.
            exclude_identifier (Optional[str]): Exclude structures with this identifier.

        Returns:
            StructureArray: A new `StructureArray` containing only the structures that
                            match the specified filtering criteria. If no criteria are
                            provided, a deep copy of the original array is returned.
        """
        result_array: "StructureArray" = StructureArray()

        # If no filters are specified, return a deep copy of the entire array.
        if (
            include_type is None
            and exclude_type is None
            and include_identifier is None
            and exclude_identifier is None
        ):
            return self.copy()

        for element in self.elements:  # Iterate directly over the internal list
            # Apply inclusion/exclusion filters for element_type
            if include_type is not None and element.element_type is not include_type:
                continue  # Skip if type doesn't match inclusion
            if exclude_type is not None and element.element_type is exclude_type:
                continue  # Skip if type matches exclusion

            # Apply inclusion/exclusion filters for identifier
            # Using `==` for string content comparison, not `is` for object identity.
            if (
                include_identifier is not None
                and element.identifier != include_identifier
            ):
                continue  # Skip if identifier doesn't match inclusion
            if (
                exclude_identifier is not None
                and element.identifier == exclude_identifier
            ):
                continue  # Skip if identifier matches exclusion

            result_array.addElement(element)  # Add the element if it passes all filters

        return result_array

    def updateLinks(self, design_unit: Any) -> None:
        """
        Calls the `updateLinks` method for each `Structure` object within this array.
        This cascades the link-updating process down to the individual structures
        and their contained elements.

        Args:
            design_unit (Any): An object representing a design_unit, passed down to each
                          structure's `updateLinks` method.
        """
        for element in self.elements:  # Iterate directly over the internal list
            element.updateLinks(design_unit)

    def getAlwaysList(self):
        from ..classes.always import Always

        """
        Retrieves a list of `Always` block structures from the array.
        It filters for elements that are instances of `Always` and contain
        at least one behavior element.

        Returns:
            List[Always]: A list of `Always` block instances.
        """

        result: List["Always"] = []
        for element in self.elements:
            # Check if the element is an instance of 'Always' and has content in its behavior.
            # Assuming 'Always' is a subclass of 'Structure' or has a 'behavior' attribute.
            if isinstance(element, Always) and len(element.behavior) >= 1:
                result.append(element)
        return result

    def getNoAlwaysStructures(self) -> List["Structure"]:
        from ..classes.always import Always

        """
        Retrieves a list of `Structure` objects that are NOT `Always` blocks
        and are NOT of type `ElementsTypes.TASK_ELEMENT`, but still contain
        at least one behavior element.

        Returns:
            List[Structure]: A list of non-Always, non-Task `Structure` instances with behavior.
        """
        result: List["Structure"] = []
        for element in self.elements:
            # Filters out 'Always' instances and 'TASK_ELEMENT' types,
            # and only includes structures that have content in their behavior.
            if (
                not isinstance(element, Always)
                and element.element_type is not ElementsTypes.TASK_ELEMENT
                and len(element.behavior) >= 1
            ):
                result.append(element)
        return result

    def getLastElement(self) -> Optional["Structure"]:
        """
        Retrieves the last `Structure` object added to the array.

        Returns:
            Optional[Structure]: The last `Structure` element in the array,
                                 or None if the array is empty.
        """
        if self.elements:  # Check if the list is not empty
            return self.elements[-1]
        else:
            return None

    def getStructuresInStrFormat(self) -> str:
        """
        Generates a combined string representation of all `Structure` objects
        in the array. Each structure's string representation (`__str__` method)
        is placed on a new line.

        Returns:
            str: A multi-line string with all structures formatted.
        """
        result_parts: List[str] = []
        for element in self.elements:
            result_parts.append(str(element))

        # Join with newlines and remove any leading/trailing whitespace (including newlines)
        return "\n".join(result_parts).strip()

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `StructureArray`,
        showing its elements, each on a new line.
        """
        return self.getStructuresInStrFormat()  # Delegate to the formatting method

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `StructureArray` object,
        displaying the `repr` of its internal elements list.
        """
        return f"StructuresArray(\n{self.elements!r}\n)"

    # Add standard container methods for better usability and Pythonic behavior
    def __len__(self) -> int:
        """Returns the number of elements in the array. Enables `len(instance)`."""
        return len(self.elements)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union["Structure", List["Structure"]]:
        """Allows direct indexing and slicing of the array, e.g., `array[0]` or `array[1:3]`."""
        return self.elements[index]

    def __iter__(self):
        """Makes the array iterable, allowing `for element in array_instance:`."""
        return iter(self.elements)
