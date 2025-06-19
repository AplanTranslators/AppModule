from enum import Enum, auto
from typing import List, Optional, Tuple
from ..classes.basic import Basic, BasicArray
from ..classes.element_types import ElementsTypes


class RangeTypes(Enum):
    """
    Defines the types of range or bit selections applied to an identifier.
    This is common in hardware description languages (e.g., SystemVerilog)
    where signals can be bit-vectors or arrays with specified ranges.
    """

    START = (
        auto()
    )  # Indicates a selection like `[start:]` or `(start` (start of a range/slice)
    END = auto()  # Indicates a selection like `[:end]` or `end)` (end of a range/slice)
    UNDEFINED = auto()  # No specific range selection applied
    START_END = (
        auto()
    )  # Indicates a full range selection like `[start:end]` or `(start, end)`


class Node(Basic):
    """
    Represents a fundamental element or a "node" in an abstract syntax tree (AST)
    or an expression. It can be an identifier, a literal, an operator,
    or part of a complex expression with design_unit qualification or bit/range selections.

    Extends `Basic` to inherit properties like identifier, source interval, and element type.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int] = (0, 0),
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        """
        Initializes a new `Node` instance.

        Args:
            identifier (str): The primary string representation of the node
                              (e.g., variable name, operator symbol, literal value).
            source_interval (Tuple[int, int], optional): A tuple (start_position, end_position)
                                                        indicating where this node appears
                                                        in the original source file.
                                                        Defaults to (0, 0) if not specified.
            element_type (ElementsTypes, optional): The classification of this node's type
                                                    (e.g., IDENTIFIER_ELEMENT, OPERATOR_ELEMENT).
                                                    Defaults to `ElementsTypes.NONE_ELEMENT`.
        """
        super().__init__(identifier, source_interval, element_type)

        self.expression: Optional[str] = (
            None  # The full string expression this node is part of, or represents.
        )
        self.module_name: Optional[str] = (
            None  # If this node represents a signal within a design_unit instance,
        )
        # this holds the instance name (e.g., `U1.signal_name`).
        self.bit_selection: bool = (
            False  # True if this node involves a single-bit selection (e.g., `signal[0]`).
        )
        self.range_selection: RangeTypes = (
            RangeTypes.UNDEFINED
        )  # Type of range selection (e.g., `[start:end]`, `[start:]`).

    def copy(self) -> "Node":
        """
        Creates a shallow copy of the current `Node` instance.
        Since all attributes are immutable types (str, bool, Enum) or are themselves
        copied by value (Tuple), a shallow copy is effectively a deep copy for this class.

        Returns:
            Node: A new `Node` object with the same attribute values as the original.
        """
        node_copy = Node(self.identifier, self.source_interval, self.element_type)
        node_copy.expression = self.expression
        node_copy.module_name = self.module_name
        node_copy.bit_selection = self.bit_selection
        node_copy.range_selection = self.range_selection
        return node_copy

    def getName(self) -> str:
        """
        Generates a formatted name for the node, incorporating design_unit qualification
        and specific formatting for bit/range selections.

        This method aims to reconstruct a representation of the node's identifier
        as it would appear in the source code, potentially adding parentheses
        based on `range_selection` or `bit_selection`.

        Returns:
            str: The formatted name string for the node.
        """
        result = self.identifier

        # Prepend design_unit name if present (e.g., "design_unit.signal")
        if self.module_name:
            result = f"{self.module_name}.{result}"

        # Apply formatting based on range selection type
        if self.range_selection == RangeTypes.START_END:
            result = f"({result})"
        elif self.range_selection == RangeTypes.START:
            result = f"({result}"
        elif self.range_selection == RangeTypes.END:
            result = f"{result})"

        # Apply formatting for bit selection
        if self.bit_selection:
            # Check if identifier is numeric (e.g., '0' for a bit index)
            # Assumes self.utils.isNumericString is available and works.
            if hasattr(self, "utils") and self.utils.isNumericString(self.identifier):
                result = f"({result})"
            else:
                # This formatting ", {0})" seems unusual for a bit selection.
                # It might imply a specific internal representation for a list/tuple like structure.
                # For example, BGET(array, index)
                result = f", {result})"
        return result

    def __str__(self) -> str:
        """
        Returns the primary identifier of the node.
        This provides a concise human-readable representation.
        """
        return self.identifier

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `Node` object,
        displaying its key attributes for debugging and introspection.
        """
        return (
            f"Node(identifier={self.identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"element_type={self.element_type!r}, "
            f"expression={self.expression!r}, "
            f"module_name={self.module_name!r}, "
            f"bit_selection={self.bit_selection!r}, "
            f"range_selection={self.range_selection!r}, "
            f"sequence={getattr(self, 'sequence', 'N/A')!r})"
        )


