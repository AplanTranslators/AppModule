from typing import List, Optional, Tuple
from .basic import Basic, BasicArray
from .element_types import ElementsTypes
from .value_parametrs import ValueParametrArray
import re


class DesignUnitCall(Basic):
    """
    Represents an instance of a design_unit call (instantiation) in a hardware description
    language (HDL) context (e.g., SystemVerilog design_unit instantiation).

    This class encapsulates information about the design_unit being instantiated,
    the name of the instance, and how its parameters are connected.
    It extends `Basic` for fundamental properties like identifier and source interval.
    """

    @staticmethod
    def extractParametrsAndValues(expression: str) -> List[Tuple[str, str]]:
        """
        Extracts parameter-value assignments from a given string expression.
        It looks for patterns like ".parameter_name(value_expression)".

        Args:
            expression (str): The string containing parameter assignments,
                              e.g., ".WIDTH(SOURCE_WIDTH), .DEPTH(LOCAL_DEPTH)".

        Returns:
            List[Tuple[str, str]]: A list of tuples, where each tuple contains
                                   (parameter_name, value_expression).
        """
        result: List[Tuple[str, str]] = []
        # Regex to find '.PARAM_NAME(VALUE_EXPRESSION)' patterns.
        # Captures PARAM_NAME and VALUE_EXPRESSION.
        # \b ensures word boundary for parameter name.
        matches = re.findall(r"\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.+?)\)", expression)
        for param_name, value_expr in matches:
            result.append((param_name, value_expr))
        return result

    def __init__(
        self,
        identifier: str,  # The unique name of this design_unit *instance*
        object_name: str,  # The name of the *design_unit definition* being called (e.g., 'my_module' in `my_module instance_name(...)`)
        source_identifier: str,  # The identifier from the source definition (e.g., design_unit name)
        destination_identifier: str,  # The identifier in the destination context (e.g., instance name)
        parameter_value_assignment: Optional[str] = None,
        source_parametrs: Optional[ValueParametrArray] = None,
    ):
        """
        Initializes a new `DesignUnitCall` instance.

        Args:
            identifier (str): The unique identifier for this design_unit *instance* (e.g., "U1" or "my_instance").
                              This is also passed to the `Basic` parent.
            object_name (str): The name of the design_unit *definition* being instantiated (e.g., "my_adder").
            source_identifier (str): The identifier of the source component (likely the design_unit being instantiated).
                                     This might be redundant with `object_name` depending on context,
                                     but kept for original intent.
            destination_identifier (str): The identifier of the destination component.
                                          This is often the same as `identifier` but could differ.
            parameter_value_assignment (Optional[str]): A string containing the
                                                        parameter assignments for this call,
                                                        e.g., ".WIDTH(8), .DEPTH(16)". Defaults to None.
            source_parametrs (Optional[ValueParametrArray]): An array of available source parameters
                                                              to resolve values during assignment.
                                                              Defaults to None.
        """
        # Call the parent `Basic` constructor.
        # The source_interval (0,0) suggests that DesignUnitCall instances might not always
        # have a direct textual span, or it's implicitly handled elsewhere.
        super().__init__(
            identifier, (0, 0), element_type=ElementsTypes.MODULE_CALL_ELEMENT
        )  # Added element_type

        self.object_name: str = object_name
        self.source_identifier: str = source_identifier
        self.destination_identifier: str = destination_identifier

        # `paramets` stores `ValueParametr` objects that are associated with this design_unit call.
        self.paramets: ValueParametrArray = ValueParametrArray()

        # If parameter assignments and source parameters are provided, process them.
        if parameter_value_assignment is not None and source_parametrs is not None:
            # Extract parameter name and value expression pairs from the assignment string.
            params_for_assignment = self.extractParametrsAndValues(
                parameter_value_assignment
            )
            # Iterate through extracted assignments
            for target_param_name, source_value_expr in params_for_assignment:
                # Attempt to find the source parameter (by its value expression)
                # in the provided `source_parametrs` array.
                source_parametr = source_parametrs.getElement(source_value_expr)
                if source_parametr is not None:
                    # If found, add the resolved source parameter to this design_unit call's parameters.
                    self.paramets.addElement(source_parametr)

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `DesignUnitCall` object.
        This provides a detailed view of its state for debugging and inspection.
        """
        return (
            f"DesignUnitCall(\n"
            f"\tidentifier={self.identifier!r},\n"
            f"\tobject_name={self.object_name!r},\n"
            f"\tsource_identifier={self.source_identifier!r},\n"
            f"\tdestination_identifier={self.destination_identifier!r},\n"
            f"\tparameters={self.paramets!r},\n"  # Use __repr__ of ValueParametrArray
            f"\tsequence={getattr(self, 'sequence', 'N/A')!r}\n"
            f")"
        )

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `DesignUnitCall` object.
        This provides a concise summary of the design_unit instantiation.
        """
        params_str = ""
        if len(self.paramets) > 0:
            params_str = ", ".join(
                str(p) for p in self.paramets.getElements()
            )  # Assumes ValueParametr has a __str__
            params_str = f" #(.{params_str})"

        return (
            f"{self.object_name} {self.identifier}{params_str} (\n"
            f"  // connections would go here\n"
            f");"
        )


