from app.utils.logger import Logger


class BaseTranslationManager:
    logger = Logger()

    def setup(self, *args, **kwargs):
        self.logger.warning("Base translation mngr set up function is called!")

    def translate(self):
        self.logger.warning("Base translation mngr transalte function is called!")

        self.logger.delimetr(color="blue")
        return "base"
