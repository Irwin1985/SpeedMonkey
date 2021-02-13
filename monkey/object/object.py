from enum import Enum


class Type(Enum):
    INTEGER_OBJ = "INTEGER",
    BOOLEAN_OBJ = "BOOLEAN",
    NULL_OBJ = "NULL",


class ObjectType:
    pass


class Object:
    def type(self):
        pass

    def inspect(self):
        pass


class Integer(Object):
    def __init__(self, value=None):
        self.value = value

    def inspect(self):
        return str(self.value)

    def type(self):
        return Type.INTEGER_OBJ


class Boolean(Object):
    def __init__(self, value=None):
        self.value = value

    def inspect(self):
        return str(self.value)

    def type(self):
        return Type.BOOLEAN_OBJ


class Null(Object):
    def __init__(self):
        self.value = None

    def inspect(self):
        return "null"

    def type(self):
        return Type.NULL_OBJ




