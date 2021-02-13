"""
This is an example of a calculator that exposes the pratt parser usage.
1. First we need to create the precedence table
2. Then we need to establish the relationship between tokens and precedence operators
3. Next we must link our parsing functions with the related tokens
4. Finally we must provide some helpers in order to consume the tokens and get the parsing functions
"""
from enum import Enum


class TokenType(Enum):
    EOF = "EOF"
    INTEGER = "INTEGER"
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    BANG = "!"
    LPAREN = "("
    RPAREN = ")"
    LESS = "<"
    GREATER = ">"
    LESS_EQ = "<="
    GREATER_EQ = ">="
    EQUAL = "=="
    NOT_EQ = "!="


class Token:
    def __init__(self, type, value = None):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token(type:{self.type}, value:{self.value})'

    def __repr__(self):
        return self.__str__()


class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.cur_char = self.source[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.source) - 1:
            self.cur_char = None
        else:
            self.cur_char = self.source[self.pos]

    def skip_comments(self):
        while self.cur_char is not None and self.cur_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.cur_char is not None and self.cur_char.isdigit():
            result += self.cur_char
            self.advance()
        return Token(type=TokenType.INTEGER, value=int(result))

    def get_next_token(self):
        while self.cur_char is not None:
            if self.cur_char.isspace():
                self.skip_comments()
                continue

            if self.cur_char.isdigit():
                return self.number()

            if self.cur_char == '+':
                self.advance()
                return Token(type=TokenType.PLUS, value="+")

            if self.cur_char == '-':
                self.advance()
                return Token(type=TokenType.MINUS, value="-")

            if self.cur_char == '*':
                self.advance()
                return Token(type=TokenType.MUL, value="*")

            if self.cur_char == '/':
                self.advance()
                return Token(type=TokenType.DIV, value="/")

            if self.cur_char == '!':
                self.advance()
                if self.cur_char == '=':
                    self.advance()
                    return Token(type=TokenType.NOT_EQ, value="!=")

                return Token(type=TokenType.BANG, value="!")

            if self.cur_char == '<':
                self.advance()
                if self.cur_char == '=':
                    self.advance()
                    return Token(type=TokenType.LESS_EQ, value="<=")

                return Token(type=TokenType.LESS, value="<")

            if self.cur_char == '>':
                self.advance()
                if self.cur_char == '=':
                    self.advance()
                    return Token(type=TokenType.GREATER_EQ, value=">=")

                return Token(type=TokenType.GREATER, value=">")

            print(f'Lexer error: unknown character {self.cur_char}')

        return Token(type=TokenType.EOF, value=None)


"""
Here in the parser we need to create the following:
1. The precedence table enumerable.
2. The token and precedence relationship data type.
"""


class Precedence(Enum):
    LOWEST = 1
    EQUALITY = 2
    COMPARISON = 3
    TERM = 4
    FACTOR = 5
    UNARY = 6


class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.cur_token = None
        self.peek_token = None
        self.next_tokens()
        self.next_tokens()
        """
        The following is the arithmetical token and precedence order relationship dictionary.
        When you access the token key you get the operator precedence order.
        """
        self.precedence = {
            TokenType.EQUAL: int(Precedence.EQUALITY.value),
            TokenType.NOT_EQ: int(Precedence.EQUALITY.value),
            TokenType.LESS: int(Precedence.COMPARISON.value),
            TokenType.GREATER: int(Precedence.COMPARISON.value),
            TokenType.LESS_EQ: int(Precedence.COMPARISON.value),
            TokenType.GREATER_EQ: int(Precedence.COMPARISON.value),
            TokenType.PLUS: int(Precedence.TERM.value),
            TokenType.MINUS: int(Precedence.TERM.value),
            TokenType.MUL: int(Precedence.FACTOR.value),
            TokenType.DIV: int(Precedence.FACTOR.value),
        }
        """
        Next up, we need to create the parsing functions-token relationship dictionary.        
        """
        # prefix functions
        self.prefix_parsing_functions = {
            TokenType.INTEGER: self.parse_integer_literal,
            TokenType.MINUS: self.parse_prefix_expression,
        }
        # infix functions
        self.infix_parsing_functions = {
            TokenType.PLUS: self.parse_infix_expression,
        }

    """
    The following functions are called `parsing functions` or `semantic code`
    we'll write them in the following order:
    1. parse_integer_literal # 1, 2, 3, ...
    2. parse_prefix_expression # -1, -2, -3, ...
    3. parse_infix_expression # 1 + 2, 5 - 4, 3 * 2, ...
    4. parse_grouped_expression # ((1 + 2) * 3) + 4
    5. parse_expression
    """
    def parse_integer_literal(self):
        return self.cur_token.value

    def parse_prefix_expression(self):
        self.next_tokens()
        operand = self.parse_expression(int(Precedence.UNARY.value))
        return operand * -1
    """
    steps:
    1. Get and save the current precedence (self.cur_token)
    2. Advance the tokens
    3. Parse the right hand expression passing the saved precedence
    4. Return the AST or value.
    """
    def parse_infix_expression(self, left):
        precedence = self.cur_precedence()
        operator = self.cur_token.type
        self.next_tokens()
        right_exp = self.parse_expression(precedence=precedence)

        result = 0
        if operator == TokenType.PLUS:
            result = left + right_exp

        return result

    def parse_grouped_expression(self):
        pass

    def parse_expression(self, precedence):
        # first we find if is there any parsing function related to our current token.
        prefix = self.prefix_parsing_functions.get(self.cur_token.type)
        # if there is no parsing function related then we report an error.
        if prefix is None:
            print(f'no prefix parsing function for the token: {self.cur_token.type}')
            return None

        # if the searching success then we call the function

        left_exp = prefix()
        """
        infix algorithm:
        1. Loop while precedence parameter value is less than peek_precedence
        2. find for a parsing function related to the peek token type.
        3. if no function found then return prefix value
        4. if found then call the infix function fetched passing the left_exp value.
        """
        peek_precedence = self.peek_precedence()
        while precedence < peek_precedence:
            infix = self.infix_parsing_functions.get(self.peek_token.type)
            if infix is None:
                return left_exp
            self.next_tokens()
            left_exp = infix(left_exp)
            peek_precedence = self.peek_precedence()

        return left_exp

    """
    And here will define some helpers methods
    """
    def next_tokens(self):
        self.cur_token = self.peek_token
        self.peek_token = self.tokenizer.get_next_token()

    def match_peek(self, token_type):
        if self.peek_token.type == token_type:
            self.next_tokens()
            return True
        else:
            print(f'expect token to be {token_type}, got={self.peek_token.type} instead.')
            return False
    """
        This helper method returns the current precedence order
        for the current_token type.
    """
    def cur_precedence(self):
        precedence = self.precedence.get(self.cur_token.type)
        return int(Precedence.LOWEST.value) if precedence is None else precedence

    def peek_precedence(self):
        precedence = self.precedence.get(self.peek_token.type)
        return int(Precedence.LOWEST.value) if precedence is None else precedence


if __name__ == '__main__':
    tokenizer = Tokenizer(source="1985+1985")
    parser = Parser(tokenizer=tokenizer)
    print(parser.parse_expression(int(Precedence.LOWEST.value)))