from typing import List, Optional, Tuple, Union
from ..classes.basic import Basic, BasicArray
from ..classes.declarations import (
    AplanDeclType,
    DeclTypes,
    Declaration,
    DeclarationArray,
)
from ..classes.element_types import ElementsTypes


class Typedef(Basic):
    """
    Represents a type definition (e.g., `typedef` in C/C++, `type` in SystemVerilog).
    It defines a new named type and typically contains a collection of declarations
    that constitute the definition (e.g., members of a struct or an enum).
    """

    def __init__(
        self,
        identifier: str,
        unique_identifier: str,
        source_interval: Tuple[int, int],
        file_path: str,
        data_type: "DeclTypes",  # Type of the definition (e.g., ENUM, STRUCT)
        element_type: "ElementsTypes" = ElementsTypes.NONE_ELEMENT,  # Default to NONE_ELEMENT
    ):
        """
        Initializes a new `Typedef` instance.

        Args:
            identifier (str): The common name of the new type (e.g., "my_state_t").
            unique_identifier (str): A globally or design_unit-unique identifier for this type
                                     (e.g., "design_unit_name_my_state_t").
            source_interval (Tuple[int, int]): The (start, end) character positions in the source file.
            file_path (str): The absolute or relative path to the file where this typedef is defined.
            data_type (DeclTypes): The category of the type being defined (e.g., `DeclTypes.ENUM_TYPE`,
                                   `DeclTypes.STRUCT_TYPE`, `DeclTypes.UNION_TYPE`).
            element_type (ElementsTypes, optional): The specific type of element in the parsing context.
                                                    Defaults to `ElementsTypes.NONE_ELEMENT`.
        """
        super().__init__(identifier, source_interval, element_type)
        # `declarations` holds a list of `Declaration` objects that make up the
        # members of this typedef (e.g., enum members, struct fields).
        self.declarations: "DeclarationArray" = DeclarationArray()
        self.file_path: str = file_path
        self.unique_identifier: str = unique_identifier
        self.data_type: "DeclTypes" = data_type

    def checkDecl(self, identifier) -> bool:
        decl: Declaration | None = self.declarations.getElement(identifier)
        if decl :
            return True
        return False

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "Typedef":
        """
        Creates a deep copy of the `Typedef` instance.
        Ensures that the `declarations` array is also deep-copied to maintain independence.

        Returns:
            Typedef: A new `Typedef` object with copied attributes and declarations.
        """
        new_typedef = Typedef(
            self.identifier,
            self.unique_identifier,
            self.source_interval,
            self.file_path,
            self.data_type,
            self.element_type,
        )
        new_typedef.declarations = (
            self.declarations.copy()
        )  # Assumes DeclarationArray.copy() is deep
        return new_typedef

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the Typedef.
        The format varies depending on the `data_type` (e.g., ENUM, STRUCT).
        It aims to represent the typedef's structure in a readable way.

        Returns:
            str: The formatted string representation of the typedef.
        """
        result = f"{self.unique_identifier}:"
        indent_level = "\t\t\t"  # Standard indentation for members

        if self.data_type is DeclTypes.ENUM_TYPE:
            result += "(\n"
            member_strings = [
                element.getName() for element in self.declarations.getElements()
            ]
            result += indent_level + (",\n" + indent_level).join(member_strings)
            result += "\n\t\t)"
        elif (
            self.data_type is DeclTypes.STRUCT_TYPE
            or self.data_type is DeclTypes.UNION_TYPE
        ):
            # Assuming UNION_TYPE would also follow a similar structure format
            result += " obj (\n"  # "obj" might indicate an object type, like a struct
            member_strings = [
                element.getAplanDecltype(
                    AplanDeclType.STRUCT
                )  # Assumes this returns a string for struct members
                for element in self.declarations.getElements()
            ]
            result += indent_level + (",\n" + indent_level).join(member_strings)
            result += "\n\t\t)"
        else:
            # Default representation for other types if needed, or raise an error
            result += f" {self.data_type.name}"  # Just print the data type name for simplicity
            if self.declarations:  # If there are declarations for other types, add them
                result += (
                    " {"
                    + ", ".join([str(d) for d in self.declarations.getElements()])
                    + "}"
                )
        return result

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `Typedef` object,
        useful for debugging and introspection.
        """
        return (
            f"Typedef("
            f"identifier={self.identifier!r}, "
            f"unique_identifier={self.unique_identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"file_path={self.file_path!r}, "
            f"data_type={self.data_type!r}, "
            f"element_type={self.element_type!r}, "
            f"declarations={self.declarations!r}"
            f")"
        )


