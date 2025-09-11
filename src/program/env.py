from typing import TYPE_CHECKING

from Core.src.logger.logger import LOG_NL

from ..classes.declarations import DeclTypes

from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def generateEnv(self: "Program"):
    self.aplan_logger.env("environment (")

    # ----------------------------------
    # Types
    # ----------------------------------
    self.aplan_logger.env("\ttypes : obj (")
    sub_env = ""
    decls = self.typedefs.getElementsIE()

    for design_unit in self.design_units.getElements():
        decls += design_unit.typedefs.getElementsIE()

    sub_env += str(decls)

    if len(sub_env) > 0:
        self.aplan_logger.env(sub_env)
    else:
        self.aplan_logger.env("\t\t\tNil")

    self.aplan_logger.env("\t);")

    # ----------------------------------
    # Attributes
    # ----------------------------------
    self.aplan_logger.env("\tattributes : obj (Nil);")

    # ----------------------------------
    # Agents types
    # ----------------------------------

    self.aplan_logger.env("\tagent_types : obj (")

    # Генеруємо рядки для кожного design_unit
    design_unit_strings = []
    for design_unit in self.design_units.getElementsIE(
        exclude=ElementsTypes.OBJECT_ELEMENT
    ).getElements():
        decls = design_unit.declarations.getElementsIE(
            data_type_exclude=DeclTypes.ENUM_TYPE
        )

        element_strings = [
            "\t\t\t{0}:{1}".format(elem.getName(), elem.getAplanDecltype())
            for elem in decls.getElements()
        ]

        # Використовуємо тернарний оператор для вибору між елементами та "Nil"
        decls_content = ",\n".join(element_strings) if element_strings else "\t\t\tNil"

        design_unit_content = ("\t\t{0} : obj (\n" "{1}\n" "\t\t),").format(
            design_unit.ident_uniq_name_upper, decls_content
        )

        design_unit_strings.append(design_unit_content)

    # Логуємо об'єднані рядки
    self.aplan_logger.env("\n".join(design_unit_strings))

    self.aplan_logger.env("\t\tENVIRONMENT:obj(Nil)")
    self.aplan_logger.env("\t);")

    # ----------------------------------
    # Agents
    # ----------------------------------
    self.aplan_logger.env("\tagents : obj (")
    for design_unit in self.design_units.getElementsIE(
        exclude=ElementsTypes.CLASS_ELEMENT
    ).getElements():
        self.aplan_logger.env(
            "\t\t{0} : obj ({1}),".format(
                design_unit.ident_uniq_name_upper,
                design_unit.ident_uniq_name,
            )
        )

    self.aplan_logger.env("\t\tENVIRONMENT : obj (env)")
    self.aplan_logger.env("\t);")

    # ----------------------------------
    # Axioms
    # ----------------------------------
    self.aplan_logger.env("\taxioms : obj (Nil);")

    # ----------------------------------
    # Logic formula
    # ----------------------------------
    self.aplan_logger.env("\tlogic_formula : obj (1)")
    self.aplan_logger.env(");")

    # self.write_to_file(self.result_path + "project.env_descript", env)
    self.logger.info(".env_descript file created ", "purple")
