from typing import TYPE_CHECKING
from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def create_Beh_File(self: "Program"):
    # ----------------------------------
    # Behaviour
    # ----------------------------------
    behaviour = []
    for index, design_unit in enumerate(
        self.design_units.getElementsIE(
            exclude=ElementsTypes.OBJECT_ELEMENT
        ).getElements()
    ):

        raw_protocol_strings = [
            design_unit.getBehInitProtocols(),
            design_unit.structures.getStructuresInStrFormat(),
            design_unit.out_of_block_elements.getProtocolsInStrFormat(),
        ]
        tmp = [s for s in raw_protocol_strings if s and s.strip()]
        tmp = "\n".join(tmp)

        tmp = self.str_formater.removeTrailingComma(tmp)

        behaviour.append(tmp)

    behaviour = ",\n".join(behaviour)

    self.write_to_file(self.path_to_result + "project.behp", behaviour)
    self.logger.info(".beh file created", "purple")
