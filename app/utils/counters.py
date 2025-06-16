from app.utils.singleton import SingletonMeta
from enum import Enum, auto


class CounterTypes(Enum):
    ASSIGNMENT_COUNTER = auto()
    IF_COUNTER = auto()
    CASE_COUNTER = auto()
    B_COUNTER = auto()
    ASSERT_COUNTER = auto()
    MODULE_COUNTER = auto()
    BODY_COUNTER = auto()
    ELSE_BODY_COUNTER = auto()
    LOOP_COUNTER = auto()
    CONDITION_COUNTER = auto()
    NONE_COUNTER = auto()
    STRUCT_COUNTER = auto()
    REPEAT_COUNTER = auto()
    FOREVER_COUNTER = auto()
    TASK_COUNTER = auto()
    ENUM_COUNTER = auto()
    OBJECT_COUNTER = auto()
    SEQUENCE_COUNTER = auto()


class Counters(metaclass=SingletonMeta):
    types = CounterTypes
    counters = {}

    def __init__(self) -> None:
        self.reinit()

    def reinit(self):
        self.counters[self.types.ASSIGNMENT_COUNTER] = 1
        self.counters[self.types.ASSERT_COUNTER] = 1
        self.counters[self.types.MODULE_COUNTER] = 1
        self.counters[self.types.BODY_COUNTER] = 1
        self.counters[self.types.IF_COUNTER] = 0
        self.counters[self.types.ELSE_BODY_COUNTER] = 1
        self.counters[self.types.CASE_COUNTER] = 0
        self.counters[self.types.B_COUNTER] = 0
        self.counters[self.types.LOOP_COUNTER] = 1
        self.counters[self.types.CONDITION_COUNTER] = 1
        self.counters[self.types.STRUCT_COUNTER] = 0
        self.counters[self.types.REPEAT_COUNTER] = 1
        self.counters[self.types.FOREVER_COUNTER] = 1
        self.counters[self.types.TASK_COUNTER] = 1
        self.counters[self.types.ENUM_COUNTER] = 1
        self.counters[self.types.OBJECT_COUNTER] = 1
        self.counters[self.types.SEQUENCE_COUNTER] = 0

    def unhandled_cb(self, counter_type: CounterTypes):
        raise ValueError(f"Unhandled counter type: {counter_type.name}")

    def incriese(self, counter_type: CounterTypes):
        if counter_type in self.counters:
            self.counters[counter_type] += 1
        else:
            self.unhandled_cb(counter_type)

    def decriese(self, counter_type: CounterTypes):
        if counter_type in self.counters:
            if self.counters[counter_type] > 0:
                self.counters[counter_type] -= 1
        else:
            self.unhandled_cb(counter_type)

    def get(self, counter_type: CounterTypes):
        value = self.counters.get(counter_type, None)
        if not value:
            self.unhandled_cb(counter_type)
        return value

    def deinit(self):
        self.reinit()
