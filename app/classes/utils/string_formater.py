from app.classes.utils.singleton import SingletonMeta


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
