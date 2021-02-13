from monkey.lexer.lexer import Lexer
from monkey.parser.parser import Parser
from monkey.evaluator.evaluator import Evaluator

PROMPT = '>> '

MONKEY_FACE = """
            __,__
   .--.  .-"     "-.  .--.
  / .. \/  .-. .-.  \/ .. \
 | |  '|  /   Y   \  |'  | |
 | \   \  \ 0 | 0 /  /   / |
  \ '- ,\.-"""""""-./, -' /
   ''-' /_   ^ ^   _\ '-''
       |  \._   _./  |
       \   \ '~' /   /
        '._ '-=-' _.'
           '-----'
"""


def start():
    print('Hello! This is SpeedMonkey programming language!\n')
    print('Feel free to type in commands\n')
    
    while True:
        try:
            source = input(PROMPT)
        except EOFError:
            break
        if not source:
            continue

        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        if len(parser.errors) != 0:
            print_parser_errors(parser.errors)

        evaluator = Evaluator()
        evaluated = evaluator.eval(program)
        if evaluated is not None:
            print(evaluated.inspect())


def print_parser_errors(errors):
    print(MONKEY_FACE)
    print("Whoops! We ran into some monkey business here!")
    print(" parser errors:")
    for error in errors:
        print(error)


if __name__ == '__main__':
    start()