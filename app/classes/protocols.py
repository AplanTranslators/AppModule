import re
from typing import Optional, Tuple, List, Union
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
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        parametrs: ParametrArray | None = None,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.body: BodyElementArray = BodyElementArray()
        self.parametrs: ParametrArray = ParametrArray()
        if parametrs is not None:
            self.parametrs = parametrs

    def copy(self):
        protocol = Protocol(self.identifier, self.source_interval, self.element_type)
        for element in self.body.getElements():
            protocol.body.addElement(element)
        protocol.parametrs = self.parametrs.copy()
        protocol.number = self.number
        return protocol

    def addBody(self, body: BodyElement):
        self.body.addElement(body)

    def getName(self):
        identifier = self.identifier
        if self.number:
            identifier = "{0}_{1}".format(identifier, self.number)
        if len(self.parametrs) > 0:
            identifier = "{0}({1})".format(identifier, str(self.parametrs))

        return identifier

    def updateLinks(self, module):
        for index, element in enumerate(self.body.getElements()):
            func_name = self.utils.extractFunctionName(element.identifier)
            if func_name:
                action = module.actions.getElement(func_name)
                if action:
                    self.body[index] = (
                        action,
                        element.element_type,
                        element.element_type,
                    )

    def __str__(self):
        return "{0} = {1}".format(
            self.getName(),
            str(self.body),
        )

    def __repr__(self):
        return f"\tProtocol({self.identifier!r}, {self.sequence!r})\n"


class ProtocolArray(BasicArray):
    def __init__(self):
        super().__init__(Protocol)

    def copy(self):
        new_aray: ProtocolArray = ProtocolArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
    ):
        result: ProtocolArray = ProtocolArray()
        elements = self.elements

        if (
            include is None
            and exclude is None
            and include_identifier is None
            and exclude_identifier is None
        ):
            return self.copy()

        for element in elements:
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue
            if (
                include_identifier is not None
                and element.identifier is not include_identifier
            ):
                continue
            if (
                exclude_identifier is not None
                and element.identifier is exclude_identifier
            ):
                continue

            result.addElement(element)

        return result

    def updateLinks(self, module):
        for element in self.getElements():
            element.updateLinks(module)

    def getProtocolsInStrFormat(self):
        result = ""
        for element in self.elements:
            result += "\n"
            result += str(element)
        result = self.string_formater.removeTrailingComma(result)
        return result

    def __repr__(self):
        return f"ProtocolsArray(\n{self.elements!r}\n)"
