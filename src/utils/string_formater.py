from ast import literal_eval
import os
import re
from typing import TYPE_CHECKING
from ..logger.logger import Logger, LoggerManager
from ..singleton.singleton import SingletonMeta

if TYPE_CHECKING:
    from ..classes.value_parametrs import ValueParametrArray


class StringFormater(metaclass=SingletonMeta):

    def __init__(self):
        logger_manager = LoggerManager()
        self.logger: Logger = logger_manager.getLogger(self.__class__.__qualname__)

    # NEED UNIT TESTS
    def tokenizeExpression(self, expression):
        """
        Splits an expression string into tokens: identifiers, numbers, and other characters.

         Args:
             expression (str): SystemVerilog expression string.

         Returns:
             list: List of tokens.
        """
        # Regex pattern to search for IDs, numbers, or any other character.
        # r'(\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b|.)'
        # 1. \b[a-zA-Z_][a-zA-Z0-9_]*\b - searches for identifiers (words that do not start with a number)
        # 2. \b\d+\b - looking for numbers
        # 3. . - searches for any other character
        pattern = r"(\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b|.)"

        # re.findall() returns a list of all match groups found.
        # filter(None, ...) removes any blank lines that may appear.
        tokens = [t for t in re.findall(pattern, expression) if t.strip()]

        return tokens

    def removeTrailingComma(self, s: str) -> str:
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

    def addEqueToBGET(self, expression: str):
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

    def replaceValueParametrsCalls(
        self, param_array: "ValueParametrArray", expression: str
    ):
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

    def addSpacesAroundOperators(self, expression: str):
        """The function `addSpacesAroundOperators` adds spaces around operators in a given input expression.

        Parameters
        ----------
        expression : str
            The `addSpacesAroundOperators` function takes an input expression as a string and adds spaces
        around operators in the expression. This makes the expression more readable and easier to parse.

        Returns
        -------
            The `addSpacesAroundOperators` function returns the input expression with spaces added around the
        operators specified in the `operators` list.

        """
        operators = [
            r"\+",
            r"-",
            r"\*",
            r"/",
            r"%",
            r"\^",
            r"==",
            r"!=",
            r">=",
            r"<=",
            r">",
            r"<",
            r"&&",
            r"\|\|",
            r"&",
            r"\|",
            r"\(",
            r"\)",
            r"=",
            r"\?",
        ]
        pattern = "|".join(operators)

        spaced_expression = re.sub(f"({pattern})", r" \1 ", expression)
        spaced_expression = re.sub(r"\s+", " ", spaced_expression).strip()
        spaced_expression = re.sub(r",\s*", ", ", spaced_expression)

        return spaced_expression

    def valuesToAplanStandart(self, expression: str) -> str:
        """The function `valuesToAplanStandart` converts values in different number systems to their standard
        representation.

        Parameters
        ----------
        expression : str
            The function `valuesToAplanStandart` takes an input expression as a string and converts any values
        specified in non-standard formats to their standard representation. The function uses regular
        expressions to identify different value patterns such as binary, hexadecimal, and decimal values.

        Returns
        -------
            The function `valuesToAplanStandart` takes an input expression as a string and processes it to
        convert any values specified in non-standard formats to standard integer values. The function uses
        regular expressions to identify different patterns for binary, hexadecimal, and decimal values. It
        then converts these values to standard integer format and returns the modified input expression as a
        string.

        """
        values_patterns = [
            r"([0-9]+)\'(b)([01]+)",  # for binary
            r"([0-9]+)\'(h)([a-fA-F0-9]+)",  # for hex
            r"()(\')([0-9]+)",  # for '0
        ]

        pattern = "|".join(values_patterns)

        def replace_match(match):
            for i in range(len(values_patterns)):
                multiplier = 0
                if i > 0:
                    multiplier = 3 * (i)
                base, value_type, value_string = (
                    match.group(1 + multiplier),
                    match.group(2 + multiplier),
                    match.group(3 + multiplier),
                )
                if base is not None:
                    break
            if value_type == "h":
                value_string = "0x" + value_string
            elif value_type == "b":
                value_string = "0b" + value_string
            value = literal_eval(value_string)
            return str(value)

        expression = re.sub(pattern, lambda match: replace_match(match), expression)
        expression = str(expression)
        expression = expression.replace("'", "")
        return expression

    def addBracketsAfterNegation(self, expression: str):
        """The function `addBracketsAfterNegation` adds brackets after the negation symbol `!` in a given input
        expression.

        Parameters
        ----------
        expression : str

        Returns
        -------
            The function `addBracketsAfterNegation` returns the input expression with brackets added after the
        negation symbol `!`.

        """
        pattern = r"!([^\s]*)"
        result = re.sub(pattern, r"!(\1)", expression)
        return result

    def addLeftValueForUnaryOrOperator(self, expression: str):
        """The function adds a left value for a unary or operator in a given input expression.

        Parameters
        ----------
        expression : str

        Returns
        -------
            The function `addLeftValueForUnaryOrOperator` returns a modified version of the input expression
        where a prefix is added before any occurrence of the `|` operator that is not preceded by a letter,
        number, or underscore.

        """
        prefix = expression.split("=")[0].strip()

        pattern = re.compile(r"(?<![a-zA-Z0-9_])\|")

        new_expression = pattern.sub(f"{prefix}|", expression)

        return new_expression

    def addBracketsAfterTilda(self, expression: str):
        """The function `addBracketsAfterTilda` adds brackets `()` after the tilde `~` in a given input
        expression.

        Parameters
        ----------
        expression : str

        Returns
        -------
            The function `addBracketsAfterTilda` takes an input expression as a string and adds brackets `()`
        after the tilde `~` symbol. The function uses a regular expression pattern to match the tilde
        followed by any non-space characters and then replaces it with the tilde followed by the matched
        non-space characters enclosed in brackets.

        """
        pattern = r"~([^\s]*)"
        result = re.sub(pattern, r"~(\1)", expression)
        return result

    def parallelAssignment2Assignment(self, expression: str):
        """The function `parallelAssignment2Assignment` replaces the "<=" operator with "=" in a given input
        expression.

        Parameters
        ----------
        expression : str

        Returns
        -------
            The function `parallelAssignment2Assignment` takes an input expression as a string, searches for
        the pattern `<=` in the expression, and replaces it with `=`. The modified expression is then
        returned.

        """
        pattern = r"<="
        result = re.sub(pattern, "=", expression)
        return result

    def doubleOperators2Aplan(self, expression: str) -> str:
        """Replaces increment and decrement operators with their assignment equivalents."""

        # 1. Заміна '++'
        def replace_increment(match):
            variable = match.group(1)
            return f"{variable} = {variable} + 1"

        result = re.sub(r"(\w+)\s*\+\+", replace_increment, expression)

        # 2. Заміна '--'
        def replace_decrement(match):
            variable = match.group(1)
            return f"{variable} = {variable} - 1"

        result = re.sub(r"(\w+)\s*\-\-", replace_decrement, result)

        return result

    def notConcreteIndex2AplanStandart(self, expression: str, design_unit):
        """The function `notConcreteIndex2AplanStandart` takes an expression and a design_unit, and replaces
        specific index references with function calls based on the design_unit's declarations.

        Parameters
        ----------
        expression : str
            The `expression` parameter is a string that represents an expression containing array accesses in
        the format `identifier[index]`. The function `notConcreteIndex2AplanStandart` is designed to modify
        these array accesses based on certain conditions.
        design_unit
            The `design_unit` parameter in the `notConcreteIndex2AplanStandart` function is expected to be an object
        that contains declarations with dimensions. The function uses this design_unit to find a declaration with
        a dimension by name and then performs a specific replacement in the given expression based on the
        match found.

        Returns
        -------
            The function `notConcreteIndex2AplanStandart` takes an expression and a design_unit as input parameters.
        It searches for a specific pattern in the expression, where a word followed by a dot and another
        word is followed by square brackets containing an index.

        """
        pattern = r"(\w+\.\w+)\[([^\[\]]*[a-zA-Z][^\[\]]*)\]"

        def replace_match(match):
            identifier, index = match.group(1), match.group(2)
            tmp = identifier.split(".")
            decl_with_dimention = design_unit.declarations.findDeclWithDimentionByName(
                tmp[1]
            )
            if decl_with_dimention is not None:
                return f"{identifier}({index})"
            else:
                return f"BGET({identifier}, {index})"

        result = re.sub(pattern, lambda match: replace_match(match), expression)
        return result

    def vectorSizes2AplanStandart(self, expression: str):
        """The function `vectorSizes2AplanStandart` in the provided Python code snippet converts vector size
        expressions to a standard format.

        Parameters
        ----------
        expression : str
            The function `vectorSizes2AplanStandart` takes an expression as input and processes it based on
        certain patterns defined in the function. The patterns are used to identify specific formats within
        the expression, such as `[x]` or `[x:y]`, where `x` and `y`

        Returns
        -------
            The function `vectorSizes2AplanStandart` takes an input `expression` as a string and processes it
        based on certain patterns related to vector sizes. It uses regular expressions to match patterns
        like `[number]` or `[number : number]` and then replaces them with a modified format. The function
        then returns the modified expression.

        """
        patterns = [r"\[(\d+)\]", r"\[(\d+)\s*:\s*(\d+)\]"]

        pattern = "|".join(patterns)

        def replace_match(match):
            for i in range(len(patterns)):
                value_1, value_2 = (
                    match.group(1 + i),
                    match.group(2 + i),
                )
                if value_1 is not None:
                    break
            if value_2 is None:
                value = f"({value_1})"
            else:
                value = f"({value_2},{value_1})"
            return value

        expression = re.sub(pattern, lambda match: replace_match(match), expression)

        return expression

    def generatePythonStyleTernary(self, expression: str):
        pattern = (
            r"\((?P<condition>.+)\)\s*\?\s*(?P<true_value>.+)\s*:\s*(?P<false_value>.+)"
        )
        match = re.match(pattern, expression)

        if match:
            condition = match.group("condition").strip()
            true_value = match.group("true_value").strip()
            false_value = match.group("false_value").strip()
            expression = f"({true_value} if {condition} else {false_value})"
            return expression
        else:
            return expression

    def replace_cpp_operators(self, expression: str) -> str:
        """
        Converts C++ logical and arithmetic operators to their Python equivalents,
        handling spaces and increment/decrement operators.
        """
        # 1. Заміна інкрементних/декрементних операторів
        # Це необхідно зробити першими, щоб уникнути конфліктів з іншими замінами

        # Заміна '++' на '+= 1'
        expression = re.sub(r"(\w+)\s*\+\+", r"\1 += 1", expression)

        # Заміна '--' на '-= 1'
        expression = re.sub(r"(\w+)\s*--", r"\1 -= 1", expression)

        # 2. Заміна логічних операторів з урахуванням пробілів
        # Використовуємо захоплення груп для збереження пробілів
        replacements = {
            # Заміна && на 'and'
            r"(\s*)\&\&(\s*)": r" and ",
            # Заміна || на 'or'
            r"(\s*)\|\|(\s*)": r" or ",
            # Заміна / на '//'
            r"(\s*)/(\s*)": r" // ",
            # Заміна / на '//'
            r"(\s*)!(\s*)": r" not ",
        }

        for pattern, replacement in replacements.items():
            expression = re.sub(pattern, replacement, expression)

        # 3. Заміна оператора '!' на 'not'
        # Додаємо пробіл після 'not'
        # expression = re.sub(r"!", " not ", expression)

        # 4. Заміна булевих значень
        expression = expression.replace("true", "True").replace("false", "False")

        return expression
