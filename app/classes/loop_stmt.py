from typing import Tuple
from ..classes.element_types import ElementsTypes
from ..classes.structure import Structure


class LoopStmt(Structure):
    """
    Represents a generic loop statement or block, often used as a base
    for more specific loop types (like `forever`, `while`, `for` loops).

    It extends `Structure`, inheriting common properties like an identifier,
    source code location, and nesting level. This class marks itself as a loop.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
    ):
        """
        Initializes a new `LoopStmt` instance.

        Args:
            identifier (str): A unique string identifier for this loop statement.
                              This might be a generated ID or a label for the loop.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                                positions of the loop statement in the source code.
            name_space_level (int): The nesting level of this loop statement within
                                    the overall structure or namespace.
        """
        # Call the parent class (Structure) constructor.
        # It sets the element type specifically to LOOP_ELEMENT.
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.LOOP_ELEMENT,
        )
        # A flag to explicitly indicate that this instance represents a loop.
        # While the element_type also indicates this, a boolean flag can be
        # convenient for quick checks.
        self.is_loop: bool = True

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `LoopStmt` object.
        This is useful for debugging and provides a clear view of the object's state,
        including its identifier and inherited sequence number.
        """
        # `identifier` is defined in this class/inherited.
        # `sequence` is assumed to be inherited from the `Basic` or `Structure` base class.
        return (
            f"LoopStmt(identifier={self.identifier!r}, "
            f"name_space_level={getattr(self, 'number', 'N/A')!r}, "  # Assuming name_space_level is stored in 'number'
            f"sequence={getattr(self, 'sequence', 'N/A')!r})"
        )


class ForeverStmt(Structure):
    """
    Represents a 'forever' loop statement, common in hardware description
    languages (e.g., SystemVerilog) for continuous execution.

    It extends `Structure`, inheriting common properties like an identifier,
    source code location, and nesting level. This class specifically
    marks itself as a 'forever' loop.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
    ):
        """
        Initializes a new `ForeverStmt` instance.

        Args:
            identifier (str): A unique string identifier for this forever loop.
                              This might be a generated ID or a label for the loop.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                                positions of the loop statement in the source code.
            name_space_level (int): The nesting level of this forever loop within
                                    the overall structure or namespace.
        """
        # Call the parent class (Structure) constructor.
        # It sets the element type specifically to FOREVER_ELEMENT.
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.FOREVER_ELEMENT,
        )
        # A flag to explicitly indicate that this instance represents a forever loop.
        self.is_forever: bool = True

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `ForeverStmt` object.
        This is useful for debugging and provides a clear view of the object's state,
        including its identifier and inherited sequence number.
        """
        # `identifier` is defined in this class/inherited.
        # `sequence` is assumed to be inherited from the `Basic` or `Structure` base class.
        return (
            f"ForeverStmt(identifier={self.identifier!r}, "
            f"name_space_level={getattr(self, 'number', 'N/A')!r}, "  # Assuming name_space_level is stored in 'number'
            f"sequence={getattr(self, 'sequence', 'N/A')!r})"
        )


class WhileStmt(Structure):
    """
    Represents a 'while' loop statement, a common construct in many
    programming and hardware description languages.

    It extends `Structure`, inheriting common properties like an identifier,
    source code location, and nesting level. This class specifically
    marks itself as a 'while' loop. Additional attributes for the loop's
    condition could be added here if needed.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
    ):
        """
        Initializes a new `WhileStmt` instance.

        Args:
            identifier (str): A unique string identifier for this while loop.
                              This might be a generated ID or a label for the loop.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                                positions of the loop statement in the source code.
            name_space_level (int): The nesting level of this while loop within
                                    the overall structure or namespace.
        """
        # Call the parent class (Structure) constructor.
        # It sets the element type specifically to WHILE_ELEMENT.
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.WHILE_ELEMENT,
        )
        # A flag to explicitly indicate that this instance represents a while loop.
        self.is_while: bool = True

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `WhileStmt` object.
        This is useful for debugging and provides a clear view of the object's state,
        including its identifier and inherited sequence number.
        """
        # `identifier` is defined in this class/inherited.
        # `sequence` is assumed to be inherited from the `Basic` or `Structure` base class.
        return (
            f"WhileStmt(identifier={self.identifier!r}, "
            f"name_space_level={getattr(self, 'number', 'N/A')!r}, "  # Assuming name_space_level is stored in 'number'
            f"sequence={getattr(self, 'sequence', 'N/A')!r})"
        )
