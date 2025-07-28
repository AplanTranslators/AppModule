import re
from typing import Any, Optional, Tuple, List, Union
from ..classes.parametrs import ParametrArray
from ..classes.basic import Basic, BasicArray

from ..classes.element_types import ElementsTypes


class BodyElement(Basic):
    """
    Represents a single element within a 'body' or sequence of operations/statements.
    This could be a function call, a statement, or a structural element in a control flow.

    It extends the `Basic` class to inherit fundamental properties like `identifier`,
    `source_interval`, and `element_type`.
    """

    def __init__(
        self,
        identifier: str,
        pointer_to_related: Optional[
            Union[Basic, "BodyElementArray"]
        ] = None,  # Can point to another Basic object or a nested BodyElementArray
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        parametrs: Optional[
            ParametrArray
        ] = None,  # Made optional, default to new instance in body
    ):
        """
        Initializes a new `BodyElement` instance.

        Args:
            identifier (str): The primary name or description of the body element
                              (e.g., "always_ff", "assert", "my_function_call").
            pointer_to_related (Optional[Union[Basic, BodyElementArray]]): A reference to another
                                                                         `Basic` object or a `BodyElementArray`
                                                                         that this element is related to.
                                                                         This is often used for nesting (e.g.,
                                                                         a function call's arguments, or a block's content).
                                                                         Defaults to None.
            element_type (ElementsTypes, optional): The classification of this element's type
                                                    (e.g., FUNCTION_CALL, STATEMENT, FOREVER_ELEMENT).
                                                    Defaults to `ElementsTypes.NONE_ELEMENT`.
            parametrs (Optional[ParametrArray], optional): A collection of `Parametr` objects
                                                          associated with this body element (e.g., function arguments).
                                                          Defaults to an empty `ParametrArray`.
        """
        super().__init__(
            identifier, (0, 0), element_type
        )  # Source interval set to (0,0) by default in Basic
        self.parametrs: ParametrArray = (
            parametrs if parametrs is not None else ParametrArray()
        )
        self.pointer_to_related: Optional[Union[Basic, "BodyElementArray"]] = (
            pointer_to_related
        )

    def copy(self) -> "BodyElement":
        """
        Creates a deep copy of the current `BodyElement` instance.
        It ensures that mutable attributes like `parametrs` are also copied,
        preventing unintended side effects when modifying the copy.

        Returns:
            BodyElement: A new `BodyElement` object with copied attributes.
        """
        # Deep copy `parametrs` to ensure independence of the copied object
        copied_parametrs = self.parametrs.copy() if self.parametrs else ParametrArray()

        # If `pointer_to_related` can also be mutable and needs deep copying,
        # its copying logic would be more complex (e.g., checking its type and calling its .copy() method).
        # For now, assuming Basic and BodyElementArray's copy methods handle their internal state.
        copied_pointer_to_related: Optional[Union[Basic, "BodyElementArray"]] = None
        if self.pointer_to_related:
            if isinstance(self.pointer_to_related, Basic):
                # Assuming Basic has a copy method. If not, consider what needs to be copied.
                copied_pointer_to_related = self.pointer_to_related.copy()
            elif isinstance(self.pointer_to_related, BodyElementArray):
                copied_pointer_to_related = self.pointer_to_related.copy()
            # Add other specific types if pointer_to_related can point to them and they need deep copies

        element = BodyElement(
            self.identifier,
            copied_pointer_to_related,
            self.element_type,
            copied_parametrs,
        )
        # Any other unique attributes should be copied here if not passed to constructor
        # E.g., element.some_other_attribute = self.some_other_attribute
        return element

    def getName(self) -> str:
        """
        Generates a formatted name for the body element.
        If the element has associated parameters, it formats them as a function call.

        Returns:
            str: The formatted name string for the body element.
        """
        if self.parametrs and len(self.parametrs) > 0:
            # Format as "identifier(param1, param2)"
            return f"{self.identifier}({str(self.parametrs)})"
        else:
            # If no parameters, just return the identifier
            return self.identifier

    def __str__(self) -> str:
        """
        Returns the formatted name of the `BodyElement`.
        """

        return self.getName()

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `BodyElement` object,
        displaying its key attributes for debugging and introspection.
        """
        return (
            f"BodyElement("
            f"identifier={self.identifier!r}, "
            f"element_type={self.element_type!r}, "
            f"parametrs={self.parametrs!r}, "
            f"pointer_to_related={self.pointer_to_related!r}"
            f")"
        )


class BodyElementArray(BasicArray):
    """
    A specialized array for managing a sequence of `BodyElement` objects.
    This class is typically used to represent the body of a function, a block
    of code, or a sequence of statements in an abstract syntax tree (AST).

    It provides custom logic for string representation (`toStr`) that
    reconstructs a formatted code snippet based on the element types and their relationships.
    """

    def __init__(self, element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT):
        """
        Initializes a new `BodyElementArray` instance.

        Args:
            element_type (ElementsTypes, optional): The overarching type of elements
                                                    contained in this array. This influences
                                                    how the elements are joined in `toStr`.
                                                    Defaults to `ElementsTypes.NONE_ELEMENT`.
        """
        super().__init__(
            BodyElement
        )  # Configure BasicArray to hold BodyElement objects
        self.element_type: ElementsTypes = (
            element_type  # Type of the array context (e.g., GENERATE_ELEMENT for `||` separation)
        )

    def copy(self) -> "BodyElementArray":
        """
        Creates a deep copy of the current `BodyElementArray` instance.
        It iterates through all contained `BodyElement` objects and adds their deep copies
        to the new array, preserving the array's `element_type`.

        Returns:
            BodyElementArray: A new `BodyElementArray` containing deep copies of all original elements.
        """
        # Corrected: Pass the element_type to the constructor of the new array
        new_array: BodyElementArray = BodyElementArray(self.element_type)
        for element in self.elements:  # Access self.elements directly
            new_array.addElement(element.copy())  # Use BodyElement's copy method
        # self.element_type is already copied via constructor, no need for new_array.element_type = self.element_type
        return new_array

    def getElementByIndex(self, index: int) -> BodyElement:
        """
        Retrieves a `BodyElement` object from the array by its index.

        Args:
            index (int): The zero-based index of the desired element.

        Returns:
            BodyElement: The `BodyElement` object at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        return self.elements[index]

    def addElement(self, new_element: BodyElement) -> int:
        """
        Adds a new `BodyElement` to the array.

        Args:
            new_element (BodyElement): The `BodyElement` object to add.

        Returns:
            int: The index of the newly added element.
        """
        # BasicArray is expected to handle type checks or other validations.
        # This method directly appends. If uniqueness checks or specific ordering
        # are needed, they should be implemented here or in BasicArray.
        self.elements.append(new_element)
        return len(self.elements) - 1  # Return the index of the added element

    # Redundant methods, consider removing and using Python built-ins:
    # def getElements(self) -> List[BodyElement]:
    #     """Returns the internal list of elements. Prefer direct iteration or __getitem__."""
    #     return self.elements

    # def getLen(self) -> int:
    #     """Returns the number of elements. Prefer `len(instance)`."""
    #     return len(self.elements)

    def __len__(self) -> int:
        """
        Returns the number of elements in the array.
        Enables `len(body_array_instance)`.
        """
        return len(self.elements)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[BodyElement, List[BodyElement]]:
        """
        Allows direct indexing and slicing of the array, e.g., `body_array[0]` or `body_array[1:3]`.
        """
        return self.elements[index]

    def __iter__(self):
        """
        Makes the array iterable, allowing `for element in body_array_instance:`.
        """
        return iter(self.elements)

    def __str__(self) -> str:
        """
        Returns the string representation of the array by calling `toStr()`.
        """
        return self.toStr()

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `BodyElementArray` object,
        displaying the `repr` of its internal elements and its `element_type`.
        """
        return (
            f"BodyElementArray("
            f"element_type={self.element_type!r}, "
            f"elements={self.elements!r}"
            f")"
        )

    def toStr(self, last_comma: bool = True) -> str:
        """
        Reconstructs a formatted string representation of the sequence of body elements.
        This method applies complex rules for adding separators, parentheses, and
        handling related/nested elements based on their `element_type`.

        Args:
            last_comma (bool, optional): If True, a trailing comma is added to the
                                         very end of the reconstructed string.
                                         Defaults to True.

        Returns:
            str: The reconstructed string representation of the body.
        """
        body_to_str_parts: List[str] = []  # Use list for efficient string building
        # This flag likely controls opening/closing of a group of elements,
        # e.g., a conditional expression group.
        # It's initially False, then set to True for IF_CONDITION_LEFT, and False for IF_CONDITION_RIGHT.
        within_parentheses_group = False

        for index, body_element in enumerate(self.elements):
            element_str = body_element.getName()
            # This flag controls if a default semicolon or specific operator should be used
            # based on element type interactions. It's an internal helper.
            # Renamed from `protocol_element` for clarity, as it seems to influence separators.
            needs_default_separator = False

            previous_body_element: Optional[BodyElement] = None
            if index > 0:
                previous_body_element = self.elements[index - 1]

            # --- Logic for adding separators between elements ---
            if index != 0:  # For all elements after the first one
                if self.element_type == ElementsTypes.GENERATE_ELEMENT:
                    # Specific separator for GENERATE blocks (e.g., Verilog generate constructs)
                    body_to_str_parts.append(" || ")
                else:
                    # General separator logic based on previous and current element types
                    if previous_body_element:  # Ensure previous_body_element exists
                        if body_element.element_type == ElementsTypes.FOREVER_ELEMENT:
                            # Semicolon before a FOREVER block (e.g., always @(posedge clk) ; begin ... end)
                            body_to_str_parts.append(";")
                        elif (
                            body_element.element_type
                            == ElementsTypes.IF_CONDITION_RIGTH
                            and previous_body_element.element_type
                            == ElementsTypes.IF_CONDITION_LEFT
                        ):
                            # Plus sign between left and right parts of an IF condition
                            # This implies a specific syntax like (condition_left + condition_right)
                            body_to_str_parts.append(" + ")
                        elif (
                            previous_body_element.element_type
                            == ElementsTypes.ACTION_ELEMENT
                            and (
                                body_element.element_type
                                == ElementsTypes.ACTION_ELEMENT
                                or body_element.element_type
                                == ElementsTypes.PROTOCOL_ELEMENT
                            )
                        ):
                            # Dot separator between consecutive ACTION or ACTION/PROTOCOL elements
                            body_to_str_parts.append(".")
                        else:
                            # Default separator: semicolon, and set flag indicating it's a 'protocol' like element
                            # or just a standard statement separator.
                            needs_default_separator = (
                                True  # This flag influences later bracket handling
                            )
                            body_to_str_parts.append(";")
                    else:  # This case for index > 0 but no previous_body_element is unreachable if self.elements is a list
                        needs_default_separator = True
                        body_to_str_parts.append(
                            ";"
                        )  # Fallback, should ideally not be hit if previous_body_element is always there.

            # --- Logic for handling `pointer_to_related` (nesting/replacement) ---
            if body_element.pointer_to_related:
                if not isinstance(body_element.pointer_to_related, BodyElementArray):
                    # If `pointer_to_related` is a single Basic object, replace its identifier in the string.
                    # This seems to be a substitution mechanism, where the identifier of the related object
                    # replaces its occurrence within the current element's string.
                    # Example: if element_str is "call(arg)" and pointer_to_related.identifier is "arg",
                    # and pointer_to_related.getName() is "some_value", it becomes "call(some_value)".
                    # Using `re.sub` for whole word matching.
                    element_str = re.sub(
                        r"\b{}\b".format(
                            re.escape(body_element.pointer_to_related.identifier)
                        ),
                        body_element.pointer_to_related.getName(),
                        element_str,
                    )
                else:
                    # If `pointer_to_related` is a nested BodyElementArray,
                    # recursively call its `toStr` method without a trailing comma.
                    element_str = body_element.pointer_to_related.toStr(
                        last_comma=False
                    )

            # --- Logic for wrapping elements with brackets or specific formatting ---
            if body_element.element_type == ElementsTypes.FOREVER_ELEMENT:
                # Elements of type FOREVER are wrapped in curly braces
                body_to_str_parts.append("{" + element_str + "}")
            elif (
                not needs_default_separator
            ):  # This means a specific separator (||, +, .) was used, or it's the first element.
                body_to_str_parts.append(element_str)
            else:  # This path is taken when `needs_default_separator` is True (e.g., after a semicolon)
                if body_element.element_type == ElementsTypes.IF_CONDITION_LEFT:
                    # Open a new group with a parenthesis for IF_CONDITION_LEFT
                    within_parentheses_group = True
                    body_to_str_parts.append("(" + element_str)
                else:
                    # Other elements after a default separator are wrapped in parentheses
                    body_to_str_parts.append("(" + element_str + ")")

            # --- Logic for closing parenthetical groups ---
            # This 'if brackets' check is redundant and potentially problematic
            # as `brackets` is not globally managed well.
            # It seems like it was intended to close the IF_CONDITION_LEFT group.
            # I'll integrate this into the `within_parentheses_group` flag.

            if (
                within_parentheses_group
                and body_element.element_type == ElementsTypes.IF_CONDITION_RIGTH
            ):
                # Close the group opened by IF_CONDITION_LEFT
                # The original code added `element_str` twice here which is likely a bug.
                # It should just close the parenthesis.
                body_to_str_parts.append(")")  # Just close the parenthesis
                within_parentheses_group = False  # Reset the flag

            # --- Logic for adding a trailing comma ---
            if index == len(self.elements) - 1 and last_comma:
                # Add a comma at the very end if it's the last element and `last_comma` is True
                body_to_str_parts.append(",")

        return "".join(body_to_str_parts)  # Join all parts into the final string


class Protocol(Basic):
    """
    Represents a 'protocol' block, which is a named entity containing a sequence
    of operations or statements (its 'body') and a set of associated parameters.
    This often corresponds to a high-level function, task, or a state machine
    description in hardware design.

    It extends the `Basic` class to inherit fundamental properties like `identifier`
    and `source_interval`.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes | None = ElementsTypes.NONE_ELEMENT,
        parametrs: Optional[
            ParametrArray
        ] = None,  # Made optional, will be initialized in the body
    ):
        """
        Initializes a new `Protocol` instance.

        Args:
            identifier (str): The name of the protocol (e.g., "read_data", "write_reg").
            source_interval (Tuple[int, int]): A tuple (start_position, end_position)
                                                indicating where this protocol appears
                                                in the original source file.
            element_type (ElementsTypes, optional): The classification of this protocol's type.
                                                    Defaults to `ElementsTypes.NONE_ELEMENT`.
            parametrs (Optional[ParametrArray], optional): A collection of `Parametr` objects
                                                          representing the inputs/outputs or
                                                          configuration parameters of this protocol.
                                                          If `None`, an empty `ParametrArray` is created.
        """
        if element_type == None:
            element_type = ElementsTypes.NONE_ELEMENT
        super().__init__(identifier, source_interval, element_type)

        # `body` stores the sequence of operations/statements within this protocol.
        self.body: BodyElementArray = BodyElementArray()

        # `parametrs` stores the formal parameters of this protocol.
        # Ensure a new instance if None is passed to avoid mutable default argument issues.
        self.parametrs: ParametrArray = (
            parametrs if parametrs is not None else ParametrArray()
        )

    def copy(self) -> "Protocol":
        """
        Creates a deep copy of the current `Protocol` instance.
        It ensures that mutable nested objects (`body` and `parametrs`) are
        also deep-copied to prevent unintended shared state.

        Returns:
            Protocol: A new `Protocol` object with copied attributes and nested structures.
        """
        # Create a new Protocol instance with basic attributes
        new_protocol = Protocol(
            self.identifier, self.source_interval, self.element_type
        )

        # Deep copy the BodyElementArray (body of the protocol)
        new_protocol.body = self.body.copy()

        # Deep copy the ParametrArray (parameters of the protocol)
        new_protocol.parametrs = self.parametrs.copy()

        # Copy the 'number' attribute if it exists
        new_protocol.number = self.number

        # If there are other attributes that are mutable objects, they should also be deep-copied.
        # Example: new_protocol.some_list = list(self.some_list)

        return new_protocol

    def addBodyElement(self, body_element: BodyElement) -> None:
        """
        Adds a `BodyElement` to the protocol's body.

        Args:
            body_element (BodyElement): The `BodyElement` to be added to this protocol's sequence of operations.
        """
        self.body.addElement(body_element)

    def getName(self) -> str:
        """
        Generates a formatted name for the protocol.
        It can include a numeric suffix (if `self.number` is set) and
        a parenthesized list of parameters (if the protocol has any).

        Returns:
            str: The formatted name string for the protocol.
                 Examples: "my_protocol", "my_protocol_1", "my_protocol(arg1, arg2)".
        """
        display_identifier = self.identifier

        # Append numeric suffix if 'number' is set
        if (
            self.number is not None
        ):  # Use `is not None` for clarity when dealing with optional numbers like 0
            display_identifier = f"{display_identifier}_{self.number}"

        # Append parameters in parentheses if they exist
        if len(self.parametrs) > 0:
            display_identifier = f"{display_identifier}({str(self.parametrs)})"

        return display_identifier

    def updateLinks(self, design_unit: Any) -> None:
        """
        Updates internal references (links) within the protocol's body.
        This method iterates through the `BodyElement`s in the protocol's `body`.
        If a `BodyElement`'s identifier corresponds to a known 'action' in the
        provided `design_unit`, it replaces the `BodyElement` with the actual 'action' object.

        This mechanism is crucial for resolving symbolic references to actual objects.

        Args:
            design_unit (Any): An object representing a design_unit, expected to have an
                          `actions` attribute (e.g., `design_unit.actions`) which is
                          a collection (like `BasicArray`) containing callable
                          'action' elements. It also needs a `utils` object
                          (e.g., `self.utils`) to extract function names.
        """
        # Ensure `self.utils` is available. This should ideally be initialized in __init__
        # or passed to the Protocol class, or inherited from Basic.
        if not hasattr(self, "utils") or self.utils is None:
            # Consider logging an error or raising an exception if utils is mandatory for this method
            self.logger.warning(
                f" 'utils' not initialized for Protocol '{self.identifier}'. Cannot update links."
            )
            return

        for index, element in enumerate(
            self.body.getElements()
        ):  # Assuming getElements() is available for BodyElementArray
            # Attempt to extract a function name from the body element's identifier
            func_name = self.utils.extractFunctionName(element.identifier)

            if func_name:  # If a function name was successfully extracted
                # Try to find the corresponding action in the design_unit's actions collection
                action = design_unit.actions.getElement(
                    func_name
                )  # Assumes design_unit.actions has getElement method

                if action:
                    # If the action is found, replace the BodyElement at this index
                    # with a tuple containing the action and its types.
                    # The original code's replacement `(action, element.element_type, element.element_type)`
                    # seems to convert a BodyElement into a tuple. This might imply a
                    # different internal representation for linked elements.
                    # This change in type (from BodyElement to Tuple) could cause issues if
                    # subsequent operations expect a BodyElement.
                    # CONSIDER: Is it better to update `element.pointer_to_related = action`
                    # or to ensure `BodyElementArray` can store heterogeneous types or a custom wrapper?
                    # For now, matching original behavior, but flagging as a potential design area.
                    self.body.elements[index] = (
                        action,  # The resolved action object
                        element.element_type,  # Original element type of the BodyElement
                        element.element_type,  # Duplicated element type; confirm if intentional or an error
                    )

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the protocol,
        showing its name and its body (sequence of operations).
        Formats as "ProtocolName = ProtocolBody".

        Returns:
            str: The string representation of the protocol.
        """

        return f"{self.getName()} = {str(self.body)}"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `Protocol` object,
        displaying its key attributes for debugging and introspection.
        """
        return (
            f"Protocol("
            f"identifier={self.identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"element_type={self.element_type!r}, "
            f"parametrs={self.parametrs!r}, "
            f"body={self.body!r}, "
            f"number={self.number!r}"
            f")"
        )


