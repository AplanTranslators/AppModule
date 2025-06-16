import os
import sys
import time
import traceback
from app.translator.base_translator_mngr import BaseTranslationManager
from app.utils.logger import Logger
from app.utils.singleton import SingletonMeta
from app.program.program import Program
from app.utils.time import TimeUtils


class BaseTool:
    logger = Logger()
    translation_mngr = BaseTranslationManager()
    time_utils = TimeUtils()
    start_time = time.time()
    end_time = 0

    def __init__(
        self,
    ):
        pass

    def is_pass_exist(self, path: str):
        if not os.path.exists(path):
            raise ValueError(f"Path '{path}' does not exist")

    def is_sv_file(self, path: str):
        self.is_pass_exist(path)

        if os.path.isfile(path) and path.endswith(".sv"):
            return True
        else:
            raise ValueError(f"Path '{self.path}' is not a .sv file")

    def start(self, path, path_to_aplan_result):
        result = False
        self.logger.delimetr(
            text="SV TO APLAN TRANSLATOR START",
            color="cyan",
        )
        self.start_time = start_time = time.time()
        tmp = "Program start time: " + self.time_utils.format_time_date_h_m_s(
            self.start_time
        )
        self.logger.info(tmp, "green")
        self.logger.delimetr(
            text="MAIN PROGRAM",
            color="cyan",
        )
        try:
            program = Program(path_to_aplan_result)

            if self.is_sv_file(path):
                file_data = program.readFileData(path)
                self.translation_mngr.setup(file_data)
                self.translation_mngr.translate()

            program.create_result_dirrectory()
            program.create_aplan_files()

        except Exception as e:
            result = True
            self.logger.error("Program finished with error: \n")
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        self.logger.delimetr(
            color="cyan",
        )
        self.end_time = time.time()
        execution_time = self.end_time - start_time
        tmp = "Program end time: " + self.time_utils.format_time_date_h_m_s(
            self.end_time
        )
        self.logger.info(tmp, color="green")
        self.logger.info(
            "Program execution time: "
            + self.time_utils.format_time_m_s(execution_time),
            color="green",
        )
        self.logger.delimetr(text="SV TO APLAN TRANSLATOR END", color="cyan")
        return result
