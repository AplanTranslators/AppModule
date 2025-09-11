from ..logger.logger import Logger


class BaseTranslationManager:

    def __init__(self):
        self.logger: Logger = Logger(self.__class__.__qualname__)

    def setup(self, *args, **kwargs):
        self.logger.warning("Base translation mngr set up function is called!")

    def translate(self):
        self.logger.warning("Base translation mngr transalte function is called!")

        self.logger.delimetr(color="blue")
        return "base"
