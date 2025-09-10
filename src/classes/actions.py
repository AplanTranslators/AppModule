from typing import Optional, Tuple, List

from ..classes.parametrs import Parametr, ParametrArray
from ..classes.basic import Basic, BasicArray
from ..classes.element_types import ElementsTypes
from ..classes.node import NodeArray


class ActionParts:
    """
    Represents a collection of action components or segments, stored as a list of strings.
    This class is designed to hold the "body" or main content of an action,
    allowing for easy manipulation and representation of its parts.
    """

    def __init__(self):
        """
        Initializes a new ActionParts instance with an empty list for its body.
        The 'body' attribute will store string elements that constitute the action's parts.
        """
        self.body: List[str] = []

    def copy(self) -> "ActionParts":
        """
        Creates and returns a deep copy of the current ActionParts instance.
        This method ensures that modifications to the copied instance's 'body'
        do not affect the original instance's 'body'.

        Returns:
            ActionParts: A new ActionParts object with an independent copy of the 'body' list.
        """
        action_part_copy = ActionParts()
        # Use .copy() on the list to create a shallow copy of the list itself.
        # Since the list elements are strings (immutable), a shallow copy is sufficient
        # to prevent unintended modifications to the original object's list.
        action_part_copy.body = self.body.copy()
        return action_part_copy

    def __str__(self) -> str:
        """
        Returns a string representation of the action's body.
        The elements in the 'body' list are joined together by a semicolon and a space ("; ").
        This provides a human-readable format for the action's parts.
        """
        # The join method is more efficient and Pythonic for concatenating strings from a list
        # compared to looping and concatenating them manually.
        return "; ".join(self.body)

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the ActionParts object.
        This representation includes the class name and the 'body' attribute's
        representation, which is useful for debugging and introspection.
        """
        return f"ActionParts(body={self.body!r})"


class Action(Basic):
    """
    Represents a specific action within a system or process.

    This class extends `Basic`, inheriting foundational properties like an identifier
    and source interval. It encapsulates the core components of an action,
    including its preconditions, postconditions, and descriptive elements.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        exist_parametrs: ParametrArray = None,  # Changed default to None for clarity
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        """
        Initializes an Action instance.

        Args:
            identifier (str): A unique string identifier for the action.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                                positions of the action in its source.
            exist_parametrs (ParametrArray, optional): An array of parameters that must
                                                        exist for this action. Defaults to
                                                        an empty ParametrArray if not provided.
            element_type (ElementsTypes, optional): The type of element this action represents.
                                                    Defaults to ElementsTypes.NONE_ELEMENT.
        """
        # Call the parent class (Basic) constructor to initialize shared properties.
        super().__init__(identifier, source_interval, element_type)

        # Initialize collections for preconditions and postconditions.
        # These are expected to be NodeArray instances, specifically for
        # precondition and postcondition element types.
        self.precondition: NodeArray = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
        self.postcondition: NodeArray = NodeArray(ElementsTypes.POSTCONDITION_ELEMENT)

        # Initialize lists for description parts.
        # 'description_start' and 'description_end' are lists of strings,
        # likely for modular description building.
        self.description_start: List[str] = []
        # 'description_action_name' holds the main name of the action for descriptive purposes.
        self.description_action_name: str = ""
        self.description_end: List[str] = []

        # Initialize parameter arrays.
        # 'exist_parametrs' represents parameters that must exist for the action to be valid.
        self.exist_parametrs: ParametrArray = (
            exist_parametrs if exist_parametrs is not None else ParametrArray()
        )
        # 'parametrs' holds parameters specifically associated with this action's definition.
        self.parametrs: ParametrArray = ParametrArray()
        # Note: self.utils is assumed to be available, potentially from the Basic class or imported.
        # If it's not inherited, it should be initialized here or imported explicitly.

    def copy(self) -> "Action":
        """
        Creates a deep copy of the current Action instance.
        This ensures that when an Action object is copied, all its mutable attributes
        (like lists and custom array objects) are also independently copied,
        preventing unintended side effects from modifications to the copy.

        Returns:
            Action: A new Action object that is a deep copy of the original.
        """
        action_copy = Action(
            self.identifier,
            self.source_interval,
            self.exist_parametrs.copy(),  # Deep copy ParametrArray
            self.element_type,
        )
        # Deep copy mutable collections.
        action_copy.precondition = self.precondition.copy()
        action_copy.postcondition = self.postcondition.copy()
        # For simple lists of immutable types (strings), a shallow copy is often sufficient,
        # but to be truly "deep," we would use self.description_start.copy().
        # However, for performance and typical use cases, direct assignment is fine if
        # these lists are not modified independently in the copy.
        # Changed to .copy() for consistency with other mutable types.
        action_copy.description_start = self.description_start.copy()
        action_copy.description_action_name = (
            self.description_action_name
        )  # String is immutable
        action_copy.description_end = self.description_end.copy()
        action_copy.parametrs = self.parametrs.copy()  # Deep copy ParametrArray

        return action_copy

    def getName(self, include_params: bool = True, to_upper: bool = False) -> str:

        display_identifier = self.identifier
        if to_upper:
            display_identifier = display_identifier.upper()

        # Append numeric suffix if 'number' is set and non-zero
        if self.number:  # Checks for truthiness (0 would be False)
            display_identifier = f"{display_identifier}_{self.number}"

        if include_params:
            if self.parametrs and len(self.parametrs) > 0:
                display_identifier = f"{display_identifier}({str(self.parametrs)})"
        return display_identifier

    def findParametrInBodyAndSetParametrs(self, parameters: "ParametrArray"):
        """
        Identifies parameters within the action's preconditions and postconditions
        and adds them to the action's internal `parametrs` list.

        Args:
            parameters (ParametrArray): An array of parameters to check against
                                        the action's body.
        """
        # It's assumed `self.utils` is available and has an `isVariablePresent` method.
        # If `self.utils` is not defined, this method will raise an AttributeError.
        if not hasattr(self, "utils"):
            self.logger.warning(
                "'self.utils' is not defined. `findParametrInBodyAndSetParametrs` might not function correctly."
            )
            return

        for parametr in parameters.getElements():
            # Check if the parameter's identifier is present in the string representation
            # of the precondition.
            if self.utils.isVariablePresent(
                str(self.precondition), parametr.identifier
            ):
                self.parametrs.addElement(parametr)

            # Check if the parameter's identifier is present in the string representation
            # of the postcondition.
            if self.utils.isVariablePresent(
                str(self.postcondition), parametr.identifier
            ):
                self.parametrs.addElement(parametr)

    def getBody(self) -> str:
        """
        Constructs and returns a formatted string representing the complete body of the action.
        This includes the description, preconditions, and postconditions,
        formatted for output, potentially in a specific domain language.
        """
        description_parts: List[str] = []

        # Join unique elements from description_start, separated by "; "
        # Use a set to keep track of added elements for uniqueness without changing order too much
        added_elements = set()
        for element in self.description_start:
            if element not in added_elements:
                description_parts.append(element)
                added_elements.add(element)
        description = "; ".join(description_parts)

        # Append the action name part
        # if description:  # Add "; " only if description_start had elements
        #    description += "; "
        description += f":action '{self.description_action_name} ("

        # Join unique elements from description_end, separated by "; "
        end_parts: List[str] = []
        added_elements = set()  # Reset for description_end
        for element in self.description_end:
            if element not in added_elements:
                end_parts.append(element)
                added_elements.add(element)
        description += "; ".join(end_parts)
        description += ")'"

        # Format the final body string based on the presence of parameters.
        if len(self.exist_parametrs) > 0:
            return (
                f" = ( Exist ({self.exist_parametrs}) (\n"
                f"\t\t({self.precondition})->\n"
                f'\t\t("{description};")\n'
                f"\t\t({self.postcondition})))"
            )
        elif len(self.parametrs) > 0:
            return (
                f"({self.parametrs}) = (\n"
                f"\t\t({self.precondition})->\n"
                f'\t\t("{description};")\n'
                f"\t\t({self.postcondition}))"
            )
        else:
            return (
                f" = (\n"
                f"\t\t({self.precondition})->\n"
                f'\t\t("{description};")\n'
                f"\t\t({self.postcondition}))"
            )

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the Action object.
        Combines the action's identifier with its formatted body.
        """
        return f"{self.identifier}{self.getBody()},"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the Action object.
        This representation includes the class name, identifier, and inherited
        'number' and 'sequence' attributes (if they exist from Basic), useful for debugging.
        """
        # Assumes 'number' and 'sequence' are attributes inherited from 'Basic'.
        # If they are not, this line might cause an AttributeError.
        return f"\tAction(identifier={self.identifier!r}, number={getattr(self, 'number', 'N/A')!r}, sequence={getattr(self, 'sequence', 'N/A')!r})\n"

    def __eq__(self, other: object) -> bool:
        """
        Compares this Action object to another object for equality.
        Two Action objects are considered equal if their formatted bodies are identical.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the objects are equal (based on body content), False otherwise.
        """
        if isinstance(other, Action):
            return self.getBody() == other.getBody()
        return False


