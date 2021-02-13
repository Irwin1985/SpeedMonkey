from monkey.parser.parser import Parser
from monkey.lexer.lexer import Lexer

from enum import Enum

class MyEnum(Enum):
    FIRST = 0,
    SECOND = 1,
    THIRD = 2,

# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def test_expression():
    source = "1 + 2 + 3;"
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    print(program.string())

def print_bye(name):
    print(f'Good bye {name}')


def main():

    test = {
        "hola": print_hi,
        "adios": print_bye,
    }

    token_type = "hola"

    my_func = test.get(token_type)
    if my_func is not None:
        my_func("PyCharm!")

    bye = test.get("adios")
    if bye is not None:
        bye('Julian!')




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test_expression()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
