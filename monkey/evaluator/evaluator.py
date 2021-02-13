from monkey.ast.ast import (
    Program,
    ExpressionStatement,
    IntegerLiteral,
    Boolean as BooleanAST,
    NullLiteral,
    PrefixExpression,
    InfixExpression,
)
from monkey.object.object import (
    Integer,
    Boolean,
    Null,
    Type,
)

TRUE = Boolean(value=True)
FALSE = Boolean(value=False)
NULL = Null()


class Evaluator:

    def eval(self, node):
        # Statements
        if type(node) is Program:
            return self.eval_statements(node.statements)

        elif type(node) is ExpressionStatement:
            return self.eval(node.expression)

        # Expressions
        elif type(node) is IntegerLiteral:
            return Integer(value=node.value)

        elif type(node) is BooleanAST:
            return TRUE if node.value else FALSE

        elif type(node) is NullLiteral:
            return NULL

        elif type(node) is PrefixExpression:
            right = self.eval(node.right)
            return self.eval_prefix_expression(node.operator, right)

        elif type(node) is InfixExpression:
            left = self.eval(node.left)
            right = self.eval(node.right)
            return self.eval_infix_expression(node.operator, left, right)

        return None

    def eval_statements(self, stmts):
        result = None

        for statement in stmts:
            result = self.eval(statement)

        return result

    def eval_prefix_expression(self, operator, right):
        if operator == "!":
            return self.eval_bang_operator_expression(right)
        elif operator == "-":
            return self.eval_minus_prefix_operator_expression(right)
        else:
            return NULL

    def eval_infix_expression(self, operator, left, right):
        if left.type() == Type.INTEGER_OBJ and right.type() == Type.INTEGER_OBJ:
            return self.eval_integer_infix_expression(operator, left, right)
        elif operator == "==":
            return self.native_bool_to_boolean_object(left == right)
        elif operator == "!=":
            return self.native_bool_to_boolean_object(left != right)
        else:
            return NULL

    def eval_integer_infix_expression(self, operator, left, right):
        left_val = left.value
        right_val = right.value

        if operator == '+':
            return Integer(value=int(left_val+right_val))
        elif operator == '-':
            return Integer(value=int(left_val-right_val))
        elif operator == '*':
            return Integer(value=int(left_val*right_val))
        elif operator == '/':
            return Integer(value=int(left_val/right_val))
        elif operator == '<':
            return self.native_bool_to_boolean_object(left_val < right_val)
        elif operator == '>':
            return self.native_bool_to_boolean_object(left_val > right_val)
        elif operator == '==':
            return self.native_bool_to_boolean_object(left_val == right_val)
        elif operator == '!=':
            return self.native_bool_to_boolean_object(left_val != right_val)
        else:
            return NULL

    def native_bool_to_boolean_object(self, value):
        return TRUE if value else FALSE

    def eval_bang_operator_expression(self, right):
        if right == TRUE:
            return FALSE
        elif right == FALSE:
            return TRUE
        elif right == NULL:
            return TRUE
        else:
            return FALSE

    def eval_minus_prefix_operator_expression(self, right):
        if right.type() != Type.INTEGER_OBJ:
            return NULL
        value = right.value
        return Integer(value=-value)