class TypedefArray(BasicArray):
    """
    A specialized array for managing a collection of `Typedef` objects.
    This class extends `BasicArray` and provides comprehensive methods for
    adding, retrieving, and filtering `Typedef` instances based on various criteria.
    """

    def __init__(self):
        """
        Initializes a new `TypedefArray` instance, specifically configured
        to store objects of type `Typedef`.
        """
        super().__init__(Typedef)  # Configure BasicArray to hold Typedef objects

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "TypedefArray":
        """
        Creates a deep copy of the current `TypedefArray` instance.
        It iterates through all contained `Typedef` objects and adds their
        deep copies to the new array, ensuring full independence.

        Returns:
            TypedefArray: A new `TypedefArray` containing deep copies of all
                          original typedefs.
        """
        new_array = TypedefArray()
        for element in self.elements:  # Iterate directly over the internal list
            new_array.addElement(element.copy())  # Use Typedef's deep copy method
        return new_array

    def getLastElement(self) -> Optional["Typedef"]:
        """
        Retrieves the last `Typedef` object added to the array.
        This method delegates to the base `BasicArray`'s implementation.

        Returns:
            Optional[Typedef]: The last `Typedef` element in the array,
                               or None if the array is empty.
        """
        return super().getLastElement()

    def getElementByIndex(self, index: int) -> "Typedef":
        """
        Retrieves a `Typedef` object from the array by its zero-based index.

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            Typedef: The `Typedef` object at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        return self.elements[index]  # Direct list access is efficient

    def getElementsIE(
        self,
        include_type: Optional["ElementsTypes"] = None,
        exclude_type: Optional["ElementsTypes"] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
        file_path: Optional[str] = None,
        include_data_type: Optional["DeclTypes"] = None,
        exclude_data_type: Optional["DeclTypes"] = None,
    ) -> "TypedefArray":
        """
        Filters the `Typedef` objects in the array based on various criteria,
        including `element_type`, `identifier`, `file_path`, and `data_type`.
        This method allows for both inclusion and exclusion criteria for each filter.

        Args:
            include_type (Optional[ElementsTypes]): Only include typedefs with this element type.
            exclude_type (Optional[ElementsTypes]): Exclude typedefs with this element type.
            include_identifier (Optional[str]): Only include typedefs with this common identifier.
            exclude_identifier (Optional[str]): Exclude typedefs with this common identifier.
            file_path (Optional[str]): Only include typedefs defined in this file path.
            include_data_type (Optional[DeclTypes]): Only include typedefs with this data type.
            exclude_data_type (Optional[DeclTypes]): Exclude typedefs with this data type.

        Returns:
            TypedefArray: A new `TypedefArray` containing only the typedefs that
                          match all specified filtering criteria. If no criteria are
                          provided, a deep copy of the original array is returned.
        """
        result_array: "TypedefArray" = TypedefArray()

        # If no filters are specified, return a deep copy of the entire array.
        if all(
            arg is None
            for arg in [
                include_type,
                exclude_type,
                include_identifier,
                exclude_identifier,
                file_path,
                include_data_type,
                exclude_data_type,
            ]
        ):
            return self.copy()

        for element in self.elements:
            # Apply element_type filters
            if include_type is not None and element.element_type is not include_type:
                continue
            if exclude_type is not None and element.element_type is exclude_type:
                continue

            # Apply identifier filters (use `==` for string comparison)
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

            # Apply file_path filter (use `==` for string comparison)
            if file_path is not None and element.file_path != file_path:
                continue

            # Apply data_type filters (use `is` for enum comparison)
            if (
                include_data_type is not None
                and element.data_type is not include_data_type
            ):
                continue
            if exclude_data_type is not None and element.data_type is exclude_data_type:
                continue

            result_array.addElement(element)  # Add the element if it passes all filters
        return result_array

    def findElementWithSource(
        self,
        identifier: str,
        unique_identifier: str,
        source_interval: Tuple[int, int],
    ) -> Optional["Typedef"]:
        """
        Finds a `Typedef` element in the array that matches any of the provided criteria:
        its common identifier, unique identifier, or source interval.
        This function returns the first match found.

        Args:
            identifier (str): The common identifier to match.
            unique_identifier (str): The unique identifier to match.
            source_interval (Tuple[int, int]): The source interval to match.

        Returns:
            Optional[Typedef]: The first `Typedef` object that matches any criterion,
                               or None if no match is found.
        """
        for element in self.elements:
            # Use `==` for content comparison, `is` for identity or enums.
            # `source_interval` is a tuple, so `==` works for value comparison.
            if (
                element.identifier == identifier
                or element.source_interval == source_interval
                or element.unique_identifier == unique_identifier
            ):
                return element
        return None

    def addElement(self, new_element: "Typedef") -> Tuple[bool, int]:
        """
        Adds a new `Typedef` element to the array.
        This method includes a uniqueness check using `findElementWithSource`
        and sorts the internal list of elements after each addition.

        Args:
            new_element (Typedef): The `Typedef` object to add.

        Returns:
            Tuple[bool, int]: A tuple where:
                              - The first element (bool) is True if the element was added,
                                False if a matching element (by `findElementWithSource` criteria)
                                already exists.
                              - The second element (int) is the index of the added or
                                existing element.

        Raises:
            TypeError: If the `new_element` is not an instance of `Typedef`.
        """
        if not isinstance(new_element, self.element_type):
            raise TypeError(
                f"Object should be of type {self.element_type.__name__} but "
                f"you passed an object of type {type(new_element).__name__}. \n"
                f"Object: {new_element!r}"
            )

        # Check for uniqueness based on the criteria in `findElementWithSource`
        is_uniq_element = self.findElementWithSource(
            new_element.identifier,
            new_element.unique_identifier,
            new_element.source_interval,
        )
        if is_uniq_element is not None:
            # If a matching element exists, return False and its index.
            return (False, self.getElementIndex(is_uniq_element.identifier))

        self.elements.append(new_element)

        # The index returned here might not be the actual index after sorting.
        # If the index is critical, you might need to find it again after sorting.
        return (
            True,
            self.getElementIndex(new_element.identifier),
        )  # Re-find index after sort

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `TypedefArray`,
        listing each contained `Typedef` object's string representation on a new line.

        Returns:
            str: A multi-line string containing the formatted typedefs.
        """
        result_parts: List[str] = []
        # No need for manual index check and comma handling if using join
        for element in self.elements:
            result_parts.append(str(element))

        # Join with ",\n" and a tab indent for each new element.
        # This will result in ", " for separator and "\n\t\t" for the start of next line
        # result = ",\n\t\t".join(result_parts) # Original intent seemed to be this.
        # However, the original code had "\t\t" on the first line as well.

        # To match original output style:
        if not result_parts:
            return ""

        # Add initial indent and then join with ",\n\t\t"
        return "\t\t" + (
            ",\n\t\t".join(result_parts)
        )  # Corrected for proper indentation

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `TypedefArray` object,
        displaying the `repr` of its internal elements list for debugging.
        """
        return f"TypedefArray(\n{self.elements!r}\n)"

    # Add standard container methods for better usability and Pythonic behavior
    def __len__(self) -> int:
        """Returns the number of elements in the array. Enables `len(instance)`."""
        return len(self.elements)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union["Typedef", List["Typedef"]]:
        """Allows direct indexing and slicing of the array, e.g., `array[0]` or `array[1:3]`."""
        return self.elements[index]

    def __iter__(self):
        """Makes the array iterable, allowing `for element in array_instance:`."""
        return iter(self.elements)