class NodeArray(BasicArray):
    """
    A specialized array for managing a collection of `Node` objects.
    This class is typically used to represent parsed expressions or sequences
    of operations where each part is a `Node`.

    It includes logic for handling specific types of actions (like assignments)
    and custom logic for reconstructing the expression string.
    """

    def __init__(self, node_type: ElementsTypes):
        """
        Initializes a new `NodeArray` instance.

        Args:
            node_type (ElementsTypes): The primary type that this NodeArray represents
                                       (e.g., a specific type of expression or statement).
        """
        super().__init__(Node)  # Configure BasicArray to hold Node objects
        self.node_type: ElementsTypes = node_type
        # `action_type` seems to represent the type of the overall operation this node array forms.
        self.action_type: ElementsTypes = ElementsTypes.NONE_ELEMENT

    def isAssign(self) -> bool:
        """
        Checks if the `action_type` of this NodeArray indicates an assignment operation.

        Returns:
            bool: True if the action type is `ASSIGN_ELEMENT` or `ASSIGN_SENSETIVE_ELEMENT`,
                  False otherwise.
        """
        return (
            self.action_type == ElementsTypes.ASSIGN_ELEMENT
            or self.action_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
        )

    # The commented-out `InitAssign` method suggests it might be for
    # automatically inserting an '=' operator for assignments.
    # def InitAssign(self):
    #     """
    #     (Commented out in original)
    #     Potentially inserts an assignment operator (=) into the node array
    #     if it's an assignment type and only contains one element initially.
    #     """
    #     if self.isAssign() and len(self) == 1:
    #         self.elements.append(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))

    def addElement(self, new_element: Basic) -> int:
        """
        Adds a new element (expected to be a `Node`) to the array.
        Includes custom logic to prevent adding elements with overlapping
        source intervals if `source_interval` is not (0,0).

        Args:
            new_element (Basic): The element to add. Expected to be a `Node` instance.

        Returns:
            int: The index of the newly added element (or the last element if not added due to interval overlap).

        Raises:
            TypeError: If `new_element` is not of type `Node` (a warning is logged instead of raising if this is typical behavior).
                       The original code logs a warning, but the type hint expects `Node`.
        """
        # Check if the new element's source interval conflicts with existing elements.
        # This typically means elements with distinct source locations should be distinct in the array.
        # Assumes `checkSourceInteval` and `getLastElement` are methods of BasicArray.
        if new_element.source_interval != (0, 0):
            # Get the last element to compare its source interval.
            last_element = self.getLastElement()
            if last_element:  # Check if there's an element to compare against
                # If the new element's source interval is not unique (e.g., overlaps),
                # prevent adding and return the index of the last element.
                if not self.checkSourceInteval(new_element.source_interval):
                    return len(self) - 1

        self.elements.append(new_element)

        # Log a warning if the added element is not a `Node` instance.
        # This implies `NodeArray` is strictly for `Node` objects, but allows `Basic` for flexibility
        # in the method signature, with a warning for type mismatches.
        if not isinstance(new_element, Node):
            # Ensure logger is initialized (as per the __init__ update)
            self.logger.warning(
                f"Object should be of type {Node.__name__} but you passed an "
                f"object of type {type(new_element).__name__}. Object: {new_element}",
            )
        return len(self) - 1

    def __str__(self) -> str:
        """
        Reconstructs a string representation of the expression from the sequence of `Node` objects.
        This method contains complex logic to correctly insert spaces, parentheses, and
        apply specific formatting rules based on `ElementsTypes` and `RangeTypes`.

        This method relies heavily on `self.utils` and `self.string_formater` which
        MUST be initialized in the `NodeArray` instance before calling this method.

        Returns:
            str: The reconstructed expression string.
        """
        result_parts: List[str] = (
            []
        )  # Using a list of parts for efficient string building
        # Unary operators that typically do not have a space between them and their operand
        unary_operators = {"~", "!"}
        bracket_flag = False  # Flag to track open parentheses after unary operators

        # Check for the presence of required utility objects
        if self.utils is None:
            self.logger.error(
                "NodeArray.utils is not initialized. Cannot format string."
            )
            return "<Error: utils not initialized>"
        if self.string_formater is None:
            self.logger.error(
                "NodeArray.string_formater is not initialized. Cannot format string."
            )
            return "<Error: string_formater not initialized>"

        for index, element in enumerate(self.elements):
            current_node: Node = element
            previous_node: Optional[Node] = None
            if index > 0:
                previous_node = self.elements[index - 1]

            # 1. Logic for closing parentheses if `bracket_flag` is set and the current element is an operator
            # This is generally for closing parentheses opened after a unary operator
            if (
                bracket_flag
                and current_node.element_type is ElementsTypes.OPERATOR_ELEMENT
            ):
                result_parts.append(")")
                bracket_flag = False

            # --- Start of improved space handling logic ---
            # 2. Logic for adding spaces between elements
            if index > 0:  # Add a space before all elements except the first one
                # Special cases where NO space is added before the current element
                if (
                    current_node.element_type is ElementsTypes.DOT_ELEMENT
                    or current_node.element_type is ElementsTypes.SEMICOLON_ELEMENT
                    or current_node.bit_selection  # e.g., `array[index]` no space between array and [
                    or current_node.range_selection
                    in {
                        RangeTypes.START_END,
                        RangeTypes.START,
                        RangeTypes.END,
                    }  # e.g., `signal[msb:lsb]` no space between signal and [
                    or (
                        current_node.identifier == "("
                        and previous_node
                        and previous_node.element_type
                        is ElementsTypes.IDENTIFIER_ELEMENT
                    )  # Function call: `func(`
                ):
                    pass  # No space
                # Special cases where NO space is added AFTER the previous element
                elif (
                    previous_node
                    and previous_node.element_type is ElementsTypes.DOT_ELEMENT
                    or (
                        previous_node and previous_node.identifier in unary_operators
                    )  # Unary operator: `!signal`
                ):
                    pass  # No space
                else:
                    # Default: add a space
                    result_parts.append(" ")

                # Specific logic for opening parentheses after unary operators.
                # This should only happen IF the previous_node was a unary operator AND we *didn't* add a space.
                # It's crucial this check happens *after* determining if a space is needed.
                if (
                    previous_node
                    and previous_node.identifier in unary_operators
                    and not bracket_flag
                ):
                    # Only add '(' if it's not already part of current_node's identifier (e.g., current_node is already a function call)
                    if "(" not in current_node.identifier:
                        result_parts.append("(")
                        bracket_flag = True
            # --- End of improved space handling logic ---

            # 3. Get the formatted name of the current node
            formatted_identifier = current_node.getName()

            # 4. Apply specific formatting based on element type
            if current_node.element_type is ElementsTypes.ARRAY_ELEMENT:
                formatted_identifier += ".value"
            elif current_node.element_type is ElementsTypes.ARRAY_SIZE_ELEMENT:
                formatted_identifier += ".size"

            # 5. Handle bit-selection formatting for the NEXT element (if current is part of BGET)
            if index + 1 < len(self.elements):
                next_node: Node = self.elements[index + 1]
                if next_node.bit_selection:
                    if self.utils.isNumericString(next_node.identifier) is None:
                        formatted_identifier = f"BGET({formatted_identifier}"

            # 6. Apply specific formatting for PRECONDITION_ELEMENT type
            if self.node_type == ElementsTypes.PRECONDITION_ELEMENT:
                formatted_identifier = self.string_formater.addEqueToBGET(
                    formatted_identifier
                )

            # 7. Special handling for a 'pipe-only' identifier (|) after an operator
            if (
                self.utils.containsOnlyPipe(formatted_identifier)
                and previous_node
                and previous_node.element_type is ElementsTypes.OPERATOR_ELEMENT
            ):
                first_element_name = self.elements[0].getName()
                formatted_identifier = f"{first_element_name} {formatted_identifier}"

            # 8. Handle increment/decrement operators (++, --)
            if "++" in str(current_node.identifier) and previous_node:
                # These are usually post-increment/decrement,
                # so the previous element's name is the operand.
                # The '++' or '--' token itself shouldn't directly appear as part of the output,
                # but rather converted to a `+1` or `-1` assignment.
                # We need to ensure no space was added just before the '++' or '--'
                if result_parts and result_parts[-1] == " ":
                    result_parts.pop()  # Remove the last added space if there was one
                result_parts.append(f"= {previous_node.getName()} + 1")
            elif "--" in str(current_node.identifier) and previous_node:
                if result_parts and result_parts[-1] == " ":
                    result_parts.pop()  # Remove the last added space if there was one
                result_parts.append(f"= {previous_node.getName()} - 1")
            else:
                # 9. General case: append the formatted identifier
                if current_node.element_type is ElementsTypes.SEMICOLON_ELEMENT:
                    if index != len(self.elements) - 1:
                        result_parts.append(f"{formatted_identifier}\n\t\t")
                    else:
                        result_parts.append(formatted_identifier)
                else:
                    result_parts.append(formatted_identifier)

        # 10. Close any pending open parentheses at the very end of the expression
        if bracket_flag:
            result_parts.append(")")

        return "".join(result_parts)

    def getElementByIndex(self, index: int) -> Node:
        """
        Retrieves a `Node` object from the array by its index.

        Args:
            index (int): The zero-based index of the desired element.

        Returns:
            Node: The `Node` object at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        # BasicArray is expected to manage 'self.elements' list.
        return self.elements[index]

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `NodeArray` object,
        displaying its `node_type`, `action_type`, and the `repr` of its internal elements.
        """
        return (
            f"NodeArray(\n"
            f"\tnode_type={self.node_type!r},\n"
            f"\taction_type={self.action_type!r},\n"
            f"\telements={self.elements!r}\n"
            f")"
        )
