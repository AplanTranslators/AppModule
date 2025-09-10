from ..utils.counters import Counters
from ..logger.logger import Logger, LoggerManager
from ..utils.string_formater import StringFormater
from ..program.beh import create_Beh_File
from ..program.action import create_Action_File
from ..program.env import create_ENV_File
from ..program.evt import create_EVT_File
from ..singleton.singleton import SingletonMeta
from ..classes.typedef import TypedefArray
from ..classes.design_unit import DesignUnitArray
from ..classes.design_unit_call import DesignUnitCallArray
import os


class Program(metaclass=SingletonMeta):
    str_formater = StringFormater()
    counters = Counters()

    def __init__(self, path_to_result: str = None) -> None:
        self.path_to_result = path_to_result
        self.design_units: DesignUnitArray = DesignUnitArray()
        self.DesignUnit: DesignUnitCallArray = DesignUnitCallArray()
        self._typedefs: TypedefArray = TypedefArray()
        self.logger: Logger = LoggerManager().getLogger(self.__class__.__qualname__)

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

    def create_result_dirrectory(self):
        if self.path_to_result is not None:
            last_char = self.path_to_result[-1]
            if last_char != os.sep:
                self.path_to_result += os.sep
        else:
            self.path_to_result = "results" + os.sep

        self.logger.info(
            'Path to result: "{0}"\n'.format(self.path_to_result), "bold_yellow"
        )

        if not os.path.exists(self.path_to_result[:-1]):
            os.mkdir(self.path_to_result[:-1])

    def write_to_file(self, path, data):
        f = open(path, "w")
        f.write(data)
        f.close()

    def create_aplan_files(self):
        create_EVT_File(self)
        create_ENV_File(self)
        create_Action_File(self)
        create_Beh_File(self)
        self.logger.info(
            "The translation was successfully completed! \n", "bold_yellow"
        )
        self.counters.deinit()
