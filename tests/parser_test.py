import unittest

from monkey.lexer.lexer import Lexer
from monkey.parser.parser import Parser


class TestParser(unittest.TestCase):

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

            if not self.assert_test_integer_literal(exp.left, left_value):
                return

            self.assertEqual(exp.operator, operator, f"exp.operator is not '{operator}'. got={exp.operator}")

            if not self.assert_test_integer_literal(exp.right, right_value):
                return

    def test_parsing_prefix_expressions(self):
        prefix_tests = [
            ["!5;", "!", 5],
            ["-15;", "-", 15],
        ]

        for tt in prefix_tests:
            lexer = Lexer(tt[0])
            parser = Parser(lexer)
            program = parser.parse_program()
            self.assert_check_parser_errors(parser)

            self.assertEqual(1, len(program.statements),
                             f'program.statements does not contain 1 statements. got={len(program.statements)}')

            stmt = program.statements[0]
            exp = stmt.expression

            self.assertEqual(exp.operator, tt[1],
                             f"exp.operator is not '{tt[1]}'. got={exp.operator}")

            self.assertTrue(self.assert_test_integer_literal(exp.right, tt[2]))

    def assert_test_integer_literal(self, integ, value):
        if integ.value != value:
            print(f'integ.value not {value}. got={integ.value}')
            return True

        if integ.token_literal() != str(value):
            print(f'integ.token_literal() not {value}. got={integ.token_literal()}')
            return False

        return True

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
        source = """
            let x = 5;
            let y = 10;
            let foobar = 838383;
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()
        self.assert_check_parser_errors(parser)

        if program is None:
            self.fail("parse_program() returned None")

        self.assertEqual(3, len(program.statements),
                         f"program.statements does not contain 3 statements. got={len(program.statements)}")

        tests = ["x", "y", "foobar"]

        i = 0
        for statement in program.statements:
            self.assertTrue(self.assert_test_let_statement(statement, tests[i]))
            i += 1

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
