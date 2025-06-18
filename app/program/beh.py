from typing import TYPE_CHECKING
from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def create_Beh_File(self: "Program"):
    # ----------------------------------
    # Behaviour
    # ----------------------------------
    behaviour = []
    for index, module in enumerate(
        self.modules.getElementsIE(exclude=ElementsTypes.OBJECT_ELEMENT).getElements()
    ):
        tmp = [
            module.getBehInitProtocols(),
            module.structures.getStructuresInStrFormat(),
            module.out_of_block_elements.getProtocolsInStrFormat(),
        ]

        tmp = "\n".join(tmp)

        tmp = self.str_formater.removeTrailingComma(tmp)

        behaviour.append(tmp)

    behaviour = ",\n".join(behaviour)

    self.write_to_file(self.path_to_result + "project.behp", behaviour)
    self.logger.info(".beh file created", "purple")
