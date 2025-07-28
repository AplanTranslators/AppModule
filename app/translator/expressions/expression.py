from typing import Tuple

from ...utils.counters import CounterTypes
from ...classes.node import Node
from ...classes.element_types import ElementsTypes
from ...classes.protocols import Protocol
from ...classes.actions import Action


def findAssociatedAction(
    protocol: Protocol | None,
    element_type: ElementsTypes,
    name_part: str,
    action: Action,
    action_name: str,
):
    previus_action = False
    last_element = None
    if protocol and len(protocol.body) > 0:
        last_element = protocol.body.getElementByIndex(len(protocol.body) - 1)
        if (
            last_element.element_type == ElementsTypes.ACTION_ELEMENT
            and last_element.pointer_to_related
            and last_element.pointer_to_related.element_type == element_type
            and last_element.pointer_to_related.description_action_name == name_part
        ):
            if not last_element.pointer_to_related.postcondition.have_common_identifier_elements(
                action.postcondition
            ):
                previus_action = True
                action_name = action.identifier
            else:
                last_element = None
        else:
            last_element = None

    return (last_element, previus_action, action_name)


def copyToAssociatedAction(last_element: Action, action: Action) -> Action:
    if last_element:
        previous_action: Action = last_element.pointer_to_related
        previous_action.description_end += action.description_end
        previous_action.description_start += action.description_start

        if previous_action.precondition.elements[0].identifier != "1":
            previous_action.precondition.addElement(
                Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
            )
            previous_action.precondition += action.precondition

        if previous_action.postcondition.elements[0].identifier != "1":
            previous_action.postcondition.addElement(
                Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
            )
            previous_action.postcondition += action.postcondition

        action = previous_action

    return action


def getNamePartAndCounter(element_type: ElementsTypes) -> Tuple[str, CounterTypes]:
    name_part = ""
    counter_type = CounterTypes.NONE_COUNTER

    if element_type == ElementsTypes.ASSERT_ELEMENT:
        name_part = "assert"
        counter_type = CounterTypes.ASSERT_COUNTER
    elif element_type == ElementsTypes.CONDITION_ELEMENT:
        name_part = "cond"
        counter_type = CounterTypes.CONDITION_COUNTER
    elif (
        element_type == ElementsTypes.ASSIGN_ELEMENT
        or element_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT
        or element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
    ):
        name_part = "assign"
        counter_type = CounterTypes.ASSIGNMENT_COUNTER
    elif element_type == ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT:
        name_part = "assign_array"
        counter_type = CounterTypes.ASSIGNMENT_COUNTER
    elif element_type == ElementsTypes.REPEAT_ELEMENT:
        name_part = "repeat_iteration"
        counter_type = CounterTypes.REPEAT_COUNTER

    return (name_part, counter_type)
