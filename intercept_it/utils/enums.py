from enum import Enum


class WarningLevelsEnum(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class ExecutionModesEnum(Enum):
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"


class HandlersExecutionModesEnum(Enum):
    ORDERED = "ordered"
    FAST = "fast"
