from monkey.tok.tok import Token, TokenType, lookup_ident


def error(msg=None) -> object:
    if msg is None:
        msg = 'Lexer Error'
    raise Exception(msg)


def is_letter(ch):
    return ch.isalnum() or ch == "_"


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

    def skip_comments(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

        if self.current_char is None:
            error('Unexpected end of file')

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

            error('Illegal character ' + self.current_char)

        return Token(TokenType.EOF, "")

    def read_identifier(self):
        position = self.pos
        while self.current_char is not None and is_letter(self.current_char):
            self.advance()

        return self.input[position:self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
