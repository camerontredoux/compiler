from emitter import Emitter
from lexer import Kind, Lexer


class Parser:
    def __init__(self, emitter: Emitter, lexer: Lexer):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()
        self.declared = set()
        self.went = set()

        self.token = None
        self.peek = None
        self.next()
        self.next()

    def check_token(self, kind):
        return kind == self.token.kind

    def check_peek(self, kind):
        return kind == self.peek.kind

    def match(self, kind):
        if not self.check_token(kind):
            self.abort("Expected " + kind.name + ", Got " + self.token.kind.name)
        self.next()

    def next(self):
        self.token = self.peek
        self.peek = self.lexer.token()

    def abort(self, message):
        from sys import exit

        exit("Error: " + message)

    def program(self):
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void){")
        while self.check_token(Kind.NEWLINE):
            self.next()
        while not self.check_token(Kind.EOF):
            self.statement()
        for label in self.went:
            if label not in self.declared:
                self.abort("Attempting to GOTO undeclared label: " + label)
        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

    def print(self):
        self.next()
        if self.check_token(Kind.STRING):
            self.emitter.emit_line('printf("' + self.token.text + '\\n");')
            self.next()
        else:
            self.emitter.emit('printf("%' + '.2f\\n", (float)(')
            self.expression()
            self.emitter.emit_line("));")

    def if_statement(self):
        self.next()
        self.emitter.emit("if(")
        self.comparison()
        self.match(Kind.THEN)
        self.newline()
        self.emitter.emit_line("){")

        while not self.check_token(Kind.ENDIF):
            self.statement()
        self.match(Kind.ENDIF)
        self.emitter.emit_line("}")

    def while_loop(self):
        self.next()
        self.emitter.emit("while(")
        self.comparison()
        self.match(Kind.REPEAT)
        self.newline()
        self.emitter.emit_line("){")

        while not self.check_token(Kind.ENDWHILE):
            self.statement()
        self.match(Kind.ENDWHILE)
        self.emitter.emit_line("}")

    def label(self):
        self.next()
        if self.token.text in self.declared:
            self.abort("Label already declared: " + self.token.text)
        self.declared.add(self.token.text)
        self.emitter.emit_line(self.token.text + ":")
        self.match(Kind.IDENT)

    def goto(self):
        self.next()
        self.went.add(self.token.text)
        self.emitter.emit_line("goto " + self.token.text + ";")
        self.match(Kind.IDENT)

    def input(self):
        self.next()
        if self.token.text not in self.symbols:
            self.symbols.add(self.token.text)
            self.emitter.header_line("float " + self.token.text + ";")
        self.emitter.emit_line('if(0 == scanf("%' + 'f", &' + self.token.text + ")){")
        self.emitter.emit_line(self.token.text + " = 0;")
        self.emitter.emit_line('scanf("%' + '*s");')
        self.emitter.emit_line("}")
        self.match(Kind.IDENT)

    def let(self):
        self.next()
        if self.token.text not in self.symbols:
            self.symbols.add(self.token.text)
            self.emitter.header_line("float " + self.token.text + ";")
        self.emitter.emit(self.token.text + " = ")
        self.match(Kind.IDENT)
        self.match(Kind.EQ)
        self.expression()
        self.emitter.emit_line(";")

    def statement(self):
        if self.check_token(Kind.PRINT):
            self.print()
        elif self.check_token(Kind.IF):
            self.if_statement()
        elif self.check_token(Kind.WHILE):
            self.while_loop()
        elif self.check_token(Kind.LABEL):
            self.label()
        elif self.check_token(Kind.GOTO):
            self.goto()
        elif self.check_token(Kind.INPUT):
            self.input()
        elif self.check_token(Kind.LET):
            self.let()
        else:
            self.abort(
                "Invalid statement at "
                + self.token.text
                + " ("
                + self.token.kind.name
                + ")"
            )
        self.newline()

    def expression(self):
        self.term()
        while self.check_token(Kind.PLUS) or self.check_token(Kind.MINUS):
            self.emitter.emit(self.token.text)
            self.next()
            self.term()

    def term(self):
        self.unary()
        while self.check_token(Kind.SLASH) or self.check_token(Kind.ASTERISK):
            self.emitter.emit(self.token.text)
            self.next()
            self.unary()

    def unary(self):
        if self.check_token(Kind.PLUS) or self.check_token(Kind.MINUS):
            self.emitter.emit(self.token.text)
            self.next()
        self.primary()

    def primary(self):
        if self.check_token(Kind.NUMBER):
            self.emitter.emit(self.token.text)
            self.next()
        elif self.check_token(Kind.IDENT):
            if self.token.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.token.text)
            self.emitter.emit(self.token.text)
            self.next()
        else:
            self.abort("Unexpected token at " + self.token.text)

    def comparison(self):
        self.expression()
        if self.check_comparison():
            self.emitter.emit(self.token.text)
            self.next()
            self.expression()
        else:
            self.abort("Expected comparison operator at " + self.token.text)
        while self.check_comparison():
            self.emitter.emit(self.token.text)
            self.next()
            self.expression()

    def newline(self):
        self.match(Kind.NEWLINE)
        while self.check_token(Kind.NEWLINE):
            self.next()

    def check_comparison(self):
        return (
            self.check_token(Kind.EQEQ)
            or self.check_token(Kind.NOTEQ)
            or self.check_token(Kind.GT)
            or self.check_token(Kind.GTEQ)
            or self.check_token(Kind.LT)
            or self.check_token(Kind.LTEQ)
        )
