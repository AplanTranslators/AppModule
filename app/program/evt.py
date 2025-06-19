from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from program import Program


def create_EVT_File(self: "Program"):
    evt = "events(\n"
    for design_unit in self.design_units.getElements():
        for elem in design_unit.declarations.getInputPorts():
            evt += "\ts_{0}:obj(x1:{1});\n".format(
                elem.getName(), elem.getAplanDecltype()
            )
    evt += ");"
    self.write_to_file(self.path_to_result + "project.evt_descript", evt)
    self.logger.info(".evt_descript file created \n", "purple")
