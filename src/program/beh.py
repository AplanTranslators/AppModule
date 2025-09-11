from typing import TYPE_CHECKING
from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def create_Beh_File(self: "Program"):
    # ----------------------------------
    # Behaviour
    # ----------------------------------
    behaviour = []
    for design_unit in self.design_units.getElementsIE(
        exclude=ElementsTypes.OBJECT_ELEMENT
    ).getElements():

        # Створення та фільтрація рядків в одному рядку коду
        protocol_strings = [
            s
            for s in [
                design_unit.getBehInitProtocols(),
                design_unit.structures.getStructuresInStrFormat(),
                design_unit.out_of_block_elements.getProtocolsInStrFormat(),
            ]
            if s and s.strip()
        ]

        tmp = "\n".join(protocol_strings)
        tmp = self.str_formater.removeTrailingComma(tmp)
        behaviour.append(tmp)

    behaviour = ",\n".join(behaviour)
    self.aplan_logger.behpPush(behaviour)
    self.logger.info(".beh file created", "purple")
