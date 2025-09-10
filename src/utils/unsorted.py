import hashlib
import re
import string
from ..logger.logger import Logger, LoggerManager
from ..singleton.singleton import SingletonMeta


class UnsortedUnils(metaclass=SingletonMeta):

    def __init__(self):
        self.logger: Logger = LoggerManager().getLogger(self.__class__.__qualname__)

    def is_interval_contained(self, interval1, interval2):
        start1, end1 = interval1
        start2, end2 = interval2

        return start1 >= start2 and end1 <= end2

    def isNumericString(self, s):
        match = re.fullmatch(r"\d+", s)
        return match.group(0) if match else None

    def containsOnlyPipe(self, s):
        match = re.fullmatch(r"\|", s)
        return True if match else None

    def isVariablePresent(self, expression: str, variable: str) -> bool:
        if len(variable) < 1:
            return False
        pattern = rf"\b{re.escape(variable)}\b"
        return re.search(pattern, expression) is not None

    def extractFunctionName(self, expression: str) -> str:
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

    def vectorSize2AplanVectorSize(
        self, left: str | int | None, right: str | int | None
    ):
        """The function `vectorSize2AplanVectorSize` takes two inputs, left and right, and returns a list with
        the difference between left and right as the first element and right as the second element, unless
        right is "0" in which case left is incremented by 1 and right is set to 0.

        Parameters
        ----------
        left
            The `left` parameter in the `vectorSize2AplanVectorSize` function represents the x-coordinate of a
        vector in a 2D plane.
        right
            The `right` parameter in the `vectorSize2AplanVectorSize` function represents the second component
        of a 2D vector. If `right` is equal to "0", the function increments the first component (`left`) by
        1 and sets the second component to 0. Otherwise

        Returns
        -------
            The function `vectorSize2AplanVectorSize` returns a list containing two elements. The first element
        is the result of subtracting the integer value of `right` from the integer value of `left` if
        `right` is not equal to "0". If `right` is equal to "0", the first element is the integer value of
        `left` incremented by 1. The

        """
        if left is None or right is None:
            self.logger.error("ERROR! One of vector size values is None!")
            raise ValueError

        if right == "0":
            left = int(left) + 1
            return [left, 0]
        else:
            right = int(right)
            left = int(left)
            return [left - right, right]

    def evaluateExpression(self, expr: str, variables=None):
        """The function `evaluateExpression` takes a string representing a mathematical expression, evaluates
        it, and returns the result.

        Parameters
        ----------
        expr : str
            The `evaluateExpression` function takes a string `expr` as input, which represents a mathematical
        expression that can be evaluated using the `eval` function in Python. The function then returns the
        result of evaluating the expression.

        Returns
        -------
            The function `evaluateExpression` takes a string `expr` as input, evaluates the expression using
        the `eval` function, and returns the result of the evaluation.

        """
        if variables is None:
            variables = {}
        result = eval(expr, {}, variables)
        return result

    def extractVectorSize(self, s: str):
        matches = re.findall(r"\[(.+)\s*:\s*(.+)\]", s)
        if matches:
            left = matches[0][0]
            right = matches[0][1]
            left = self.evaluateExpression(left)
            right = self.evaluateExpression(right)
            result = [str(left), str(right)]
            return result

    def extractDimentionSize(self, expression: str):
        if expression == "[$]":
            return

        vector_size = self.extractVectorSize(expression)
        if vector_size is not None:
            aplan_vector_size = self.vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )
            return aplan_vector_size[0]
        else:
            matches = re.findall(r"\[\s*(.+)\s*\]", expression)
            if matches:
                value = matches[0][0]
                value = self.evaluateExpression(value)
                return value

    def containsOperator(self, s):
        match = re.search(r"[+\-*/&|^~<>=%!]", s)
        return match.group(0) if match else None

    def generate_unique_short_id(self, input_string: str) -> str:
        """
        Генерує унікальний 4-символьний ідентифікатор з наданого рядка.

        Використовує перші символи вхідного рядка і доповнює
        випадковими, якщо рядок коротший за 4 символи.
        """
        if not isinstance(input_string, str):
            raise TypeError("Вхідні дані повинні бути рядком.")

        # Використовуємо хеш SHA-256 для отримання детермінованого, але унікального початку.
        # Це забезпечує, що для одного й того ж input_string завжди буде однаковий хеш.
        # Потім кодуємо його в base64 для отримання коротших, друкованих символів.
        # (Це не прямий base64, а використання urlsafe_b64encode для сумісності з URL)
        hash_object = hashlib.sha256(input_string.encode("utf-8"))

        # Використовуємо перші 4 байти хешу як основу
        # Це дозволить отримати більш "випадкові" символи, ніж просто перші символи input_string
        # якщо input_string дуже схожі (наприклад, "test1" і "test2")
        base_chars = hash_object.hexdigest()[:4]

        # Довжина бажаного ідентифікатора
        target_length = 4

        # Доповнюємо, якщо довжина менша за target_length
        if len(base_chars) < target_length:
            # Символи для доповнення: літери та цифри
            fill_chars = string.ascii_letters + string.digits

            # Генеруємо випадкові символи для доповнення
            num_to_add = target_length - len(base_chars)
            random_fill = "".join(random.choice(fill_chars) for _ in range(num_to_add))

            # Об'єднуємо базові символи та випадкове доповнення
            unique_id = base_chars + random_fill
        else:
            # Якщо вже 4 або більше, просто обрізаємо до 4
            unique_id = base_chars[:target_length]

        return unique_id
