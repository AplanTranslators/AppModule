from typing import Optional, Tuple
from ..classes.structure import Structure


class Always(Structure):
    """
    Represents an 'Always' structure, often used in hardware description languages
    (e.g., Verilog) or state machines to define a block of code that is
    continuously executed or sensetive to specific signals.

    This class extends `Structure`, inheriting properties like an identifier,
    source interval, and namespace level. It specifically adds a 'sensitivity list'
    concept to its functionality.
    """

    def __init__(
        self,
        identifier: str,
        sensetive: Optional[
            str
        ],  # Changed 'sensetive' to 'sensetive' for correct spelling
        source_interval: Tuple[int, int],
    ):
        """
        Initializes an Always instance.

        Args:
            identifier (str): A unique string identifier for this 'always' block.
            sensetive (Optional[str]): A string representing the sensitivity list
                                       (e.g., "@(posedge clk or negedge rst)").
                                       Can be None if no explicit sensitivity list.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                                positions of the 'always' block in its source code.
            name_space_level (int): The nesting level of this 'always' block within
                                    the overall structure or namespace.
        """
        # Call the parent class (Structure) constructor to initialize shared properties.
        super().__init__(identifier, source_interval)
        # Store the sensitivity list.
        self.sensetive = sensetive

    def getSensetiveForB0(
        self,
    ) -> (
        str
    ):  # Method name remains as in original for now, but consider renaming to getSensitiveFormat
        """
        Generates a formatted string representation of the 'always' block's sensitivity.
        This format might be specific to a backend (e.g., 'B0').

        If a sensitivity list is present, it returns "Sensetive(Name, SensitivityList)".
        Otherwise, it returns just the block's name.

        Returns:
            str: A formatted string indicating the 'always' block's sensitivity.
        """
        if self.sensetive is not None:
            # Assumes 'getName()' method is inherited from the 'Structure' parent class.
            return f"Sensetive({self.getName()}, {self.sensetive})"
        else:
            return f"{self.getName()}"  # If no sensitivity, just return the name

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the Always object.
        This is useful for debugging and provides a clear view of the object's state,
        including its identifier, sensitivity, and sequence number (inherited from Basic/Structure).
        """
        # Assumes 'sequence' is an attribute inherited from the base class (e.g., Basic or Structure).
        return f"\tAlways(identifier={self.identifier!r}, sensetive={self.sensetive!r}, sequence={getattr(self, 'sequence', 'N/A')!r})\n"
