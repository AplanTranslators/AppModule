import os
import sys
import time
import traceback
from typing import Literal
from app.translator.base_translator_mngr import BaseTranslationManager
from app.utils.file_manager import FilesMngr
from app.utils.logger import Logger
from app.utils.singleton import SingletonMeta
from app.program.program import Program
from app.utils.time import TimeUtils


class BaseTool(metaclass=SingletonMeta):
    logger = Logger()
    translation_mngr = BaseTranslationManager()
    time_utils = TimeUtils()
    file_manager = FilesMngr()
    name = ""
    _type = None

    def __init__(self, name: str = "Tool"):
        self.name = name
        pass

    def setType(self, i_type):
        self._type = i_type

    def start(self, path, path_to_aplan_result):
        if not self._type:
            self.logger.error("Select type for translator")
            return False
        result = False
        self.logger.delimetr(
            text=f"{self.name.upper()} START",
            color="cyan",
        )
        start_time = time.time()
        tmp = "Program start time: " + self.time_utils.format_time_date_h_m_s(
            start_time
        )
        self.logger.info(tmp, "green")
        self.logger.delimetr(
            text="MAIN PROGRAM",
            color="cyan",
        )
        try:
            program = Program(path_to_aplan_result)

            if self.file_manager.is_testing_file(path, self._type.lower()):
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
        end_time = time.time()
        execution_time = end_time - start_time
        tmp = "Program end time: " + self.time_utils.format_time_date_h_m_s(end_time)
        self.logger.info(tmp, color="green")
        self.logger.info(
            "Program execution time: "
            + self.time_utils.format_time_m_s(execution_time),
            color="green",
        )
        self.logger.delimetr(
            text=f"{self._type.upper()} {self.name.upper()} END", color="cyan"
        )
        return result

    def run_test(self, test_number, source_file, result_path, aplan_code_path):
        result = False
        self.logger.delimetr(
            text=f"TEST {test_number}",
            color="purple",
        )
        test_start_time = time.time()
        try:
            self.logger.info(f"Source file : {source_file} \n", color="blue")
            self.logger.activate()
            result = self.start(source_file, result_path)
            self.logger.deactivate()

            if result:
                self.logger.error(f"Test {test_number} finished with error: ")

            differences_found = self.file_manager.compareAplanByPathes(
                aplan_code_path, result_path
            )
            if differences_found:
                self.logger.error(f"Test {test_number} found differences.")
                result = True
        except Exception as e:
            self.logger.error(
                f"Test {test_number} finished with error:",
            )
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
            result = True
        finally:
            self.file_manager.remove_directory(result_path)
            test_end_time = time.time()
            test_execution_time = test_end_time - test_start_time
            self.logger.info(
                f"Test {test_number} execution time: "
                + self.time_utils.format_time_date_h_m_s(test_execution_time),
                color="green",
            )
            self.logger.delimetr(color="cyan")
        return result

    def tests_start(self, examples_list_path):
        all_examples = self.file_manager.load_examples_from_json(examples_list_path)
        failed_tests = []

        self.logger.delimetr(
            text="TESTS START",
            color="purple",
        )

        start_time = time.time()
        self.logger.info(
            "Testing start time: " + self.time_utils.format_time_m_s(start_time),
            color="green",
        )

        for test_number, data in enumerate(all_examples):
            source_file = data["file"]
            result_path = data["result_dir"]
            aplan_code_path = data["aplan_dir"]
            if self.run_test(
                test_number + 1, source_file, result_path, aplan_code_path
            ):
                failed_tests.append((test_number + 1, source_file))

        end_time = time.time()
        execution_time = end_time - start_time
        self.logger.info(
            "Testing end time: " + self.time_utils.format_time_m_s(end_time),
            color="green",
        )
        self.logger.info(
            "Testing execution time: "
            + self.time_utils.format_time_date_h_m_s(execution_time),
            color="green",
        )

        if not failed_tests:
            self.logger.delimetr(text="TESTS SUCCESS", color="purple")
            return 0
        else:
            self.logger.delimetr(text="TESTS FAILED", color="bold_red")
            self.logger.critical(f"Errors in tests: {failed_tests}\n")
            return 1

    def run_generation(self, test_number, source_file, result_path):
        result = False
        self.logger.info(
            text=f"GENERATION {test_number}",
            color="purple",
        )

        gen_start_time = time.time()
        try:
            self.logger.info(f"Source file : {source_file} ", color="blue")
            self.logger.activate()
            result = self.start(source_file, result_path)
            self.logger.deactivate()
        except Exception as e:
            self.logger.error(f"Generation {test_number} finished with error:")
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
            return True
        finally:
            gen_execution_time = time.time() - gen_start_time
            self.logger.info(
                "Generation  execution time: "
                + self.time_utils.format_time_date_h_m_s(gen_execution_time),
                color="green",
            )
            self.logger.delimetr(color="cyan")
        return result

    def regeneration_start(self, examples_list_path=None, path_to_sv=None):
        failed_generations = []
        self.logger.info(
            text="GENERATON START",
            color="purple",
        )
        start_time = time.time()
        start_time = time.time()
        self.logger.info(
            "Generation process start time: "
            + self.time_utils.format_time_m_s(start_time),
            color="green",
        )

        if path_to_sv is None:
            all_examples = self.file_manager.load_examples_from_json(examples_list_path)
            for test_number, data in enumerate(all_examples):
                source_file = data["file"]
                unused_path = data["result_dir"]
                result_path = data["aplan_dir"]
                if self.run_generation(test_number + 1, source_file, result_path):
                    failed_generations.append(test_number + 1)
        else:
            directory = os.path.dirname(path_to_sv)
            source_file = path_to_sv
            result_path = os.path.join(directory, "aplan")
            if self.run_generation(1, source_file, result_path):
                failed_generations.append(1)

        end_time = time.time()
        execution_time = end_time - start_time

        self.logger.info(
            "Generation process end time: " + self.time_utils.format_time_m_s(end_time),
            color="green",
        )
        self.logger.info(
            "Generation process execution time: "
            + self.time_utils.format_time_date_h_m_s(execution_time),
            color="green",
        )

        if not failed_generations:
            self.logger.delimetr("GENERATON SUCCESS", color="purple")
            return 0
        else:
            self.logger.delimetr("GENERATON FAILED", color="bold_red")
            self.logger.critical(f"Errors in generations: {failed_generations}")
            return 1