class ModuleCallArray(BasicArray):
    """
    A specialized array for managing a collection of `DesignUnitCall` objects.
    This class extends `BasicArray` and provides specific methods for
    finding and filtering design_unit calls within a design.
    """

    def __init__(self):
        """
        Initializes a new `ModuleCallArray` instance, specifically configured
        to store objects of type `DesignUnitCall`.
        """
        super().__init__(DesignUnitCall)

    def findModuleByUniqIdentifier(self, object_name: str) -> Optional[DesignUnitCall]:
        """
        Finds a `DesignUnitCall` object based on the unique name of the design_unit *definition*
        being instantiated (`object_name`).

        Args:
            object_name (str): The name of the design_unit definition (e.g., "my_adder")
                               to search for among the instantiated modules.

        Returns:
            Optional[DesignUnitCall]: The first `DesignUnitCall` object found that instantiates
                                   a design_unit with the given `object_name`, or `None` if not found.
        """
        for element in self.elements:
            if element.object_name == object_name:
                return element
        return None

    def getElementsIE(
        self,
        include: Optional[ElementsTypes] = None,
        exclude: Optional[ElementsTypes] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
    ) -> "ModuleCallArray":
        """
        Filters and retrieves `DesignUnitCall` elements based on specified inclusion/exclusion criteria.
        This method primarily supports filtering by `ElementsTypes` and instance identifiers.

        Args:
            include (Optional[ElementsTypes]): If provided, only include design_unit calls
                                               of this specific `ElementsTypes`.
            exclude (Optional[ElementsTypes]): If provided, exclude design_unit calls
                                               of this specific `ElementsTypes`.
            include_identifier (Optional[str]): If provided, only include design_unit calls
                                                matching this instance identifier.
            exclude_identifier (Optional[str]): If provided, exclude design_unit calls
                                                matching this instance identifier.

        Returns:
            ModuleCallArray: A new `ModuleCallArray` containing only the filtered elements.
                              Returns a deep copy of the original array if no filters are applied.
        """
        result_array: ModuleCallArray = ModuleCallArray()

        # If no filters are specified, return a deep copy of all elements for consistency.
        if all(
            arg is None
            for arg in [include, exclude, include_identifier, exclude_identifier]
        ):
            return self.copy()  # Use the copy method to ensure deep copy

        for element in self.elements:
            # Apply exclusion filters first
            if exclude is not None and element.element_type is exclude:
                continue
            if (
                exclude_identifier is not None
                and element.identifier == exclude_identifier
            ):
                continue

            # Apply inclusion filters
            if include is not None and element.element_type is not include:
                continue
            if (
                include_identifier is not None
                and element.identifier != include_identifier
            ):
                continue

            # If the element passes all filters, add it to the result.
            result_array.addElement(element)

        return result_array

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `ModuleCallArray` object.
        This is useful for debugging and provides a clear view of the array's contents.
        """
        return f"ModuleCallArray(\n{self.elements!r}\n)"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `ModuleCallArray`.
        Each design_unit call is represented on a new line.
        """
        return "\n".join(str(call) for call in self.elements)

    def __iter__(self):
        """
        Makes the `ModuleCallArray` iterable, allowing direct iteration over its elements
        (e.g., `for call in my_module_calls:`).
        """
        return iter(self.elements)

    def __getitem__(self, index: int) -> DesignUnitCall:
        """
        Enables direct access to elements using square brackets (e.g., `my_array[0]`).

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            DesignUnitCall: The `DesignUnitCall` object at the specified index.
        """
        return self.elements[index]
