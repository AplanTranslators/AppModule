from typing import TYPE_CHECKING
from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def create_Action_File(self: "Program"):
    # ----------------------------------
    # Actions
    # ----------------------------------
    actions = ""
    for index, design_unit in enumerate(
        self.design_units.getElementsIE(exclude=ElementsTypes.OBJECT_ELEMENT).getElements()
    ):
        result = design_unit.actions.getActionsInStrFormat()
        if index != 0:
            if len(result) > 0:
                actions += ",\n"
        actions += result

    self.write_to_file(self.path_to_result + "project.act", actions)
    self.logger.info(".act file created \n", "purple")
