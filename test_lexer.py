from tok.tok import TokenType
from lexer import lexer
from tok import *


input = """
let five = 5;
let ten = 10;

let add = fn(x, y) {
    x + y;
};

let result = add(five, ten);
!-/*5;
5 < 10 > 5;

if (5 < 10) {
    return true;
} else {
    return false;
}

10 == 10;
10 != 9;
"""

lexer = lexer.Lexer(input)
tok = lexer.next_token()

while tok.type != TokenType.EOF:
    print(tok)
    tok = lexer.next_token()
