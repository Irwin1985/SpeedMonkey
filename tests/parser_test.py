import unittest

from monkey.lexer.lexer import Lexer
from monkey.parser.cfg_parser import Parser


class TestParser(unittest.TestCase):

    def test_call_expression_parsing(self):
        source = "add(1, 2 * 3, 4 + 5);"
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assert_check_parser_errors(parser)

        self.assertEqual(1, len(program.statements),
                         f'program.statements does not contain 1 statements. got={len(program.statements)}')

        stmt = program.statements[0]  # ExpressionStatement AST node.
        exp = stmt.expression  # CallExpression AST node.

        if not self.assert_test_identifier(exp.function, "add"):
            return

        self.assertEqual(3, len(exp.arguments), f'wrong length of arguments. got={len(exp.arguments)}')

        self.assert_test_literal_expression(exp.arguments[0], 1)
        self.assert_test_infix_expression(exp.arguments[1], 2, "*", 3)
        self.assert_test_infix_expression(exp.arguments[2], 4, "+", 5)

    def test_function_parameter_parsing(self):
        tests = [
            ["fn() {};", []],
            ["fn(x) {};", ["x"]],
            ["fn(x, y, z) {};", ["x", "y", "z"]],
        ]

        for tt in tests:
            source = tt[0]
            expected_params = tt[1]

            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            self.assert_check_parser_errors(parser)

            stmt = program.statements[0]  # ExpressionStatement AST node.
            function = stmt.expression  # FunctionLiteral AST node.

            if len(function.parameters) != len(expected_params):
                print(f'length parameters wrong. want {len(expected_params)}, got={len(function.parameters)}')

            for i, ident in enumerate(expected_params):
                self.assert_test_literal_expression(function.parameters[i], ident)

    def test_function_literal_parsing(self):
        source = "fn(x, y) { x + y; }"

        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assert_check_parser_errors(parser)

        self.assertEqual(1, len(program.statements),
                         f'program.statements does not contain 1 statements. got={len(program.statements)}')

        expression_statement = program.statements[0]  # ExpressionStatement AST node.
        function = expression_statement.expression  # FunctionLiteral AST node.

        self.assertEqual(2, len(function.parameters),
                         f'function literal parameters wrong. want 2, got={len(function.parameters)}')

        self.assert_test_literal_expression(function.parameters[0], "x")
        self.assert_test_literal_expression(function.parameters[1], "y")

        self.assertEqual(1, len(function.body.statements),
                         f'function.body.statements has not 1 statements. got={len(function.body.statements)}')

        body_stmt = function.body.statements[0]  # ExpressionStatement AST node.

        self.assert_test_infix_expression(body_stmt.expression, "x", "+", "y")

    def test_if_else_expression(self):
        source = "if (x < y) { x } else { y }"
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        self.assert_check_parser_errors(parser)
        self.assertEqual(1, len(program.statements))

        stmt = program.statements[0]  # ExpressionStatement AST

        exp = stmt.expression  # IfExpression AST node

        if not self.assert_test_infix_expression(exp.condition, "x", "<", "y"):
            return

        if len(exp.consequence.statements) != 1:
            print(f'consequence is not 1 statements. got={len(exp.consequence.statements)}')

        consequence = exp.consequence.statements[0]  # ExpressionStatement AST

        if not self.assert_test_identifier(consequence.expression, "x"):
            return

        if len(exp.alternative.statements) != 1:
            print(f'alternative is not 1 statements. got={len(exp.alternative.statements)}')

        alternative = exp.alternative.statements[0]  # ExpressionStatement AST

        if not self.assert_test_identifier(alternative.expression, "y"):
            return

    def test_if_expression(self):
        source = "if (x < y) { x }"
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assert_check_parser_errors(parser)

        self.assertEqual(1, len(program.statements),
                         f'program.body does not contain 1 statements. got={len(program.statements)}')

        stmt = program.statements[0]  # ExpressionStatement AST

        exp = stmt.expression  # IfExpression AST node

        if not self.assert_test_infix_expression(exp.condition, "x", "<", "y"):
            return

        if len(exp.consequence.statements) != 1:
            print(f'consequence is not 1 statements. got={len(exp.consequence.statements)}')

        consequence = exp.consequence.statements[0]  # ExpressionStatement AST

        if not self.assert_test_identifier(consequence.expression, "x"):
            return

        if exp.alternative is not None:
            print(f'exp.alternative.statements was not nil. got={exp.alternative}')

    def test_boolean_expression(self):
        tests = [
            ["true;", True],
            ["false;", False],
        ]
        for tt in tests:
            source = tt[0]
            expected = tt[1]
            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            self.assert_check_parser_errors(parser)

            self.assertEqual(1, len(program.statements))

            expression_statement = program.statements[0]
            boolean_exp = expression_statement.expression

            self.assertEqual(boolean_exp.value, expected)

    def test_operator_precedence_parsing(self):
        tests = [
            ["-a * b", "((-a) * b)"],
            ["!-a", "(!(-a))"],
            ["a + b + c", "((a + b) + c)"],
            ["a + b - c", "((a + b) - c)"],
            ["a * b * c", "((a * b) * c)"],
            ["a * b / c", "((a * b) / c)"],
            ["a + b / c", "(a + (b / c))"],
            ["a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"],
            ["3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"],
            ["5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"],
            ["5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"],
            ["3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"],
            ["true", "true"],
            ["false", "false"],
            ["3 > 5 == false", "((3 > 5) == false)"],
            ["3 < 5 == true", "((3 < 5) == true)"],
            ["1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"],
            ["(5 + 5) * 2", "((5 + 5) * 2)"],
            ["2 / (5 + 5)", "(2 / (5 + 5))"],
            ["-(5 + 5)", "(-(5 + 5))"],
            ["!(true == true)", "(!(true == true))"],
            ["a + add(b * c) + d", "((a + add((b * c))) + d)"],
            ["add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))", "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))"],
            ["add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"],
        ]

        for tt in tests:
            source = tt[0]
            expected = tt[1]
            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            self.assert_check_parser_errors(parser)

            actual = program.string()

            self.assertEqual(actual, expected, f"expected={expected}, got={actual}")

    def test_parsing_infix_expressions(self):
        infix_tests = [
            ["5 + 5;", 5, "+", 5],
            ["5 - 5;", 5, "-", 5],
            ["5 * 5;", 5, "*", 5],
            ["5 / 5;", 5, "/", 5],
            ["5 < 5;", 5, "<", 5],
            ["5 > 5;", 5, ">", 5],
            ["5 == 5;", 5, "==", 5],
            ["5 != 5;", 5, "!=", 5],
            ["true == true", True, "==", True],
            ["true != false", True, "!=", False],
            ["false == false", False, "==", False],
        ]

        for tt in infix_tests:
            source = tt[0]
            left_value = tt[1]
            operator = tt[2]
            right_value = tt[3]

            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            self.assert_check_parser_errors(parser)

            self.assertEqual(1, len(program.statements),
                             f"program.statements does not contain 1 statements. got={len(program.statements)}")

            stmt = program.statements[0]  # ExpressionStatement AST
            exp = stmt.expression  # InfixExpression AST

            if not self.assert_test_literal_expression(exp.left, left_value):
                return

            if not self.assert_test_literal_expression(exp.right, right_value):
                return

            self.assertEqual(exp.operator, operator, f"exp.operator is not '{operator}'. got={exp.operator}")

            if not self.assert_test_literal_expression(exp.right, right_value):
                return

    def test_parsing_prefix_expressions(self):
        prefix_tests = [
            ["!5;", "!", 5],
            ["-15;", "-", 15],
            ["!true;", "!", True],
            ["!false;", "!", False],
        ]

        for tt in prefix_tests:
            source = tt[0]
            operator = tt[1]
            value = tt[2]

            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            self.assert_check_parser_errors(parser)

            self.assertEqual(1, len(program.statements),
                             f'program.statements does not contain 1 statements. got={len(program.statements)}')

            stmt = program.statements[0]
            exp = stmt.expression

            self.assertEqual(exp.operator, operator, f"exp.operator is not '{operator}'. got={exp.operator}")

            self.assertTrue(self.assert_test_literal_expression(exp.right, value))

    def assert_test_identifier(self, ident, value):
        if ident.value != value:
            print(f'ident.value not {value}. got={ident.value}')
            return False
        if ident.token_literal() != value:
            print(f'ident.token_literal() not {value}. got={ident.token_literal()}')
            return False
        return True

    def assert_test_infix_expression(self, op_exp, left, operator, right):
        if not self.assert_test_literal_expression(op_exp.left, left):
            return False
        if op_exp.operator != operator:
            print(f"exp.operator is not '{operator}'. got={op_exp.operator}")
            return False
        if not self.assert_test_literal_expression(op_exp.right, right):
            return False
        return True

    def assert_test_literal_expression(self, exp, expected):

        if type(expected) is int:
            return self.assert_test_integer_literal(exp, expected)
        elif type(expected) is str:
            return self.assert_test_identifier(exp, expected)
        elif type(expected) is bool:
            return self.assert_test_boolean_literal(exp, expected)

        print(f'type of expr not handled. got={type(expected)}')

        return False

    def assert_test_integer_literal(self, integ, value):
        if integ.value != value:
            print(f'integ.value not {value}. got={integ.value}')
            return True

        if integ.token_literal() != str(value):
            print(f'integ.token_literal() not {value}. got={integ.token_literal()}')
            return False

        return True

    def assert_test_boolean_literal(self, bo, value):
        if bo.value != value:
            print(f'bo.value not {value}. got={bo.value}')
            return False
        if bo.token_literal() != str(value).lower():
            print(f"bo.token_literal() not {value}. got={bo.token_literal()}")
            return False
        return True

    def test_null_literal_expression(self):
        lexer = Lexer("null;")
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assert_check_parser_errors(parser)
        self.assertEqual(1, len(program.statements),
                         f"program has not enough statements. got={len(program.statements)}")

        expression_statement = program.statements[0]
        null_literal = expression_statement.expression

        self.assertEqual(None, null_literal.value,
                         f"null_literal.value not 'null'. got={null_literal.value}")

    def test_integer_literal_expression(self):
        lexer = Lexer("5;")
        parser = Parser(lexer)

        program = parser.parse_program()
        self.assert_check_parser_errors(parser)

        self.assertEqual(1, len(program.statements),
                         f"program has not enough statements. got={len(program.statements)}")

        expression_statement = program.statements[0]
        literal = expression_statement.expression

        self.assertEqual(5, literal.value,
                         f"literal.value not {5}. got={literal.value}")

        self.assertEqual("5", literal.token_literal(),
                         f"literal.token_literal() not {5}. got={literal.token_literal()}")

    def test_identifier_expression(self):
        lexer = Lexer("foobar;")
        parser = Parser(lexer)

        program = parser.parse_program()
        self.assert_check_parser_errors(parser)

        self.assertEqual(1, len(program.statements),f'program has not enough statements. got={len(program.statements)}')

        expression_statement = program.statements[0]
        ident = expression_statement.expression

        self.assertEqual("foobar", ident.value, f'ident.value not {"foobar"} got={ident.value}')

        self.assertEqual("foobar", ident.token_literal(),
                         f"ident.token_literal() not {'foobar'}. got={ident.token_literal()}")

    def test_return_statements(self):
        source = """
            return 5;
            return 10;
            return 993322;
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()
        self.assert_check_parser_errors(parser)

        self.assertEqual(3, len(program.statements),
                         f'program.statements does not contain 3 statements. got={len(program.statements)}')

        for return_stmt in program.statements:
            self.assertEqual("return", return_stmt.token_literal(),
                             f'return_stmt.token_literal not "return", got {return_stmt.token_literal()}')

    def test_let_statements(self):
        tests = [
            ["let x = 5;", "x", 5],
            ["let y = true;", "y", True],
            ["let foobar = y;", "foobar", "y"],
        ]

        for tt in tests:
            source = tt[0]
            expected_identifier = tt[1]
            expected_value = tt[2]

            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            self.assert_check_parser_errors(parser)

            self.assertEqual(1, len(program.statements),
                             f"program.statements does not contain 1 statements. got={len(program.statements)}")

            stmt = program.statements[0]  # ExpressionStatement AST node.
            if not self.assert_test_let_statement(stmt, expected_identifier):
                return

            val = stmt.value
            if not self.assert_test_literal_expression(val, expected_value):
                return

    def assert_check_parser_errors(self, p):
        errors = p.errors
        if len(errors) == 0:
            return

        print(f'parser has {len(errors)} errors')
        for error in errors:
            print(f'parser error: {error}')

        self.fail()

    def assert_test_let_statement(self, let_stmt, name):
        self.assertEqual(let_stmt.token_literal(), "let", f's.token_literal() not let. got={let_stmt.token_literal()}')
        self.assertEqual(let_stmt.name.value, name, f'let_stmt.name.value not {name}. got={let_stmt.name.value}')
        self.assertEqual(let_stmt.name.token_literal(), name, f'let_stmt.name not {name} got={let_stmt.name}')
        return True


if __name__ == '__main__':
    unittest.main()
