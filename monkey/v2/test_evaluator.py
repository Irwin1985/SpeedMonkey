import unittest

from monkey.v2.main import *


class TestEvaluator(unittest.TestCase):

    def test_closures(self):
        source = """
        let newAdder = fn(x) {
            fn(y) { x + y};
        };

        let addTwo = newAdder(2);
        addTwo(2);
        """
        self.assert_test_integer_object(self.assert_test_eval(source), 4)

    def test_function_application(self):
        tests = [
            ["let identity = fn(x) { x; }; identity(5);", 5],
            ["let identity = fn(x) { return x; }; identity(5);", 5],
            ["let double = fn(x) { x * 2; }; double(5);", 10],
            ["let add = fn(x, y) { x + y; }; add(5, 5);", 10],
            ["let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20],
            ["fn(x) { x; }(5)", 5],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            self.assert_test_integer_object(self.assert_test_eval(source), expected)

    def test_function_object(self):
        source = "fn(x) { x + 2; };"

        fn = self.assert_test_eval(source)
        if type(fn) is not Function:
            self.fail(f'object is not Function. got={type(fn)}')

        if len(fn.parameters) != 1:
            self.fail(f'function has wrong parameters. Parameters={fn.parameters}')

        if fn.parameters[0].string() != "x":
            self.fail(f"parameters is not 'x'. got={fn.parameters[0]}")

        expected_body = "(x + 2)"
        if fn.body.string() != expected_body:
            self.fail(f"body is not {expected_body}. got={fn.body.string()}")

    def test_let_statements(self):
        tests = [
            ["let a = 5; a;", 5],
            ["let a = 5 * 5; a;", 25],
            ["let a = 5; let b = a; b;", 5],
            ["let a = 5; let b = a; let c = a + b + 5; c;", 15],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            self.assert_test_integer_object(self.assert_test_eval(source), expected)

    def test_error_handling(self):
        tests = [
            ["5 + true;", "type mismatch: Type.INTEGER_OBJ + Type.BOOLEAN_OBJ"],
            ["5 + true; 5;", "type mismatch: Type.INTEGER_OBJ + Type.BOOLEAN_OBJ"],
            ["-true", "unknown operator: -Type.BOOLEAN_OBJ"],
            ["true + false;", "unknown operator: Type.BOOLEAN_OBJ + Type.BOOLEAN_OBJ"],
            ["5; true + false; 5", "unknown operator: Type.BOOLEAN_OBJ + Type.BOOLEAN_OBJ"],
            ["if (10 > 1) { true + false; }", "unknown operator: Type.BOOLEAN_OBJ + Type.BOOLEAN_OBJ"],
            ["if (10 > 1) { if (10 > 1) { return true + false;} return 1;}",
             "unknown operator: Type.BOOLEAN_OBJ + Type.BOOLEAN_OBJ"],
            ["foobar", "identifier not found: foobar"],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            evaluated = self.assert_test_eval(source)
            err_obj = evaluated
            if type(err_obj) is not Error:
                print(f'no error object returned. got={type(err_obj)}')
                continue
            if err_obj.message != expected:
                print(f"wrong error message. expected='{expected}'. got='{err_obj.message}'")

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
        program = parser.parse()
        visitor = NodeVisitor()
        env = Environment()

        return visitor.visit(node=program, env=env)

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