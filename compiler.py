from lexer import Lexer
from emitter import Emitter
from parser import Parser
import sys


def main():
    print("Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Must specify input source file.")

    with open(sys.argv[1], "r") as f:
        source = f.read()
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(emitter, lexer)
    parser.program()
    emitter.write()


if __name__ == "__main__":
    main()
