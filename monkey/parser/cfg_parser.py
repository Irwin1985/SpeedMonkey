from monkey.tok.tok import TokenType

from monkey.ast.ast import (
    Program,
    LetStatement,
    Identifier,
    ReturnStatement,
    ExpressionStatement,
    IntegerLiteral,
    PrefixExpression,
    InfixExpression,
    Boolean,
    IfExpression,
    BlockStatement,
    FunctionLiteral,
    CallExpression,
    NullLiteral,
)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.cur_token = None
        self.peek_token = None
        self.errors = []
        self.next_token()
        self.next_token()

    def eat(self, token_type):
        if self.cur_token.type == token_type:
            self.next_token()
        else:
            msg = f'expected token to be {token_type}, got {self.cur_token.type} instead'
            self.errors.append(msg)

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def program(self):
        """
        program ::= (statement)+ EOF
        """
        program = Program()
        while self.cur_token.type != TokenType.EOF:
            statement = self.statement()
            if statement is not None:
                program.statements.append(statement)

        return program

    def block(self):
        block = BlockStatement(token=self.cur_token)
        self.eat(TokenType.LBRACE)

        while self.cur_token.type != TokenType.RBRACE:
            statement = self.statement()
            if statement is not None:
                block.statements.append(statement)

        self.eat(TokenType.RBRACE)

        return block

    def statement(self):
        if self.cur_token.type == TokenType.LET:
            return self.let_statement()
        elif self.cur_token.type == TokenType.RETURN:
            return self.return_statement()
        else:
            return self.expression_statement()

    def expression_statement(self):
        stmt = ExpressionStatement(token=self.cur_token)

        stmt.expression = self.expression()

        return stmt

    def let_statement(self):
        stmt = LetStatement(token=self.cur_token)
        self.eat(TokenType.LET)

        # identifier AST
        stmt.name = self.identifier()

        self.eat(TokenType.ASSIGN)

        # expression AST
        stmt.value = self.expression()

        return stmt

    def return_statement(self):
        stmt = ReturnStatement(token=self.cur_token)
        self.eat(TokenType.RETURN)

        stmt.return_value = self.expression()

        return stmt

    def expression(self):
        exp = self.equality()

        if self.cur_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)

        return exp

    def equality(self):
        equ = self.comparison()
        while self.cur_token.type in (TokenType.EQ, TokenType.NOT_EQ):
            tok = self.cur_token
            self.eat(tok.type)
            equ = InfixExpression(
                token=tok,
                left=equ,
                operator=tok.literal,
                right=self.comparison(),
            )

        return equ

    def comparison(self):
        comp = self.term()
        while self.cur_token.type in (TokenType.LT, TokenType.GT):
            tok = self.cur_token
            self.eat(tok.type)
            comp = InfixExpression(
                token=tok,
                left=comp,
                operator=tok.literal,
                right=self.comparison(),
            )

        return comp

    def term(self):
        exp = self.factor()

        while self.cur_token.type in (TokenType.PLUS, TokenType.MINUS):
            tok = self.cur_token
            self.eat(tok.type)
            exp = InfixExpression(
                token=tok,
                operator=tok.literal,
                left=exp,
                right=self.factor(),
            )

        return exp

    def factor(self):
        unary = self.unary()
        while self.cur_token.type in (TokenType.ASTERISK, TokenType.SLASH):
            tok = self.cur_token
            self.eat(tok.type)
            unary = InfixExpression(
                token=tok,
                operator=tok.literal,
                left=unary,
                right=self.unary(),
            )

        return unary

    def unary(self):
        if self.cur_token.type in (TokenType.MINUS, TokenType.BANG):
            operator = self.cur_token
            self.eat(self.cur_token.type)
            return PrefixExpression(token=self.cur_token, operator=operator.literal, right=self.unary())
        else:
            return self.call()

    def call(self):
        primary = self.primary()

        if self.cur_token.type == TokenType.LPAREN:
            function = primary
            primary = CallExpression(token=self.cur_token)
            primary.function = function

            self.eat(TokenType.LPAREN)

            if self.cur_token.type != TokenType.RPAREN:
                primary.arguments = self.parse_call_arguments()

            self.eat(TokenType.RPAREN)

        return primary

    def parse_call_arguments(self):
        args = [self.expression()]

        while self.cur_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            args.append(self.expression())

        return args

    def primary(self):
        tok = self.cur_token

        if tok.type in (TokenType.TRUE, TokenType.FALSE):
            self.eat(tok.type)
            return Boolean(token=tok, value=(tok.type == TokenType.TRUE))

        elif tok.type == TokenType.NULL:
            self.eat(tok.type)
            return Boolean(token=tok, value=None)

        elif tok.type == TokenType.INT:
            self.eat(TokenType.INT)
            return IntegerLiteral(token=tok, value=int(tok.literal))

        elif tok.type == TokenType.IDENT:
            return self.identifier()

        elif tok.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            exp = self.expression()
            self.eat(TokenType.RPAREN)
            return exp

        elif tok.type == TokenType.FUNCTION:
            return self.function_literal()

        elif tok.type == TokenType.IF:
            return self.if_expression()

    def if_expression(self):
        if_exp = IfExpression(token=self.cur_token)
        self.eat(TokenType.IF)

        self.eat(TokenType.LPAREN)
        if_exp.condition = self.expression()
        self.eat(TokenType.RPAREN)

        if_exp.consequence = self.block()

        if self.cur_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            if_exp.alternative = self.block()

        return if_exp

    def function_literal(self):
        lit = FunctionLiteral(
            token=self.cur_token,
        )
        self.eat(TokenType.FUNCTION)
        self.eat(TokenType.LPAREN)

        if self.cur_token.type != TokenType.RPAREN:
            lit.parameters = self.parse_function_parameters()

        self.eat(TokenType.RPAREN)

        lit.body = self.block()

        return lit

    def parse_function_parameters(self):

        identifiers = [self.identifier()]

        while self.cur_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            identifiers.append(self.identifier())

        return identifiers

    def identifier(self):
        ident = Identifier(
            token=self.cur_token,
            value=self.cur_token.literal,
        )
        self.eat(TokenType.IDENT)

        return ident

    def parse_program(self):
        program = self.program()
        if self.cur_token.type != TokenType.EOF:
            self.errors.append(f'Unexpected token {self.cur_token.type}')

        return program
