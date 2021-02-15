from enum import Enum

"""
This version of Monkey lang will change:
1. The Pratt Parser for a CFG Parser.
2. The Eval() method for a Visitor Pattern.
3. The AST "interface structure" for a single based class.
"""


class Environment:
    def __init__(self):
        self.store = {}
        self.outer = None

    def get(self, name):
        result = self.store.get(name)

        if result is None and self.outer is not None:
            result = self.outer.get(name)

        return result

    def set(self, name, val):
        self.store[name] = val


# Instance method
def new_enclosed_environment(outer):
    env = Environment()
    env.outer = outer
    return env


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


class TokenType(Enum):
    ILLEGAL = 'ILLEGAL'
    EOF = 'EOF'

    # Identifiers + literals
    IDENT = 'IDENT'  # add, foobar, x, y, ...
    INT = 'INT'  # 1343456
    FLOAT = 'FLOAT'  # 13.43456

    # Operators
    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    BANG = '!'
    ASTERISK = '*'
    SLASH = '/'

    LT = '<'
    GT = '>'
    EQ = '=='
    NOT_EQ = '!='

    # Delimiters
    COMMA = ','
    SEMICOLON = ';'

    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'

    # Keywords
    FUNCTION = 'fn'
    LET = 'let'
    TRUE = 'true'
    FALSE = 'false'
    IF = 'if'
    ELSE = 'else'
    RETURN = 'return'
    NULL = 'null'


NULL = Null()
TRUE = Boolean(value=True)
FALSE = Boolean(value=False)

keywords = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    "null": TokenType.NULL,
}


class Token:
    def __init__(self, type, literal):
        self.type = type
        self.literal = literal

    def __str__(self):
        return 'type: {type}, literal: {literal}'.format(
            type=self.type,
            literal=self.literal
        )

    __repr__ = __str__


def lookup_ident(ident):
    tok = keywords.get(ident)
    return tok if tok is not None else TokenType.IDENT


def lexer_error(msg=None):
    if msg is None:
        msg = 'Lexer Error'
    raise Exception(msg)


def is_letter(ch):
    return ch.isalnum() or ch == "_"


"""
The Lexer Class
"""


class Lexer:
    def __init__(self, source):
        self.input = source
        self.pos = 0
        self.current_char = self.input[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.input) - 1:
            self.current_char = None
        else:
            self.current_char = self.input[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.input) - 1:
            return None
        else:
            return self.input[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comments(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

        if self.current_char is None:
            lexer_error('Unexpected end of file')

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.' and self.peek().isdigit():
            result += self.current_char
            self.advance()  # skip the '.'
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        return Token(TokenType.INT, result)

    def identifier(self):
        result = ''
        while self.current_char is not None and is_letter(self.current_char):
            result += self.current_char
            self.advance()

        return Token(lookup_ident(result), result)

    def next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and self.peek() == '/':
                self.advance()  # skip first slash
                self.advance()  # skip second slash
                self.skip_comments()
                continue

            if self.current_char.isdigit():
                return self.number()

            if is_letter(self.current_char):
                return self.identifier()

            # single character token
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()  # eat the first '='
                    self.advance()  # eat the second '='
                    return Token(TokenType.EQ, '==')
                else:
                    self.advance()
                    return Token(TokenType.ASSIGN, '=')

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-')

            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()  # eat the '!'
                    self.advance()  # eat the '='
                    return Token(TokenType.NOT_EQ, '!=')
                else:
                    self.advance()
                    return Token(TokenType.BANG, '!')

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.SLASH, '/')

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.ASTERISK, '*')

            if self.current_char == '<':
                self.advance()
                return Token(TokenType.LT, '<')

            if self.current_char == '>':
                self.advance()
                return Token(TokenType.GT, '>')

            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';')

            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',')

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')

            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{')

            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}')

            lexer_error('Illegal character ' + self.current_char)

        return Token(TokenType.EOF, "")

    def read_identifier(self):
        position = self.pos
        while self.current_char is not None and is_letter(self.current_char):
            self.advance()

        return self.input[position:self.pos]


"""
The AST structure
"""


class AST:
    def token_literal(self):
        pass

    def string(self):
        pass


class Program(AST):
    def __init__(self):
        self.statements = []

    def token_literal(self):
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""

    def string(self):
        out = ""

        for statement in self.statements:
            out += statement.string()

        return out


class BlockStatement(AST):
    def __init__(self, token):
        self.token = token
        self.statements = []

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = ""

        for statement in self.statements:
            out += statement.string()

        return out


class IntegerLiteral(AST):
    def __init__(self, token, value=None):
        self.token = token
        self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class BooleanLiteral(AST):
    def __init__(self, token, value=None):
        self.token = token
        self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class NullLiteral(AST):
    def __init__(self, token, value=None):
        self.token = token
        self.value = None

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class Identifier(AST):
    def __init__(self, token, value = None):
        self.token = token
        self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.value


