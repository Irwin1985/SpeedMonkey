from enum import Enum


class Type(Enum):
    INTEGER_OBJ = "INTEGER",
    BOOLEAN_OBJ = "BOOLEAN",
    NULL_OBJ = "NULL",
    RETURN_VALUE_OBJ = "RETURN_VALUE"
    ERROR_OBJ = "ERROR"
    FUNCTION_OBJ = "FUNCTION"


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


class ReturnValue(Object):
    def __init__(self, value):
        self.value = value

    def inspect(self):
        return self.value.inspect()

    def type(self):
        return Type.RETURN_VALUE_OBJ


class Error(Object):
    def __init__(self, message):
        self.message = message

    def inspect(self):
        return "ERROR: " + self.message

    def type(self):
        return Type.ERROR_OBJ


class Function(Object):
    def __init__(self, parameters, body, env):
        self.parameters = parameters
        self.body = body
        self.env = env

    def inspect(self):
        out = ""
        params = []
        for p in self.parameters:
            params.append(p.string())

        out += "fn"
        out += "("
        out += ", ".join(params)
        out += '\n'
        out += self.body.string()
        out += '\n'

        return out