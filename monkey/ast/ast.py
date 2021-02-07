class Node:
    def token_literal(self):
        pass

    def string(self):
        pass


class Statement(Node):
    def statement_node(self):
        pass


class Expression(Node):
    def expression_node(self):
        pass


class Program(Statement):
    def __init__(self):
        self.statements = []

    def token_literal(self):
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""

    def string(self):
        out = ""

        for s in self.statements:
            out += s.string()

        return out


class LetStatement(Statement):
    def __init__(self, token, name=None, value=None):
        self.token = token
        self.name = name
        self.value = value

    def token_literal(self):
        return self.token.literal

    def statement_node(self):
        pass

    def string(self):
        out = self.token_literal() + " "
        out += self.name.string()
        out += " = "

        if self.value is not None:
            out += self.value.string()

        out += ";"
        return out


class Identifier(Expression):
    def __init__(self, token, value):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.value


class ReturnStatement(Statement):
    def __init__(self, token, return_value=None):
        self.token = token
        self.return_value = return_value

    def statement_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = self.token_literal() + " "

        if self.return_value is not None:
            out += self.return_value.string()

        out += ";"

        return out


class ExpressionStatement(Statement):
    def __init__(self, token, expression=None):
        self.token = token
        self.expression = expression

    def statement_node(self):
        pass

    def token_literal(self):
        return self.token.literal()

    def string(self):
        if self.expression is not None:
            return self.expression.string()

        return ""


class IntegerLiteral(Expression):
    def __init__(self, token, value=None):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class PrefixExpression(Expression):
    def __init__(self, token, operator=None, right=None):
        self.token = token
        self.operator = operator
        self.right = right

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = "("
        out += self.operator
        out += self.right.string()
        out += ")"

        return out


class InfixExpression(Expression):
    def __init__(self, token, left=None, operator=None, right=None):
        self.token = token
        self.left = left
        self.operator = operator
        self.right = right

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = "("
        out += self.left.string()
        out += " " + self.operator + " "
        out += self.right.string()
        out += ")"

        return out