class ProtocolArray(BasicArray):
    """
    A specialized array for managing a collection of `Protocol` objects.
    This class extends `BasicArray` and provides methods for filtering,
    updating links across multiple protocols, and generating a string
    representation of all contained protocols.
    """

    def __init__(self):
        """
        Initializes a new `ProtocolArray` instance, specifically configured
        to store objects of type `Protocol`.
        """
        super().__init__(Protocol)  # Configure BasicArray to hold Protocol objects

    def copy(self) -> "ProtocolArray":
        """
        Creates a deep copy of the current `ProtocolArray` instance.
        It iterates through all contained `Protocol` objects and adds their deep copies
        to the new array, ensuring full independence.

        Returns:
            ProtocolArray: A new `ProtocolArray` containing deep copies of all original protocols.
        """
        new_array = ProtocolArray()
        for protocol_element in self.elements:  # Access self.elements directly
            new_array.addElement(
                protocol_element.copy()
            )  # Use Protocol's deep copy method
        return new_array

    def getElementsIE(
        self,
        include_type: Optional[ElementsTypes] = None,
        exclude_type: Optional[ElementsTypes] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
    ) -> "ProtocolArray":
        """
        Filters the protocols in the array based on their `element_type`
        and/or `identifier`. This method allows for both inclusion and exclusion criteria.

        Args:
            include_type (Optional[ElementsTypes]): Only include protocols with this element type.
            exclude_type (Optional[ElementsTypes]): Exclude protocols with this element type.
            include_identifier (Optional[str]): Only include protocols with this identifier.
            exclude_identifier (Optional[str]): Exclude protocols with this identifier.

        Returns:
            ProtocolArray: A new `ProtocolArray` containing only the protocols that
                           match the specified filtering criteria. If no criteria are
                           provided, a copy of the original array is returned.
        """
        result_array: ProtocolArray = ProtocolArray()

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
            # Note: `is not` and `is` for string comparison is generally not recommended
            # for content equality; use `!=` and `==`. 'is' checks for object identity.
            # Assuming 'is' was intended for literal string comparisons, but changed to '==' for safety.
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
        Calls the `updateLinks` method for each `Protocol` object within this array.
        This cascades the link-updating process down to the individual protocols
        and their bodies.

        Args:
            design_unit (Any): An object representing a design_unit, passed down to each protocol's
                          `updateLinks` method.
        """
        for element in self.elements:  # Iterate directly over the internal list
            element.updateLinks(design_unit)

    def getProtocolsInStrFormat(self) -> str:
        """
        Generates a combined string representation of all protocols in the array.
        Each protocol's string representation is placed on a new line.
        It also attempts to remove a trailing comma if present, which indicates
        a dependency on `string_formater`.

        Returns:
            str: A multi-line string with all protocols formatted.
        """
        result_parts: List[str] = []
        for element in self.elements:
            result_parts.append(
                str(element)
            )  # Get string representation of each protocol

        result = "\n".join(result_parts)  # Join with newlines

        # Assuming self.string_formater is initialized
        if hasattr(self, "string_formater") and self.string_formater is not None:
            result = self.string_formater.removeTrailingComma(result)
        else:
            self.logger.warning(
                "string_formater not initialized for ProtocolArray. Cannot remove trailing comma."
            )

        return result

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `ProtocolArray`,
        similar to `getProtocolsInStrFormat`, but without the trailing comma removal.
        Each protocol is on a new line.
        """

        return "\n".join(str(element) for element in self.elements)

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `ProtocolArray` object,
        displaying the `repr` of its internal elements.
        """
        return f"ProtocolsArray(\n{self.elements!r}\n)"

    # Add standard container methods for better usability
    def __len__(self) -> int:
        """Returns the number of elements in the array. Enables `len(instance)`."""
        return len(self.elements)

    def __getitem__(self, index: Union[int, slice]) -> Union[Protocol, List[Protocol]]:
        """Allows direct indexing and slicing of the array, e.g., `array[0]` or `array[1:3]`."""
        return self.elements[index]

    def __iter__(self):
        """Makes the array iterable, allowing `for element in array_instance:`."""
        return iter(self.elements)
