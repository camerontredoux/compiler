from enum import Enum
from dataclasses import dataclass


class Kind(Enum):
    EOF = -1
    ERR = 999
    # Other
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ELIF = 115
    ELSE = 116
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    FOR = 112
    TO = 113
    NEXT = 114
    # Operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211
    MOD = 212


@dataclass
class Token:
    text: str
    kind: Kind


class Lexer:
    def __init__(self, input):
        self.input = input + "\n"
        self.curr = ""
        self.idx = -1
        self.next()

    def next(self):
        self.idx += 1
        if self.idx >= len(self.input):
            self.curr = "\0"
        else:
            self.curr = self.input[self.idx]

    def peek(self):
        if self.idx + 1 >= len(self.input):
            return "\0"
        return self.input[self.idx + 1]

    def skip(self):
        while self.curr == " " or self.curr == "\t" or self.curr == "\r":
            self.next()

        if self.curr == "#":
            while self.curr != "\n":
                self.next()

    def abort(self, message):
        from sys import exit

        exit("Lexing error: " + message)

    def peek_next(self, next, kind1, kind2):
        token = None
        if self.peek() == next:
            token = Token(self.curr + self.peek(), kind1)
            self.next()
        else:
            if kind2 == Kind.ERR:
                self.abort("Expected !=, Got !" + self.peek())
            else:
                token = Token(self.curr, kind2)
        return token

    def token(self):
        self.skip()
        token = None
        match self.curr:
            case "+":
                token = Token(self.curr, Kind.PLUS)
            case "-":
                token = Token(self.curr, Kind.MINUS)
            case "*":
                token = Token(self.curr, Kind.ASTERISK)
            case "/":
                token = Token(self.curr, Kind.SLASH)
            case "\n":
                token = Token(self.curr, Kind.NEWLINE)
            case "\0":
                token = Token(self.curr, Kind.EOF)
            case "%":
                token = Token(self.curr, Kind.MOD)
            case "=":
                token = self.peek_next("=", Kind.EQEQ, Kind.EQ)
            case ">":
                token = self.peek_next("=", Kind.GTEQ, Kind.GT)
            case "<":
                token = self.peek_next("=", Kind.LTEQ, Kind.LT)
            case "!":
                token = self.peek_next("=", Kind.NOTEQ, Kind.ERR)
            case '"':
                self.next()
                start = self.idx
                while self.curr != '"':
                    self.next()
                text = self.input[start : self.idx]
                token = Token(text, Kind.STRING)
            case _ if self.curr.isdigit():
                start = self.idx
                while self.peek().isdigit():
                    self.next()
                if self.peek() == ".":
                    self.next()
                    if not self.peek().isdigit():
                        self.abort("Illegal character in number.")
                    while self.peek().isdigit():
                        self.next()
                number = self.input[start : self.idx + 1]
                token = Token(number, Kind.NUMBER)
            case _ if self.curr.isalpha():
                start = self.idx
                while self.peek().isalnum():
                    self.next()
                ident = self.input[start : self.idx + 1]
                keywords = {
                    kind.name: kind
                    for kind in Kind
                    if kind.value >= 100 and kind.value < 200
                }
                if ident in keywords:
                    token = Token(ident, keywords[ident])
                else:
                    token = Token(ident, Kind.IDENT)
            case _:
                self.abort("Unknown token: " + self.curr)
        self.next()
        return token