class UnaryOp(AST):
    def __init__(self, token, operator=None, right=None):
        self.token = token
        self.operator = operator
        self.right = right

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = "("
        out += self.operator
        out += self.right.string()
        out += ")"

        return out


class FunctionLiteral(AST):
    def __init__(self, token):
        self.token = token
        self.parameters = []
        self.body = None

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = ""
        params = []
        for parameter in self.parameters:
            params.append(parameter.string())

        out += "("
        out += ", ".join(params) + ") "
        out += self.body.string()

        return out


class BinaryOp(AST):
    def __init__(self, token, left=None, operator=None, right=None):
        self.token = token
        self.left = left
        self.operator = operator
        self.right = right

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = "("
        out += self.left.string()
        out += " " + self.operator + " "
        out += self.right.string()
        out += ")"
        return out


class LetStatement(AST):
    def __init__(self, token, name=None, value=None):
        self.token = token
        self.name = name
        self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = self.token.literal + " "
        out += self.name.string()
        out += " = "

        if self.value is not None:
            out += self.value.string()

        out += ";"
        return out


class ReturnStatement(AST):
    def __init__(self, token, return_value=None):
        self.token = token
        self.return_value = return_value

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = self.token.literal + " "

        if self.return_value is not None:
            out += self.return_value.string()

        out += ";"

        return out


class CallExpression(AST):
    def __init__(self, token):
        self.token = token
        self.function = None
        self.arguments = []

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = ""

        args = []
        for a in self.arguments:
            args.append(a.string())

        out += self.function.string()
        out += "("
        out += ", ".join(args)
        out += ")"

        return out


class IfExpression(AST):
    def __init__(self, token, condition=None, consequence=None, alternative=None):
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = "if ("
        out += self.condition.string()
        out += ")"
        out += "{"
        out += self.consequence.string()

        if self.alternative is not None:
            out += "else"
            out += "{"
            out += self.alternative.string()
            out += "}"

        out += "}"

        return out

"""
Next, we'll create the Context Free Grammar Parser
Here's the Monkey Grammar we'll follow:
program             ::= statement_list
statement_list      ::= statement (';' statement)*
statement           ::= let_statement | return_statement
let_statement       ::= 'let' '=' expression (';')?
return_statement    ::= 'return' expression (';')?
expression          ::= term ( ('+' | '-') term)*
term                ::= factor ( ('*' | '/') factor)*
factor              ::= unary_op
                      | identifier
                      | integer_literal
                      | boolean_literal
                      | function_literal
                      | function_call
unary_op            ::= ('!' | '-') factor
"""


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
            return self.expression()

    def let_statement(self):
        stmt = LetStatement(token=self.cur_token)
        self.eat(TokenType.LET)

        # identifier AST
        stmt.name = self.identifier()

        self.eat(TokenType.ASSIGN)

        # expression AST
        stmt.value = self.expression()

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
            equ = BinaryOp(
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
            comp = BinaryOp(
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
            exp = BinaryOp(
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
            unary = BinaryOp(
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
            return UnaryOp(token=self.cur_token, operator=operator.literal, right=self.unary())
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
            return BooleanLiteral(token=tok, value=(tok.type == TokenType.TRUE))

        elif tok.type == TokenType.NULL:
            self.eat(tok.type)
            return BooleanLiteral(token=tok, value=None)

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

    def parse(self):
        program = self.program()
        if self.cur_token.type != TokenType.EOF:
            self.errors.append(f'Unexpected token {self.cur_token.type}')

        return program


class NodeVisitor:

    def visit(self, node, env):
        method_name = 'visit_' + type(node).__name__
        method_name = method_name.lower()

        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, env)

    def generic_visit(self, node, env):
        raise Exception(f'No visitor method for the AST: {type(node).__name__}')

    def visit_program(self, node, env):
        result = None

        for stmt in node.statements:
            result = self.visit(stmt, env)

            if result is not None:
                if result.type() == Type.RETURN_VALUE_OBJ:
                    return result.value
                elif result.type() == Type.ERROR_OBJ:
                    return result

            return result


    def visit_integerliteral(selfs, node, _):
        return Integer(node.value)

    def visit_unaryop(self, node, env):
        right = self.visit(node.right, env)
        if is_error(right):
            return right

        if node.operator == "!":
            if right == TRUE:
                return FALSE
            elif right == FALSE:
                return TRUE
        elif node.operator == "-":
            if not isinstance(right, Integer):
                return Error(f"unknown operator: -{right.type().value}")
            return Integer(value=-right.value)

def is_error(node):
    return node is not None and isinstance(node, Error)