class ActionArray(BasicArray):
    """
    A specialized array for managing a collection of Action objects.

    This class extends `BasicArray`, providing core functionalities for
    adding, retrieving, and manipulating `Action` instances. It includes
    methods for filtering actions, checking for uniqueness, and formatting
    their output.
    """

    def __init__(self):
        """
        Initializes a new ActionArray instance.
        It configures the array to specifically hold objects of type `Action`.
        """
        super().__init__(Action)

    def copy(self) -> "ActionArray":
        """
        Creates a deep copy of the current ActionArray instance.
        This ensures that all `Action` objects within the array are also
        independently copied, preventing shared references and enabling
        safe modifications to the copy without affecting the original.

        Returns:
            ActionArray: A new ActionArray object with independent copies of its actions.
        """
        new_array: ActionArray = ActionArray()
        for action_element in self.getElements():
            new_array.addElement(
                action_element.copy()
            )  # Ensures deep copy of each Action
        return new_array

    def getElementsIE(
        self,
        include: Optional[ElementsTypes] = None,
        exclude: Optional[ElementsTypes] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
    ) -> "ActionArray":
        """
        Filters and retrieves Action elements based on specified inclusion/exclusion criteria.
        This method allows filtering by element type and/or identifier.

        Args:
            include (Optional[ElementsTypes]): If provided, only include actions
                                               of this specific `ElementsTypes`.
            exclude (Optional[ElementsTypes]): If provided, exclude actions
                                               of this specific `ElementsTypes`.
            include_identifier (Optional[str]): If provided, only include actions
                                                matching this identifier.
            exclude_identifier (Optional[str]): If provided, exclude actions
                                                matching this identifier.

        Returns:
            ActionArray: A new ActionArray containing only the filtered elements.
                         Returns a deep copy of the original array if no filters are applied.
        """
        result_array: ActionArray = ActionArray()

        # If no filters are specified, return a deep copy of all elements.
        if (
            include is None
            and exclude is None
            and include_identifier is None
            and exclude_identifier is None
        ):
            return self.copy()

        for (
            element
        ) in (
            self.elements
        ):  # self.elements is assumed to be the internal list from BasicArray
            # Apply exclusion filters first, as they typically have higher priority.
            if exclude is not None and element.element_type == exclude:
                continue
            if (
                exclude_identifier is not None
                and element.identifier == exclude_identifier
            ):
                continue

            # Apply inclusion filters.
            if include is not None and element.element_type != include:
                continue
            if (
                include_identifier is not None
                and element.identifier != include_identifier
            ):
                continue

            # If the element passes all filters, add it to the result.
            result_array.addElement(element)

        return result_array

    def isUniqAction(
        self, action: Action
    ) -> Tuple[Optional[Action], Optional[str], Tuple[Optional[int], Optional[int]]]:
        """
        Checks if a given Action object already exists in the array based on its content.
        This relies on the `__eq__` method of the `Action` class for comparison.

        Args:
            action (Action): The Action object to check for uniqueness.

        Returns:
            Tuple[Optional[Action], Optional[str], Tuple[Optional[int], Optional[int]]]:
                A tuple containing:
                - The existing unique `Action` object if found, otherwise `None`.
                - The identifier of the found action, otherwise `None`.
                - The source interval of the found action, otherwise `(None, None)`.
        """
        for element in self.elements:
            if element == action:  # Uses Action's __eq__ for comparison
                return (element, element.identifier, element.source_interval)
        return (None, None, (None, None))

    def isUniqActionBySourceInterval(
        self, source_interval: Tuple[int, int]
    ) -> Optional[Action]:
        """
        Checks if an Action object with a specific source interval already exists in the array.

        Args:
            source_interval (Tuple[int, int]): The source interval to check for.

        Returns:
            Optional[Action]: The `Action` object if found, otherwise `None`.
        """
        for element in self.elements:
            if element.source_interval == source_interval:
                return element
        return None

    def getActionsInStrFormat(self) -> str:
        """
        Generates a multi-line string representation of all actions in the array.
        Each action is represented on a new line, and trailing commas are removed.

        Returns:
            str: A formatted string containing all actions.
        """
        result_string = ""
        for index, element in enumerate(self.elements):
            if index != 0:
                result_string += "\n"  # Add a newline between actions
            result_string += str(element)  # Convert Action to string using its __str__

        # Assumes self.string_formater is an instance of a class with removeTrailingComma.
        return self.string_formater.removeTrailingComma(result_string)

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the ActionArray object.
        This provides a clear view of the array's contents for debugging and introspection.
        """
        return f"ActionArray(\n{self.elements!r}\t)"
