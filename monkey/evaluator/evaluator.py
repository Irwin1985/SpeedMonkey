from monkey.ast.ast import (
    Program,
    ExpressionStatement,
    IntegerLiteral,
    Boolean as BooleanAST,
    NullLiteral,
    PrefixExpression,
    InfixExpression,
    IfExpression,
    BlockStatement,
    ReturnStatement,
    LetStatement,
    Identifier,
    FunctionLiteral,
    CallExpression,
)
from monkey.object.object import (
    Integer,
    Boolean,
    Null,
    Type,
    ReturnValue,
    Error,
    Function,
)

from monkey.object.environment import new_enclosed_environment

TRUE = Boolean(value=True)
FALSE = Boolean(value=False)
NULL = Null()


class Evaluator:

    def eval(self, node, env):
        # Statements
        if type(node) is Program:
            return self.eval_program(node, env)
        # Let Statement
        elif type(node) is LetStatement:
            val = self.eval(node.value, env)
            if self.is_error(val):
                return val
            env.set(node.name.value, val)
        # Identifier
        elif type(node) is Identifier:
            return self.eval_identifier(node, env)

        elif type(node) is ExpressionStatement:
            return self.eval(node.expression, env)
        # Function Literal
        elif type(node) is FunctionLiteral:
            params = node.parameters
            body = node.body
            return Function(parameters=params, body=body, env=env)
        # Function Call
        elif type(node) is CallExpression:
            function = self.eval(node.function, env)
            if self.is_error(function):
                return function
            args = self.eval_expressions(node.arguments, env)

            if len(args) == 1 and self.is_error(args[0]):
                return args[0]

            return self.apply_function(function, args)

        # Expressions
        elif type(node) is IntegerLiteral:
            return Integer(value=node.value)

        elif type(node) is BooleanAST:
            return TRUE if node.value else FALSE

        elif type(node) is NullLiteral:
            return NULL

        # Prefix and Infix Expressions
        elif type(node) is PrefixExpression:
            right = self.eval(node.right, env)

            if self.is_error(right):
                return right

            return self.eval_prefix_expression(node.operator, right)

        elif type(node) is InfixExpression:
            left = self.eval(node.left, env)

            if self.is_error(left):
                return left

            right = self.eval(node.right, env)

            if self.is_error(right):
                return right

            return self.eval_infix_expression(node.operator, left, right)

        # Conditional
        elif type(node) is BlockStatement:
            return self.eval_block_statement(node, env)

        elif type(node) is IfExpression:
            return self.eval_if_expression(node, env)

        # Return statement
        elif type(node) is ReturnStatement:
            val = self.eval(node.return_value, env)

            if self.is_error(val):
                return val

            return ReturnValue(value=val)

        return None

    def eval_expressions(self, exps, env):
        result = []
        for e in exps:
            evaluated = self.eval(e, env)
            if self.is_error(evaluated):
                return [evaluated]
            result.append(evaluated)
        return result

    def eval_program(self, program, env):
        result = None

        for statement in program.statements:
            result = self.eval(statement, env)

            if result is not None and result.type() == Type.RETURN_VALUE_OBJ:
                return result.value  # Finally program returns the wrapped value of ReturnValue()
            elif result is not None and result.type() == Type.ERROR_OBJ:
                return result  # Error does not evaluates nothing. Just print the message.

        return result

    def eval_block_statement(self, block, env):
        result = None

        for statement in block.statements:
            result = self.eval(statement, env)

            if result is not None:
                rt = result.type()
                if rt in (Type.RETURN_VALUE_OBJ, Type.ERROR_OBJ):
                    return result

        return result

    def eval_identifier(self, node, env):
        val = env.get(node.value)
        if val is None:
            return self.new_error("identifier not found: " + node.value)
        return val

    def eval_prefix_expression(self, operator, right):
        if operator == "!":
            return self.eval_bang_operator_expression(right)
        elif operator == "-":
            return self.eval_minus_prefix_operator_expression(right)
        else:
            return self.new_error(f'unknown operator: {operator} {right.type()}')

    def eval_infix_expression(self, operator, left, right):
        if left.type() == Type.INTEGER_OBJ and right.type() == Type.INTEGER_OBJ:
            return self.eval_integer_infix_expression(operator, left, right)
        elif operator == "==":
            return self.native_bool_to_boolean_object(left == right)
        elif operator == "!=":
            return self.native_bool_to_boolean_object(left != right)
        elif left.type() != right.type():
            return self.new_error(f'type mismatch: {left.type()} {operator} {right.type()}')
        else:
            return self.new_error(f'unknown operator: {left.type()} {operator} {right.type()}')

    def eval_if_expression(self, ie, env):
        condition = self.eval(ie.condition, env)

        if self.is_error(condition):
            return condition

        if self.is_truthy(condition):
            return self.eval(ie.consequence, env)
        elif ie.alternative is not None:
            return self.eval(ie.alternative, env)
        else:
            return NULL

    def is_truthy(self, obj):
        if obj == NULL:
            return False
        elif obj == TRUE:
            return True
        elif obj == FALSE:
            return False
        else:
            return True

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
            return self.new_error(f'type mismatch: {left.type()} {operator} {right.type()}')

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
            return self.new_error(f'unknown operator: -{right.type()}')
        value = right.value
        return Integer(value=-value)

    def new_error(self, message):
        return Error(message=message)

    def is_error(self, obj):
        if obj is not None:
            return obj.type() == Type.ERROR_OBJ
        return False

    def apply_function(self, function, args):
        if type(function) is not Function:
            return self.new_error(f"not a function: {type(function.type())}")

        extended_env = self.extend_function_env(function, args)
        evaluated = self.eval(function.body, extended_env)
        return self.unwrap_return_value(evaluated)

    def extend_function_env(self, fn, args):
        env = new_enclosed_environment(fn.env)

        for param_idx, param in enumerate(fn.parameters):
            env.set(param.value, args[param_idx])

        return env

    def unwrap_return_value(self, obj):
        if type(obj) is ReturnValue:
            return obj.value

        return obj


