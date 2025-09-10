from ..classes.basic import Basic, BasicArray


class ActionPrecondition(Basic):
    """
    Represents a single precondition for an action.

    This class extends the `Basic` class, implying it might inherit
    some fundamental properties like an identifier or position,
    though only 'precondition' is explicitly used here.
    """

    def __init__(
        self,
        precondition: str,
    ):
        """
        Initializes an ActionPrecondition instance.

        Args:
            precondition (str): The string description of the precondition.
        """
        self.precondition = precondition
        # Calls the constructor of the parent class 'Basic'.
        # The empty string and (0,0) are placeholder values,
        # suggesting 'Basic' might require these, even if not
        # directly relevant to 'ActionPrecondition's core purpose.
        super().__init__("")

    def __str__(self) -> str:
        """
        Returns the string representation of the precondition.
        When an ActionPrecondition object is converted to a string,
        it will simply return its 'precondition' attribute.
        """
        return self.precondition

    def __repr__(self):
        """
        Returns a developer-friendly string representation of the object.
        This representation includes the class name and the values of
        'identifier' (inherited from Basic) and 'precondition',
        making it useful for debugging.
        """
        # Note: self.identifier is inherited from Basic but not set in __init__
        # for ActionPrecondition specifically, so it will be an empty string
        # as passed to super().__init__.
        return f"ActionPrecondition({self.identifier!r}, {self.precondition!r})\n"


class ActionPreconditionArray(BasicArray):
    """
    Manages a collection of ActionPrecondition objects.

    This class extends `BasicArray`, which likely provides foundational
    methods for handling arrays of specific types of objects.
    """

    def __init__(self):
        """
        Initializes an ActionPreconditionArray instance.
        It configures the array to specifically hold ActionPrecondition objects.
        """
        # Calls the constructor of the parent class 'BasicArray',
        # specifying that this array will contain ActionPrecondition objects.
        super().__init__(ActionPrecondition)

    def __str__(self) -> str:
        """
        Returns a string representation of all preconditions in the array,
        joined by semicolons.
        """
        result = ""
        # Iterates through each ActionPrecondition object in the array.
        for index, element in enumerate(self.getElements()):
            # Adds a semicolon as a separator before each element except the first.
            if index != 0:
                result += ";"
            # Appends the string representation of the current precondition.
            result += str(element)
        return result

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the array.
        This includes the class name and the `repr` of the internal
        'elements' list, which is useful for debugging and introspection.
        """
        # 'self.elements' is likely an internal list managed by BasicArray.
        return f"ActionPreconditionArray(\n{self.elements!r}\t)"
