from typing import List, Optional, Tuple, Union, overload
from ..classes.basic import Basic, BasicArray
from ..classes.element_types import ElementsTypes


class ValueParametr(Basic):
    """
    Represents a parameter that holds an integer value, potentially derived from
    a string expression. This class is typically used for constants,
    sized literals, or simple mathematical/logical expressions.
    It extends the `Basic` class for fundamental identification and source tracking.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        value: int = 0,
        expression: Optional[str] = None,
        # element_type is inherited from Basic, defaults to NONE_ELEMENT,
        # no specific type seems to be assigned here unless done by Basic init
    ):
        """
        Initializes a new `ValueParametr` instance.

        Args:
            identifier (str): The name of the parameter (e.g., "WIDTH", "COUNT").
            source_interval (Tuple[int, int]): The (start, end) character positions
                                                in the original source file.
            value (int, optional): The pre-calculated or default integer value of the parameter.
                                   Defaults to 0.
            expression (Optional[str]): A string representing the expression from which
                                        the parameter's value can be derived. Defaults to None.
        """
        super().__init__(identifier, source_interval)
        self.value: int = value
        self.expression: Optional[str] = expression

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "ValueParametr":
        """
        Creates a shallow copy of the `ValueParametr` instance.
        For primitive types like int, str, and tuples, a shallow copy is sufficient.

        Returns:
            ValueParametr: A new `ValueParametr` object with copied attributes.
        """
        new_parametr = ValueParametr(
            self.identifier,
            self.source_interval,
            self.value,
            self.expression,
        )
        # Assuming `self.number` is an attribute (e.g., from Basic)
        new_parametr.number = self.number
        return new_parametr

    def prepareExpression(self) -> None:
        """
        Pre-processes and formats the `expression` string to a standardized Aplan format.
        This involves applying a series of transformations using utility methods
        from `self.string_formater`. The `expression` attribute is modified in-place.

        Precondition: `self.string_formater` must be initialized and accessible.
        """
        if self.expression is None:
            return  # No expression to prepare

        # The existence of self.string_formater is an implicit dependency.
        # It should be initialized in `Basic` or explicitly passed/imported.
        if not hasattr(self, "string_formater") or self.string_formater is None:
            self.logger.warning(
                f"`string_formater` not available for ValueParametr '{self.identifier}'. Expression not prepared."
            )
            return

        expression = self.expression

        # Apply various string formatting and transformation rules
        expression = self.string_formater.valuesToAplanStandart(expression)
        expression = self.string_formater.doubleOperators2Aplan(expression)
        expression = self.string_formater.addLeftValueForUnaryOrOperator(expression)
        expression = self.string_formater.addSpacesAroundOperators(expression)
        expression = self.string_formater.addBracketsAfterNegation(expression)
        expression = self.string_formater.addBracketsAfterTilda(expression)
        expression = self.string_formater.vectorSizes2AplanStandart(expression)
        expression = self.string_formater.replace_cpp_operators(expression)
        expression = self.string_formater.generatePythonStyleTernary(expression)

        self.expression = expression  # Update the instance's expression

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the ValueParametr.
        Prioritizes the expression if available, otherwise shows the value.
        """
        if self.expression:
            return f"{self.identifier} = {self.expression}"
        else:
            return f"{self.identifier} = {self.value}"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `ValueParametr` object,
        displaying its key attributes for debugging and introspection.
        """
        return (
            f"ValueParametr("
            f"identifier={self.identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"value={self.value!r}, "
            f"expression={self.expression!r}"
            f")"
        )


class ValueParametrArray(BasicArray):
    """
    A specialized array for managing a collection of `ValueParametr` objects.
    This class extends `BasicArray` and provides methods for adding, filtering,
    and evaluating parameter expressions within the array.
    """

    def __init__(self):
        """
        Initializes a new `ValueParametrArray` instance, specifically configured
        to store objects of type `ValueParametr`.
        """
        super().__init__(
            ValueParametr
        )  # Configure BasicArray to hold ValueParametr objects

        # Assumption: `self.string_formater` and `self.utils` are available,
        # likely inherited from BasicArray or a common utility base class.
        # self.string_formater: 'StringFormater' = StringFormater() # Example if initialized here
        # self.utils: 'Utils' = Utils() # Example if initialized here

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "ValueParametrArray":
        """
        Creates a deep copy of the current `ValueParametrArray` instance.
        It iterates through all contained `ValueParametr` objects and adds their
        deep copies to the new array, ensuring full independence.

        Returns:
            ValueParametrArray: A new `ValueParametrArray` containing deep copies of all
                                original parameters.
        """
        new_array = ValueParametrArray()
        for element in self.elements:  # Iterate directly over the internal list
            new_array.addElement(element.copy())  # Use ValueParametr's deep copy method
        return new_array

    def getElementByIndex(self, index: int) -> "ValueParametr":
        """
        Retrieves a `ValueParametr` object from the array by its zero-based index.
        This method delegates to the base `BasicArray`'s implementation.

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            ValueParametr: The `ValueParametr` object at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        return super().getElementByIndex(index)

    def getElementsIE(
        self,
        include_type: Optional["ElementsTypes"] = None,
        exclude_type: Optional["ElementsTypes"] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
    ) -> "ValueParametrArray":
        """
        Filters the `ValueParametr` objects in the array based on their
        `element_type` and/or `identifier`. This method allows for both
        inclusion and exclusion criteria.

        Args:
            include_type (Optional[ElementsTypes]): Only include parameters with this element type.
            exclude_type (Optional[ElementsTypes]): Exclude parameters with this element type.
            include_identifier (Optional[str]): Only include parameters with this identifier.
            exclude_identifier (Optional[str]): Exclude parameters with this identifier.

        Returns:
            ValueParametrArray: A new `ValueParametrArray` containing only the parameters
                                that match all specified filtering criteria. If no criteria
                                are provided, a deep copy of the original array is returned.
        """
        result_array: "ValueParametrArray" = ValueParametrArray()

        # If no filters are specified, return a deep copy of the entire array.
        if all(
            arg is None
            for arg in [
                include_type,
                exclude_type,
                include_identifier,
                exclude_identifier,
            ]
        ):
            return self.copy()

        for element in self.elements:
            # Apply element_type filters
            if include_type is not None and element.element_type is not include_type:
                continue
            if exclude_type is not None and element.element_type is exclude_type:
                continue

            # Apply identifier filters (use `==` for string comparison, not `is`)
            if (
                include_identifier is not None
                and element.identifier != include_identifier
            ):
                continue
            if (
                exclude_identifier is not None
                and element.identifier == exclude_identifier
            ):
                continue

            result_array.addElement(element)  # Add the element if it passes all filters
        return result_array

    def addElement(self, new_element: "ValueParametr") -> int:
        """
        Adds a new `ValueParametr` element to the array.
        The `prepareExpression` method is called on the new element before adding it.
        The internal list of elements is then sorted based on the length of their identifier.

        Args:
            new_element (ValueParametr): The `ValueParametr` object to add.

        Returns:
            int: The index of the added element in the (potentially re-sorted) array.

        Raises:
            TypeError: If the `new_element` is not an instance of `ValueParametr`.
        """
        if not isinstance(new_element, self.element_type):
            raise TypeError(
                f"Object should be of type {self.element_type.__name__} but "
                f"you passed an object of type {type(new_element).__name__}. \n"
                f"Object: {new_element!r}"
            )

        new_element.prepareExpression()  # Prepare expression immediately upon adding
        self.elements.append(new_element)

        # WARNING: This sorting operation is O(N log N) and can be very inefficient
        # if elements are added one by one to a large array.
        # Consider if this sorting is truly necessary after every add, or if it can
        # be done once at the end, or if a different data structure (e.g., a sorted list
        # implementation or a more optimized insertion strategy) is required.
        # Also, this implementation allows duplicate identifiers, unlike some other `addElement` methods.
        self.elements = sorted(
            self.elements,
            key=lambda element: len(element.identifier),
            reverse=True,  # Sorts by length of identifier, longest first
        )
        # The index returned here might not be the actual index before sorting,
        # but it will be its index after the current sort.
        return self.getElementIndex(new_element.identifier)

    def evaluateParametrExpressionByIndex(self, index: int) -> Union[int, str]:
        """
        Evaluates the expression of a `ValueParametr` at a given index within the array.
        It first substitutes any nested parameter calls within the expression
        and then evaluates the final expression string to an integer value.
        The evaluated value is stored back into the parameter's `value` attribute.

        Args:
            index (int): The index of the `ValueParametr` whose expression is to be evaluated.

        Returns:
            Union[int, str]: The evaluated integer value, or potentially the string
                             expression if evaluation fails or is not possible.

        Raises:
            IndexError: If the index is out of bounds.
        """
        parametr = self.getElementByIndex(index)
        expression = parametr.expression

        if expression is None:
            return parametr.value  # Return current value if no expression

        if len(expression) > 0:
            # Assumption: `self.string_formater` and `self.utils` are available.
            if not hasattr(self, "string_formater") or self.string_formater is None:
                self.logger.warning(
                    f"`string_formater` not available for ValueParametrArray. Cannot substitute calls."
                )
                # Fallback: attempt to evaluate without substitution
            else:
                # Replace references to other ValueParametrs in the expression
                expression = self.string_formater.replaceValueParametrsCalls(
                    self, expression
                )

            if not hasattr(self, "utils") or self.utils is None:
                self.logger.warning(
                    f"`utils` (expression evaluator) not available. Cannot evaluate expression."
                )
                return expression  # Return raw expression if no evaluator

            # Evaluate the final expression string
            evaluated_value = self.utils.evaluateExpression(expression)
            parametr.value = evaluated_value  # Update the parameter's value
            return evaluated_value
        return parametr.value  # Return current value if expression is empty

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `ValueParametrArray`,
        listing each contained `ValueParametr` object's string representation.
        """
        # Join with a comma and newline for readability, each element indented
        return ",\n".join([str(element) for element in self.elements])

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `ValueParametrArray` object,
        displaying the `repr` of its internal elements list for debugging.
        """
        return f"ValueParametrArray(\n{self.elements!r}\n)"

    # Add standard container methods for better usability and Pythonic behavior
    def __len__(self) -> int:
        """Returns the number of elements in the array. Enables `len(instance)`."""
        return len(self.elements)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union["ValueParametr", List["ValueParametr"]]:
        """Allows direct indexing and slicing of the array, e.g., `array[0]` or `array[1:3]`."""
        return self.elements[index]

    def __iter__(self):
        """Makes the array iterable, allowing `for element in array_instance:`."""
        return iter(self.elements)
