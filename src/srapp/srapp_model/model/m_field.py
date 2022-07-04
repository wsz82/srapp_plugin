from enum import Enum


class FieldConstraint(Enum):
    NOT_NULL = 0
    UNIQUE = 1
    SOIL = 2
    WATER_HORIZON = 3
    EXUDATION = 4
    STATUS = 5
    SHEARS_NUMBER = 6
