from typing import TYPE_CHECKING

from Core.src.logger.logger import LOG_NL

if TYPE_CHECKING:
    from program import Program


def generateEvt(self: "Program"):
    self.aplan_logger.evt("events(")

    for design_unit in self.design_units.getElements():
        for elem in design_unit.declarations.getInputPorts():
            self.aplan_logger.evt(
                "\ts_{0}:obj(x1:{1});".format(elem.getName(), elem.getAplanDecltype())
            )
    self.aplan_logger.evt(");")
    self.logger.info(".evt_descript file created ", "purple")
