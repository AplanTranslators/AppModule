import re
from typing import Optional, Tuple, List, Union
from ..classes.parametrs import ParametrArray
from ..classes.basic import Basic, BasicArray
from ..classes.actions import ActionParts
from ..classes.element_types import ElementsTypes
from ..classes.structure import Structure


class Task(Basic):
    """
    Represents a hardware design 'task' or 'function', analogous to Verilog tasks/functions.
    A Task encapsulates a set of parameters, a main behavioral structure, and a postcondition.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        namespace_level: int,  # Renamed for consistency with Structure
        element_type: ElementsTypes = ElementsTypes.TASK_ELEMENT,
    ):
        """
        Initializes a new `Task` instance.

        Args:
            identifier (str): The name of the task (e.g., "read_data", "calculate_checksum").
            source_interval (Tuple[int, int]): A tuple (start_position, end_position)
                                                indicating the task's location in source code.
            namespace_level (int): An integer representing the hierarchical scope level of the task.
            element_type (ElementsTypes, optional): The type of the element, defaults to TASK_ELEMENT.
        """
        super().__init__(identifier, source_interval, element_type)

        # `initial_parametrs` might represent parameters at the task definition,
        # while `parametrs` could be actual arguments passed during a call or
        # internal parameters of the task's execution. Clarification needed if distinction is complex.
        self.initial_parametrs: "ParametrArray" = ParametrArray()

        # `structure` holds the main behavioral body of the task.
        # It can be None if the task body is not yet parsed or is empty.
        self.structure: Optional["Structure"] = None

        # `postcondition` likely represents actions or assertions to be performed
        # after the task's main `structure` completes.
        self.postcondition: "ActionParts" = ActionParts()

        # `parametrs` represents the parameters associated with this task instance.
        self.parametrs: "ParametrArray" = ParametrArray()

        # `number` (derived from `namespace_level`) is used for unique naming,
        # especially when flattening or instantiating tasks.
        self.number: int = namespace_level

    def findReturnParam(self) -> bool:
        """
        Checks if a special return parameter (conventionally named `return_<task_identifier>`)
        exists within the task's `parametrs`.

        Returns:
            bool: True if the return parameter is found, False otherwise.
        """
        return_var_name = f"return_{self.identifier}"
        for (
            element
        ) in (
            self.parametrs.getElements()
        ):  # Assumes ParametrArray.getElements() returns iterable
            if element.identifier == return_var_name:
                return True
        return False

    def copy(self) -> "Task":
        """
        Creates a deep copy of the `Task` instance.
        Ensures that all mutable nested objects (`ParametrArray`, `Structure`, `ActionParts`)
        are also deep-copied to maintain independence.

        Returns:
            Task: A new `Task` object with copied attributes.
        """
        new_task = Task(
            self.identifier,
            self.source_interval,
            self.number,  # Use current number
            self.element_type,
        )
        new_task.initial_parametrs = self.initial_parametrs.copy()

        # Deep copy the structure if it exists
        if self.structure:
            new_task.structure = self.structure.copy()
        else:
            new_task.structure = None  # Ensure it's None if original was None

        new_task.postcondition = self.postcondition.copy()
        new_task.parametrs = self.parametrs.copy()
        # self.number is already copied via constructor, but explicitly assigning if it could change later
        new_task.number = self.number
        return new_task

    def getName(self) -> str:
        """
        Returns the primary identifier of the task.
        (Note: If `number` or `parametrs` were intended to be part of the display name,
        similar logic to `Structure.getName` would be needed here).

        Returns:
            str: The identifier of the task.
        """
        return self.identifier

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the Task,
        typically used for display. It formats the task as a call to its
        main structure with its parameters.

        Returns:
            str: A formatted string like "structure_identifier(parameters)".
        """
        if self.structure:
            # Using str(self.parametrs) implicitly calls ParametrArray.__str__
            # Removed trailing comma as it's typically for external joining
            return f"{self.structure.identifier}({self.parametrs})"
        else:
            # Provide a fallback if structure is None
            return f"{self.identifier}({self.parametrs})"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `Task` object,
        displaying its key attributes for debugging and introspection.
        """
        return (
            f"Task("
            f"identifier={self.identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"element_type={self.element_type!r}, "
            f"namespace_level={self.number!r}, "  # Use self.number
            f"initial_parametrs={self.initial_parametrs!r}, "
            f"structure={self.structure!r}, "
            f"postcondition={self.postcondition!r}, "
            f"parametrs={self.parametrs!r}"
            f")"
        )


class TaskArray(BasicArray):
    """
    A specialized array for managing a collection of `Task` objects.
    This class extends `BasicArray` and provides methods for filtering
    and managing `Task` instances.
    """

    def __init__(self):
        """
        Initializes a new `TaskArray` instance, specifically configured
        to store objects of type `Task`.
        """
        super().__init__(Task)  # Configure BasicArray to hold Task objects

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "TaskArray":
        """
        Creates a deep copy of the current `TaskArray` instance.
        It iterates through all contained `Task` objects and adds their
        deep copies to the new array, ensuring full independence.

        Returns:
            TaskArray: A new `TaskArray` containing deep copies of all
                       original tasks.
        """
        new_array = TaskArray()
        for element in self.elements:  # Iterate directly over the internal list
            new_array.addElement(element.copy())  # Use Task's deep copy method
        return new_array

    def getElement(self, identifier: str) -> Optional["Task"]:
        """
        Retrieves a `Task` element from the array by its identifier.
        This method delegates to the base `BasicArray`'s implementation.

        Args:
            identifier (str): The identifier of the task to retrieve.

        Returns:
            Optional[Task]: The `Task` object if found, otherwise None.
        """
        # This explicitly calls the parent's getElement method
        return super().getElement(identifier)

    # --- Consolidated getElementsIE method ---
    # The original code had two getElementsIE methods, one of which was more comprehensive.
    # This consolidated version uses the parameters from the more comprehensive one
    # and delegates to the BasicArray's method, as that's the intended common filtering logic.
    def getElementsIE(
        self,
        include_type: Optional["ElementsTypes"] = None,
        exclude_type: Optional["ElementsTypes"] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
    ) -> "TaskArray":
        """
        Filters the tasks in the array based on their `element_type`
        and/or `identifier`. This method allows for both inclusion and exclusion criteria.
        It leverages the filtering capabilities of the base `BasicArray` class.

        Args:
            include_type (Optional[ElementsTypes]): Only include tasks with this element type.
            exclude_type (Optional[ElementsTypes]): Exclude tasks with this element type.
            include_identifier (Optional[str]): Only include tasks with this identifier.
            exclude_identifier (Optional[str]): Exclude tasks with this identifier.

        Returns:
            TaskArray: A new `TaskArray` containing only the tasks that
                            match the specified filtering criteria. If no criteria are
                            provided, a deep copy of the original array is returned.
        """
        # Delegate to the comprehensive filtering logic in the base BasicArray class.
        # BasicArray.getElementsIE should return a BasicArray, which we then cast to TaskArray.
        # This assumes BasicArray's getElementsIE is already designed to return a new
        # BasicArray instance of the same specialized type if that's how it's overridden.
        # If BasicArray.getElementsIE returns BasicArray, then we need to iterate and add.

        # Simpler approach if BasicArray's getElementsIE returns a new BasicArray:
        filtered_basic_array = super().getElementsIE(
            include=include_type,
            exclude=exclude_type,
            include_identifier=include_identifier,
            exclude_identifier=exclude_identifier,
        )

        # Convert BasicArray to TaskArray by copying elements over
        result_array = TaskArray()
        for element in filtered_basic_array.getElements():
            if isinstance(
                element, Task
            ):  # Ensure type safety if BasicArray can hold mixed types
                result_array.addElement(element)
        return result_array

    def isUniqAction(
        self, task_to_check: "Task"
    ) -> Tuple[Optional[str], Tuple[Optional[int], Optional[int]]]:
        """
        Checks if a given `Task` object is considered "unique" within this array.
        The uniqueness criteria is based on direct object equality (`==` operator),
        which implies that the `Task` class must implement `__eq__` for content comparison.

        Args:
            task_to_check (Task): The `Task` object to check for uniqueness.

        Returns:
            Tuple[Optional[str], Tuple[Optional[int], Optional[int]]]:
            - If a matching task is found: (identifier, (start_interval, end_interval))
            - If no matching task is found: (None, (None, None))
        """
        for element in self.elements:
            # This relies on the Task class having a meaningful __eq__ method
            # to compare task content (e.g., structure, parameters, postcondition).
            if element == task_to_check:
                return (element.identifier, element.source_interval)
        return (None, (None, None))

    def getFunctions(self) -> List["Task"]:
        """
        Retrieves a list of `Task` objects that are specifically identified as
        functions (i.e., `element_type` is `ElementsTypes.FUNCTION_ELEMENT`).

        Returns:
            List[Task]: A list of `Task` instances representing functions.
        """
        result: List["Task"] = []
        # Iterate directly over self.elements as getElements() might create a copy
        for element in self.elements:
            if element.element_type == ElementsTypes.FUNCTION_ELEMENT:
                result.append(element)
        return result

    def getLastTask(self) -> Optional["Task"]:
        """
        Retrieves the last `Task` object added to the array.

        Returns:
            Optional[Task]: The last `Task` element in the array, or None if the array is empty.
        """
        if self.elements:  # Check if the list is not empty
            return self.elements[-1]
        return None

    def __len__(self) -> int:
        """Returns the number of elements in the array. Enables `len(instance)`."""
        return len(self.elements)

    def __getitem__(self, index: Union[int, slice]) -> Union["Task", List["Task"]]:
        """Allows direct indexing and slicing of the array, e.g., `array[0]` or `array[1:3]`."""
        return self.elements[index]

    def __iter__(self):
        """Makes the array iterable, allowing `for element in array_instance:`."""
        return iter(self.elements)

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `TaskArray` object,
        displaying the `repr` of its internal elements list.
        """
        return f"TaskArray(\n{self.elements!r}\n)"


class TaskStmt(Structure):
    """
    Represents a specific type of `Structure` that is inherently a `TASK_ELEMENT`.
    This class might be used to specifically mark a `Structure` that serves as
    the body of a Verilog task or function, ensuring its `element_type` is correctly set.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        namespace_level: int,  # Renamed for consistency
    ):
        """
        Initializes a new `TaskStmt` instance. It calls the `Structure`
        constructor, explicitly setting its `element_type` to `ElementsTypes.TASK_ELEMENT`.

        Args:
            identifier (str): The name of the task statement/structure.
            source_interval (Tuple[int, int]): The source code interval of the statement.
            namespace_level (int): The hierarchical namespace level of this statement.
        """
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.TASK_ELEMENT,  # Fixed type for TaskStmt
            namespace_level=namespace_level,
        )

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `TaskStmt` object.
        Corrected to reflect its actual type.
        """
        # The original __repr__ was for IfStmt, corrected to TaskStmt
        return (
            f"TaskStmt("
            f"identifier={self.identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"namespace_level={self.number!r}"  # Use self.number inherited from Structure
            f")"
        )
