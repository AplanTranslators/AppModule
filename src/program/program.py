from pathlib import Path
from ..utils.counters import Counters
from ..logger.logger import AplanLogger, Logger
from ..utils.string_formater import StringFormater
from ..program.beh import create_Beh_File
from ..program.action import create_Action_File
from ..program.env import generateEnv
from ..program.evt import generateEvt
from ..singleton.singleton import SingletonMeta
from ..classes.typedef import TypedefArray
from ..classes.design_unit import DesignUnitArray
from ..classes.design_unit_call import DesignUnitCallArray
import os


class Program(metaclass=SingletonMeta):
    str_formater = StringFormater()
    counters = Counters()

    def __init__(self, result_path: Path | None = None) -> None:

        self.design_units: DesignUnitArray = DesignUnitArray()
        self.DesignUnit: DesignUnitCallArray = DesignUnitCallArray()
        self._typedefs: TypedefArray = TypedefArray()

        self.logger: Logger = Logger(self.__class__.__qualname__)
        self.aplan_logger = AplanLogger(result_path)

    @property
    def result_path(self) -> Path:
        return self.aplan_logger.result_path

    @property
    def design_units_calls(self) -> DesignUnitCallArray:
        return self.DesignUnit

    @property
    def typedefs(self) -> TypedefArray:
        return self._typedefs

    def readFileData(self, path):
        self.file_path = path
        self.logger.delimetr(color="blue", text=f"Read file {path}")

        f = open(path, "r")
        data = f.read()
        f.close()
        return data

    def write_to_file(self, path, data):
        f = open(path, "w")
        f.write(data)
        f.close()

    def generateAplan(self):
        generateEvt(self)
        generateEnv(self)
        create_Action_File(self)
        create_Beh_File(self)
        self.logger.info(
            "The translation was successfully completed! \n", "bold_yellow"
        )
        self.counters.deinit()
