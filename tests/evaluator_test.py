import unittest

from monkey.lexer.lexer import Lexer
from monkey.parser.parser import Parser
from monkey.evaluator.evaluator import Evaluator, NULL
from monkey.object.object import (
    Integer,
    Boolean,
    Null,
)


class TestEvaluador(unittest.TestCase):

    def test_return_statements(self):
        tests = [
            ["return 10;", 10],
            ["return 10; 9;", 10],
            ["return 2 * 5; 9;", 10],
            ["9; return 2 * 5; 9;", 10],
            ["if (10 > 1) { if (10 > 1) { return 10;} return 1}", 10],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            evaluated = self.assert_test_eval(source)
            self.assert_test_integer_object(evaluated, expected)

    def test_if_else_expressions(self):
        tests = [
            ["if (true) { 10 }", 10],
            ["if (false) { 10 }", None],
            ["if (1) { 10 }", 10],
            ["if (1 < 2) { 10 }", 10],
            ["if (1 > 2) { 10 }", None],
            ["if (1 > 2) { 10 } else { 20 }", 20],
            ["if (1 < 2) { 10 } else { 20 }", 10],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            evaluated = self.assert_test_eval(source)
            integer = expected
            if type(integer) is int:
                self.assert_test_integer_object(evaluated, int(integer))
            else:
                self.assert_test_null_object(evaluated)

    def test_bang_operator(self):
        tests = [
            ["!true", False],
            ["!false", True],
            ["!5", False],
            ["!!true", True],
            ["!!false", False],
            ["!!5", True],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            evaluated = self.assert_test_eval(source)
            self.assert_test_boolean_object(evaluated, expected)

    def test_boolean_expression(self):
        tests = [
            ["true", True],
            ["false", False],
        ]

        for tt in tests:
            source = tt[0]
            expected = tt[1]
            evaluated = self.assert_test_eval(source)
            self.assert_test_boolean_object(evaluated, expected)

    def assert_test_null_object(self, obj):
        if obj != NULL:
            print(f'object is not NULL. got={obj}')
            return False
        return True

    def assert_test_boolean_object(self, obj, expected):
        result = obj
        if type(result) is not Boolean:
            print(f'object is not Boolean. got={type(result)}')
        if result.value != expected:
            print(f'object has wrong value. got={result.value}, want={expected}')
            return False
        return True

    def test_eval_boolean_expression(self):
        tests = [
            ["true", True],
            ["false", False],
            ["true == true", True],
            ["false == false", True],
            ["true == false", False],
            ["true != false", True],
            ["false != true", True],
            ["(1 < 2) == true", True],
            ["(1 < 2) == false", False],
            ["(1 > 2) == true", False],
            ["(1 > 2) == false", True],
            ["1 < 2", True],
            ["1 > 2", False],
            ["1 < 1", False],
            ["1 > 1", False],
            ["1 == 1", True],
            ["1 != 1", False],
            ["1 == 2", False],
            ["1 != 2", True],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            evaluated = self.assert_test_eval(source)
            self.assert_test_boolean_object(evaluated, expected)

    def test_eval_integer_expression(self):
        tests = [
            ["5", 5],
            ["10", 10],
            ["-5", -5],
            ["-10", -10],
            ["5 + 5 + 5 + 5 - 10", 10],
            ["2 * 2 * 2 * 2 * 2", 32],
            ["-50 + 100 + -50", 0],
            ["5 + 2 * 10", 25],
            ["20 + 2 * -10", 0],
            ["50 / 2 * 2 + 10", 60],
            ["2 * (5 + 10)", 30],
            ["3 * 3 * 3 + 10", 37],
            ["(5 + 10 * 2 + 15 / 3) * 2 + -10", 50],
        ]

        for tt in tests:
            source = tt[0]
            expected = tt[1]

            evaluated = self.assert_test_eval(source)
            self.assert_test_integer_object(evaluated, expected)

    def assert_test_eval(self, source):
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        eva = Evaluator()

        return eva.eval(node=program)

    def assert_test_integer_object(self, obj, expected):
        result = obj  # Object
        if type(result) is not Integer:
            print(f'object is not Integer. got={type(obj)}')
            return False

        if result.value != expected:
            print(f'object has wrong value. got={result.value}, want={expected}')
            return False
        return True


if __name__ == '__main__':
    unittest.main()