import difflib
import json
import shutil
import sys
import os
from typing import Dict, List

from ..utils.logger import Logger
from ..utils.singleton import SingletonMeta

import glob

ExampleEntry = Dict[str, str]


class FilesMngr(metaclass=SingletonMeta):
    logger = Logger()

    def is_pass_exist(self, path: str):
        if not os.path.exists(path):
            raise ValueError(f"Path '{path}' does not exist")

    def is_testing_file(self, path: str, language_type: str):
        self.is_pass_exist(path)

        if os.path.isfile(path) and path.endswith(f".{language_type}"):
            return True
        else:
            raise ValueError(f"Path '{path}' is not a .{language_type} file")

    def compare(self, file1_path, file2_path):
        with open(file1_path, "r", encoding="utf-8") as file1, open(
            file2_path, "r", encoding="utf-8"
        ) as file2:
            file1_lines = file1.readlines()
            file2_lines = file2.readlines()

        diff = difflib.unified_diff(
            file1_lines,
            file2_lines,
            fromfile=file1_path,
            tofile=file2_path,
            lineterm="",
        )
        differences = list(diff)

        return differences

    def compareAplanByPathes(
        self, path1, path2, extensions_to_compare: str | None = None
    ):
        result = False
        if extensions_to_compare == None:
            extensions_to_compare = [".act", ".behp", ".env_descript", ".evt_descript"]
        for ext in extensions_to_compare:
            files1 = glob.glob(os.path.join(path1, "*" + ext))
            files2 = glob.glob(os.path.join(path2, "*" + ext))

            for file1 in files1:
                filename = os.path.basename(file1)
                file2 = os.path.join(path2, filename)
                if file2 in files2:
                    differences = self.compare(file1, file2)
                    if differences:
                        self.logger.error(f"File {filename} differences:")
                        for diff in differences:
                            self.logger.error(f"{diff}")
                        result = True
                    else:
                        self.logger.info(
                            f"Files {filename} are the same ", color="blue"
                        )
                else:
                    self.logger.error(f"File {filename} not found in {path2}")

        return result

    def remove_directory(self, directory_path):
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            shutil.rmtree(directory_path)
            self.logger.info(
                f"Directory {directory_path} has been removed.\n", color="bold_yellow"
            )
        else:
            self.logger.warning(f"Directory {directory_path} does not exist.\n")

    def load_examples_from_json(self, filepath: str) -> List[ExampleEntry]:
        if not os.path.exists(filepath):
            self.logger.warning(
                f"JSON file not found at '{filepath}'. Returning empty list."
            )
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise TypeError("JSON file should contain a list of example objects.")

        return data
