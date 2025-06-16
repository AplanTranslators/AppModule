from typing import TYPE_CHECKING
from app.classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def create_Beh_File(self: "Program"):
    # ----------------------------------
    # Behaviour
    # ----------------------------------
    behaviour = ""
    for index, module in enumerate(
        self.modules.getElementsIE(exclude=ElementsTypes.OBJECT_ELEMENT).getElements()
    ):
        if index != 0:
            behaviour += ",\n"
        behaviour += f"{module.getBehInitProtocols()}"
        behaviour += module.structures.getStructuresInStrFormat()

        if module.isIncludeOutOfBlockElements():
            behaviour += module.out_of_block_elements.getProtocolsInStrFormat()
        else:
            behaviour = self.str_formater.removeTrailingComma(behaviour)
            # behaviour += "\n"
    self.write_to_file(self.path_to_result + "project.behp", behaviour)
    self.logger.info(".beh file created \n", "purple")
