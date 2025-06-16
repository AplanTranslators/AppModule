import re
from typing import TYPE_CHECKING
from app.utils.singleton import SingletonMeta

if TYPE_CHECKING:
    from app.classes.value_parametrs import ValueParametrArray


class StringFormater(metaclass=SingletonMeta):
    def __init__(self):
        pass

    def removeTrailingComma(s: str) -> str:
        """The function `removeTrailingComma` takes a string as input and removes any trailing commas from the
        end of the string.

        Parameters
        ----------
        s : str
            The parameter `s` in the `removeTrailingComma` function is a string (`str`). This function is
        designed to remove any trailing commas from the input string.

        Returns
        -------
            The function `removeTrailingComma` is returning the input string `s` with any trailing commas
        removed.

        """
        return s.rstrip(",")

    def addEqueToBGET(expression: str):
        """The function `addEqueToBGET` takes an input expression, searches for the pattern "BGET(...)" within
        the expression, and replaces it with "BGET(...) == 1".

        Parameters
        ----------
        expression : str

        Returns
        -------
            The function `addEqueToBGET` takes an input expression as a string, searches for any occurrences of
        the pattern "BGET(...)" using regular expressions, and replaces them with "BGET(...) == 1". The
        modified expression is then returned.

        """
        pattern = r"(BGET\(.+\))"
        result = re.sub(pattern, r"\1 == 1", expression)
        return result

    def replaceValueParametrsCalls(param_array: "ValueParametrArray", expression: str):
        """The function `replaceValueParametrsCalls` replaces parameter calls in an expression with their
        corresponding values from a `ValueParametrArray`.

        Parameters
        ----------
        param_array : ValueParametrArray
            A `ValueParametrArray` is a data structure that contains elements representing parameters with
        identifiers and values. The `replaceValueParametrsCalls` function takes a `param_array` and an
        `expression` as input. It iterates over the elements in the `param_array` and replaces occurrences
        of the
        expression : str
            The `replaceValueParametrsCalls` function takes in a `ValueParametrArray` object and a string `expression`.
        It iterates through the elements in the `param_array` and replaces occurrences of the element's
        identifier in the `expression` with the element's value.

        Returns
        -------
            The function `replaceValueParametrsCalls` returns the modified `expression` string after replacing the
        identifiers with their corresponding values from the `param_array`.

        """
        for element in param_array.elements:
            expression = re.sub(
                r"\b{}\b".format(re.escape(element.identifier)),
                str(element.value),
                expression,
            )

        return expression
