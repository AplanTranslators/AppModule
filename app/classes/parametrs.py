from typing import List, Optional, Tuple, Union
from ..classes.basic import Basic, BasicArray


class Parametr(Basic):
    """
    Represents a single parameter in a hardware description language (HDL) context,
    such as a module parameter, port, or local variable.

    It extends the `Basic` class to inherit fundamental properties like `identifier`
    and `source_interval`.
    """

    def __init__(
        self,
        identifier: str,
        param_type: str,  # Renamed 'type' to 'param_type' to avoid conflict with built-in `type()`
        source_interval: Tuple[int, int] = (0, 0),
        action_name: str = "",
    ):
        """
        Initializes a new `Parametr` instance.

        Args:
            identifier (str): The primary name of the parameter (e.g., "WIDTH", "data_in").
            param_type (str): The data type or kind of the parameter (e.g., "integer", "logic", "var", "input", "output").
                              Renamed from 'type' to avoid shadowing the built-in `type` function.
            source_interval (Tuple[int, int], optional): A tuple (start_position, end_position)
                                                        indicating where this parameter appears
                                                        in the original source file. Defaults to (0, 0).
            action_name (str, optional): An optional prefix used to create a unique identifier.
                                         Often related to the action or context this parameter is part of.
                                         Defaults to an empty string.
        """
        # Note: The original code adds an underscore to action_name if it's not empty,
        # but then concatenates it with an empty string: `action_name + ""`.
        # This seems like an oversight if the intention was to prefix the identifier.
        # I'll adjust `unique_identifier` to correctly use `action_name` as a prefix.

        self.param_type: str = param_type  # Use param_type instead of type
        self.module_name: Optional[str] = (
            None  # Name of the module this parameter belongs to, if applicable.
        )

        # Original: if len(action_name) > 0: action_name += "_"
        # Original: self.unique_identifier = action_name + ""
        # Corrected logic for unique_identifier based on common pattern:
        if action_name:  # Check if action_name is not empty
            self.unique_identifier: str = f"{action_name}_{identifier}"
        else:
            self.unique_identifier: str = (
                identifier  # If no action_name, identifier is unique identifier
            )

        # The 'number' attribute in copy() is not initialized here, which might lead to an AttributeError.
        # If 'number' is a critical attribute, it should be part of the __init__ or clearly stated
        # how it's assigned. For now, I'll add a default to prevent errors in copy().
        self.number: Optional[int] = (
            None  # Placeholder, assume it's assigned later if needed
        )

        super().__init__(identifier, source_interval)

    def copy(self) -> "Parametr":
        """
        Creates a new `Parametr` instance that is a shallow copy of the current one.
        All attributes are copied by value (str, int, tuple are immutable),
        making this effectively a deep copy for this class's attributes.

        Returns:
            Parametr: A new `Parametr` object with the same attribute values.
        """
        # Pass identifier, type, and source_interval directly to the constructor.
        # Re-apply action_name logic to derive unique_identifier if needed,
        # or directly copy unique_identifier as it's already computed.

        # Option 1: Re-derive unique_identifier from original action_name (if action_name was stored)
        # For simplicity and to match original, directly copy the computed unique_identifier.
        copied_param = Parametr(
            self.identifier, self.param_type, self.source_interval, action_name=""
        )  # Pass empty action_name to avoid re-prefixing identifier
        copied_param.unique_identifier = (
            self.unique_identifier
        )  # Directly copy already computed unique_identifier
        copied_param.module_name = self.module_name  # Copy module_name
        copied_param.number = self.number  # Ensure 'number' is copied, if it exists

        return copied_param

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `Parametr` object.
        Formats differently based on whether its type contains "var".

        Returns:
            str: The string representation of the parameter.
        """
        if "var" in self.param_type:
            return f"{self.identifier}"  # If type is 'var' (e.g., Verilog `var`), just return identifier
        else:
            # Otherwise, return unique_identifier:type (e.g., 'clk:input', 'WIDTH_my_param:parameter')
            return f"{self.unique_identifier}:{self.param_type}"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `Parametr` object,
        displaying its key attributes for debugging and introspection.
        """
        return (
            f"Parametr("
            f"identifier={self.identifier!r}, "
            f"param_type={self.param_type!r}, "
            f"unique_identifier={self.unique_identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"module_name={self.module_name!r}, "
            f"number={self.number!r}"
            f")"
        )


