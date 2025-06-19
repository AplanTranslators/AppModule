from typing import TYPE_CHECKING

from ..classes.declarations import DeclTypes

from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def create_ENV_File(self: "Program"):
    env = "environment (\n"  # Open env

    # ----------------------------------
    # Types
    # ----------------------------------
    env += "\ttypes : obj (\n"
    sub_env = ""
    decls = self.typedefs.getElementsIE()

    for design_unit in self.design_units.getElements():
        decls += design_unit.typedefs.getElementsIE()

    sub_env += str(decls)
    if len(sub_env) > 0:
        env += sub_env + "\n"
    else:
        env += "\t\t\tNil\n"
    env += "\t);\n"

    # ----------------------------------
    # Attributes
    # ----------------------------------

    env += "\tattributes : obj (Nil);\n"

    # ----------------------------------
    # Agents types
    # ----------------------------------

    env += "\tagent_types : obj (\n"

    for design_unit in self.design_units.getElementsIE(
        exclude=ElementsTypes.OBJECT_ELEMENT
    ).getElements():
        env += "\t\t{0} : obj (\n".format(design_unit.identifier)
        sub_env = ""
        decls = design_unit.declarations.getElementsIE(data_type_exclude=DeclTypes.ENUM_TYPE)
        for index, elem in enumerate(decls.getElements()):
            if index > 0:
                sub_env += ",\n"
            sub_env += "\t\t\t{0}:{1}".format(elem.getName(), elem.getAplanDecltype())
            if index + 1 == len(decls):
                sub_env += "\n"
        if len(sub_env) > 0:
            env += sub_env
        else:
            env += "\t\t\tNil\n"
        env += "\t\t),\n"
    env += "\t\tENVIRONMENT:obj(Nil)\n"
    env += "\t);\n"

    # ----------------------------------
    # Agents
    # ----------------------------------
    env += "\tagents : obj (\n"
    for design_unit in self.design_units.getElementsIE(
        exclude=ElementsTypes.CLASS_ELEMENT
    ).getElements():
        env += "\t\t{0} : obj ({1}),\n".format(
            design_unit.identifier, design_unit.ident_uniq_name
        )
    env += "\t\tENVIRONMENT : obj (env)\n"
    env += "\t);\n"

    # ----------------------------------
    # Axioms
    # ----------------------------------
    env += "\taxioms : obj (Nil);\n"

    # ----------------------------------
    # Logic formula
    # ----------------------------------
    env += "\tlogic_formula : obj (1)\n"
    env += ");"  # Close env

    self.write_to_file(self.path_to_result + "project.env_descript", env)
    self.logger.info(".env_descript file created \n", "purple")
