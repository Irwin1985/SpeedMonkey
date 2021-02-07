from tok.tok import *
from lexer.lexer import *

PROMPT = '>> '
def start():
    print('Hello! This is SpeedMonkey programming language!\n')
    print('Feel free to type in commands\n')
    
    while True:
        try:
            text = input(PROMPT)
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        tok = lexer.next_token()
        while tok.type != TokenType.EOF:
            print(tok)
            tok = lexer.next_token()


if __name__ == '__main__':
    start()