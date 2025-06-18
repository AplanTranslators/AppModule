from typing import Tuple
from ..classes.element_types import ElementsTypes
from ..classes.structure import Structure


class IfStmt(Structure):
    """
    Represents an 'if-else if-else' statement block, commonly found in
    programming and hardware description languages (HDL) like SystemVerilog.

    This class extends `Structure`, inheriting properties such as an identifier,
    source code interval, and namespace level. It specifically models the
    counting of 'if' and 'else' branches and helps manage traversal state
    within a conditional block.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        name_space_level: int,
    ):
        """
        Initializes a new `IfStmt` instance.

        Args:
            identifier (str): A unique string identifier for this if statement.
                              This might be a generated ID or the condition itself.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                                positions of the if statement in the source code.
            name_space_level (int): The nesting level of this if statement within
                                    the overall structure or namespace.
        """
        # Call the parent class (Structure) constructor.
        # It sets the element type specifically to IF_STATEMENT_ELEMENT.
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            name_space_level=name_space_level,
        )
        # Counter for 'else' or 'else if' branches encountered.
        self.else_count: int = 0
        # Counter for 'if' or 'else if' conditions.
        self.if_count: int = 0
        # Represents the final step or total number of conditional branches.
        # Calculated in `setCondCount`.
        self.last_step: int = 0
        # Current step or branch being processed (e.g., 1 for initial if, 2 for first else if, etc.)
        self.step: int = 1

    def setCondCount(self, if_count: int, else_count: int):
        """
        Sets the counts for 'if' and 'else' branches within this conditional statement.
        It also calculates `last_step` based on these counts.

        Args:
            if_count (int): The total number of 'if' and 'else if' conditions.
            else_count (int): The total number of 'else' (final) branches.
                              Typically, `else_count` is 0 or 1.
        """
        self.else_count = else_count
        self.if_count = if_count

        # If the number of 'if' branches equals 'else' branches,
        # 'last_step' is set to one more than `if_count`.
        # This might imply `if_count` refers to the number of conditional checks,
        # and `last_step` represents the total paths including the final 'else' if it exists.
        if self.else_count == self.if_count:
            self.last_step = if_count + 1

        # Reset the current processing step to 1 (start of the conditional block).
        self.step = 1

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `IfStmt` object.
        This is useful for debugging and provides a clear view of the object's state,
        including its identifier, internal counters, and inherited sequence number.
        """
        # `identifier` is defined in this class/inherited.
        # `sequence` is assumed to be inherited from the `Basic` or `Structure` base class.
        # Include all relevant counters for debugging conditional flow.
        return (
            f"IfStmt(identifier={self.identifier!r}, "
            f"if_count={self.if_count!r}, "
            f"else_count={self.else_count!r}, "
            f"last_step={self.last_step!r}, "
            f"current_step={self.step!r}, "  # Renamed 'step' to 'current_step' for clarity in repr
            f"sequence={getattr(self, 'sequence', 'N/A')!r})"
        )
