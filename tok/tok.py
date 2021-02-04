from enum import Enum

class TokenType(Enum):
    ILLEGAL     = 'ILLEGAL'
    EOF         = 'EOF'

    # Identifiers + literals
    IDENT       = 'IDENT'   # add, foobar, x, y, ...
    INT         = 'INT'     # 1343456
    FLOAT       = 'FLOAT'   # 13.43456

    # Operators
    ASSIGN      = '='
    PLUS        = '+'
    MINUS       = '-'
    BANG        = '!'
    ASTERISK    = '*'
    SLASH       = '/'

    LT          = '<'
    GT          = '>'
    EQ          = '=='
    NOT_EQ      = '!='

    # Delimiters
    COMMA       = ','
    SEMICOLON   = ';'

    LPAREN      = '('
    RPAREN      = ')'
    LBRACE      = '{'
    RBRACE      = '}'

    # Keywords
    FUNCTION    = 'fn'
    LET         = 'let'
    TRUE        = 'true'
    FALSE       = 'false'
    IF          = 'if'
    ELSE        = 'else'
    RETURN      = 'return'

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

# Keywords
keywords = {}
keywords["fn"]      = TokenType.FUNCTION
keywords["let"]     = TokenType.LET
keywords["true"]    = TokenType.TRUE
keywords["false"]   = TokenType.FALSE
keywords["if"]      = TokenType.IF
keywords["else"]    = TokenType.ELSE
keywords["return"]  = TokenType.RETURN

def lookup_ident(ident):
    tok = keywords.get(ident)
    return tok if tok is not None else TokenType.IDENT