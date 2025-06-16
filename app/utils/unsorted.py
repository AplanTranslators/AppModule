import re
from app.utils.singleton import SingletonMeta


class UnsortedUnils(metaclass=SingletonMeta):
    def is_interval_contained(interval1, interval2):
        start1, end1 = interval1
        start2, end2 = interval2

        return start1 >= start2 and end1 <= end2

    def isNumericString(s):
        match = re.fullmatch(r"\d+", s)
        return match.group(0) if match else None

    def containsOnlyPipe(s):
        match = re.fullmatch(r"\|", s)
        return True if match else None

    def isVariablePresent(expression: str, variable: str) -> bool:
        if len(variable) < 1:
            return False
        pattern = rf"\b{re.escape(variable)}\b"
        return re.search(pattern, expression) is not None

    def extractFunctionName(expression: str) -> str:
        """
        Extracts the function name from a given expression.

        Parameters
        ----------
        expression : str
            The input string containing the function call.

        Returns
        -------
        str
            The name of the function if found, otherwise an empty string.
        """
        pattern = r"\b([\w$]+)\s*\("
        match = re.search(pattern, expression)
        if match:
            return match.group(1)
        return None