class ParametrArray(BasicArray):
    """
    A specialized array for managing a collection of `Parametr` objects.
    This class extends `BasicArray` and provides specific methods for
    adding, copying, and generating unique names for parameters.
    """

    def __init__(self):
        """
        Initializes a new `ParametrArray` instance, specifically configured
        to store objects of type `Parametr`.
        """
        super().__init__(Parametr)  # Configure BasicArray to hold Parametr objects

    def copy(self) -> "ParametrArray":
        """
        Creates a deep copy of the current `ParametrArray` instance.
        It iterates through all elements and adds a copy of each `Parametr`
        object to the new array.

        Returns:
            ParametrArray: A new `ParametrArray` containing copies of all original parameters.
        """
        new_array: ParametrArray = ParametrArray()
        for (
            element
        ) in self.getElements():  # Assumes getElements() returns the list of elements
            new_array.addElement(element.copy())  # Use Parametr's copy method
        return new_array

    def insert(self, index: int, element: Parametr) -> None:
        """
        Inserts a `Parametr` element at a specific index in the array.

        Args:
            index (int): The index at which to insert the element.
            element (Parametr): The `Parametr` object to insert.
        """
        # The original code ` {self.elements.insert(index, element)} ` was a syntax error.
        # It should be a direct call to the list's insert method.
        self.elements.insert(index, element)

    def addElement(self, new_element: Parametr) -> Tuple[bool, int]:
        """
        Adds a new `Parametr` element to the array.
        It checks if an element with the same identifier already exists
        to ensure uniqueness.

        Args:
            new_element (Parametr): The `Parametr` object to add.

        Returns:
            Tuple[bool, int]: A tuple where the first element is `True` if the
                              element was added (or `False` if it already existed),
                              and the second element is the index of the added
                              or existing element.

        Raises:
            TypeError: If the `new_element` is not an instance of `self.element_type` (i.e., `Parametr`).
        """
        if isinstance(new_element, self.element_type):
            # Check if an element with the same identifier already exists
            existing_element = self.getElement(
                new_element.identifier
            )  # Assumes getElement(identifier) finds by identifier
            if existing_element is not None:
                # If it exists, return False and its index
                return (
                    False,
                    self.getElementIndex(existing_element.identifier),
                )  # Assumes getElementIndex(identifier) returns index

            # If unique, add the new element
            self.elements.append(new_element)
            return (True, self.getElementIndex(new_element.identifier))
        else:
            # Raise an error if the type is incorrect
            raise TypeError(
                f"Object should be of type {self.element_type.__name__} but you passed an object of type {type(new_element).__name__}. \n Object: {new_element}"
            )

    def generateParametrNameByIndex(self, index: int) -> str:
        """
        Generates a unique, short alphabetic name based on an integer index,
        similar to how Excel columns are named (A, B, ..., Z, AA, AB, ...).

        Args:
            index (int): The integer index to convert into an alphabetic name.

        Returns:
            str: The generated alphabetic name.
        """
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        base = len(alphabet)
        name = ""

        # Loop until the index is fully converted
        while True:
            char_index = index % base
            name = alphabet[char_index] + name
            index = (
                index // base - 1
            )  # Adjust index for the next iteration (0-based to 1-based then decrement)

            if index < 0:
                break

        return name

    def getIdentifiersListString(self, parametrs_count: int) -> str:
        """
        Generates a comma-separated string of parameter identifiers, enclosed in parentheses.
        This is typically used for function/module call arguments or port lists.

        Args:
            parametrs_count (int): The number of parameters expected or desired in the string.

        Returns:
            str: A string like "(param1, param2, param3)".

        Raises:
            ValueError: If `parametrs_count` exceeds the actual number of parameters in the array.
        """
        result_parts: List[str] = []
        if len(self.elements) == 0:
            return "".join(result_parts)

        if parametrs_count <= len(
            self.elements
        ):  # Access self.elements directly for length
            result_parts.append("(")
            for index in range(parametrs_count):
                if index != 0:
                    result_parts.append(", ")
                result_parts.append(self.elements[index].identifier)
            result_parts.append(")")
        else:
            raise ValueError(
                f"The number of arguments passed ({len(self.elements)}) is different from the number expected ({parametrs_count})."
            )
        return "".join(result_parts)

    def generateUniqNamesForParamets(self) -> None:
        """
        Assigns a unique alphabetic identifier (generated by `generateParametrNameByIndex`)
        to the `unique_identifier` attribute of each `Parametr` object in the array.
        """
        for index, element in enumerate(
            self.getElements()
        ):  # Assumes getElements() works
            element.unique_identifier = self.generateParametrNameByIndex(index)

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `ParametrArray`.
        This joins the string representation of each `Parametr` with a comma and space.

        Returns:
            str: A string like "param1, param2, param3".
        """
        # Using a list comprehension and join for conciseness and efficiency
        return ", ".join(str(element) for element in self.elements)

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `ParametrArray` object,
        displaying the `repr` of its internal elements.
        """
        return f"ParametrArray(\n{self.elements!r}\n)"

    # Optional: Add methods for better array behavior
    def __len__(self) -> int:
        """Returns the number of elements in the array."""
        return len(self.elements)

    def __getitem__(self, index: Union[int, slice]) -> Union[Parametr, List[Parametr]]:
        """Allows direct indexing and slicing of the array."""
        return self.elements[index]

    def __iter__(self):
        """Makes the array iterable."""
        return iter(self.elements)
