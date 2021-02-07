from monkey.ast.ast import (
    Program,
    LetStatement,
    Identifier,
    ReturnStatement,
    ExpressionStatement,
    IntegerLiteral,
    PrefixExpression,
    InfixExpression,
)

from monkey.tok.tok import TokenType

from enum import Enum


class Precedence(Enum):
    LOWEST = 1,
    EQUALS = 2,  # ==
    LESSGREATER = 3,  # < or >
    SUM = 4,  # +
    PRODUCT = 5,  # *
    PREFIX = 6,  # -X or !X
    CALL = 7,  # myFunction(X)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.cur_token = None
        self.peek_token = None
        self.errors = []

        # parsing function dictionary
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}

        # precedence table
        self.precedence = {
            TokenType.EQ: Precedence.EQUALS,
            TokenType.NOT_EQ: Precedence.EQUALS,
            TokenType.LT: Precedence.LESSGREATER,
            TokenType.GT: Precedence.LESSGREATER,
            TokenType.PLUS: Precedence.SUM,
            TokenType.MINUS: Precedence.SUM,
            TokenType.SLASH: Precedence.PRODUCT,
            TokenType.ASTERISK: Precedence.PRODUCT,
        }

        # register prefix tokens
        self.register_prefix_function(TokenType.IDENT, self.parse_identifier)
        self.register_prefix_function(TokenType.INT, self.parse_integer_literal)
        self.register_prefix_function(TokenType.BANG, self.parse_prefix_expression)
        self.register_prefix_function(TokenType.MINUS, self.parse_prefix_expression)

        # register infix tokens
        self.register_infix_function(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix_function(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix_function(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix_function(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix_function(TokenType.EQ, self.parse_infix_expression)
        self.register_infix_function(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix_function(TokenType.LT, self.parse_infix_expression)
        self.register_infix_function(TokenType.GT, self.parse_infix_expression)

        # set the current and peek token
        self.next_token()
        self.next_token()

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self):
        program = Program()

        while not self.cur_token_is(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()

        return program

    def parse_statement(self):
        if self.cur_token.type == TokenType.LET:
            return self.parse_let_statement()
        elif self.cur_token.type == TokenType.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self):
        stmt = LetStatement(self.cur_token)

        if not self.expect_peek(TokenType.IDENT):
            return None

        stmt.name = Identifier(self.cur_token, self.cur_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        # TODO: We're skipping the expressions until we encounter a semicolon
        while not self.cur_token_is(TokenType.SEMICOLON):
            self.next_token()

        return stmt

    def parse_return_statement(self):
        return_stmt = ReturnStatement(token=self.cur_token)

        self.next_token()  # eat RETURN token

        while not self.cur_token_is(TokenType.SEMICOLON):
            self.next_token()  # skip expressions for now.

        return return_stmt

    def parse_expression_statement(self):
        stmt = ExpressionStatement(token=self.cur_token)

        stmt.expression = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):  # ';' is optional to ease expression typing on the REPL.
            self.next_token()

        return stmt

    def parse_expression(self, precedence):
        prefix = self.prefix_parse_fns.get(self.cur_token.type)

        if prefix is None:
            self.no_prefix_parse_fn_error(self.cur_token.type)
            return None

        left_exp = prefix()

        while not self.peek_token_is(TokenType.SEMICOLON) and int(precedence.value[0]) < self.peek_precedence():
            infix = self.infix_parse_fns.get(self.peek_token.type)
            if infix is None:
                return left_exp

            self.next_token()  # eat the prefix (left expression) token.

            left_exp = infix(left_exp)

        # TODO: implement here the posfix operators.

        return left_exp

    def parse_identifier(self):
        return Identifier(token=self.cur_token, value=self.cur_token.literal)

    def parse_integer_literal(self):
        lit = IntegerLiteral(token=self.cur_token)

        value = int(self.cur_token.literal)
        lit.value = value

        return lit

    def cur_token_is(self, t):
        return self.cur_token.type == t

    def parse_prefix_expression(self):
        expression = PrefixExpression(token=self.cur_token, operator=self.cur_token.literal)
        self.next_token()  # eat the '!' or '-' token

        expression.right = self.parse_expression(Precedence.PREFIX)

        return expression

    def parse_infix_expression(self, left):
        expression = InfixExpression(
            token=self.cur_token,
            operator=self.cur_token.literal,
            left=left,
        )

        precedence = self.cur_precedence()
        self.next_token()  # eat the infix operator.
        expression.right = self.parse_expression(precedence=precedence)

        return expression

    def peek_token_is(self, t):
        return self.peek_token.type == t

    def expect_peek(self, t):
        if self.peek_token_is(t):
            self.next_token()  # eat the current token.
            return True
        else:
            self.peek_error(t)
            return False

    def peek_error(self, t):
        msg = f'expected next token to be {t}, got {self.peek_token.type}'
        self.errors.append(msg)

    def peek_precedence(self):
        p = self.precedence.get(self.peek_token.type)
        return int(p.value[0]) if p is not None else int(Precedence.LOWEST.value[0])

    def cur_precedence(self):
        p = self.precedence.get(self.cur_token.type)
        return p if p is not None else Precedence.LOWEST

    def no_prefix_parse_fn_error(self, t):
        msg = f'no prefix parse function for {t}'
        self.errors.append(msg)

    # pratt parser functions helpers
    def register_prefix_function(self, token_type, prefix_function):
        self.prefix_parse_fns[token_type] = prefix_function

    def register_infix_function(self, token_type, infix_function):
        self.infix_parse_fns[token_type] = infix_function

