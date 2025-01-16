class Emitter:
    def __init__(self, output):
        self.output = output
        self.header = ""
        self.code = ""

    def emit(self, code):
        self.code += code

    def emit_line(self, code):
        self.code += code + "\n"

    def header_line(self, code):
        self.header += code + "\n"

    def write(self):
        with open(self.output, "w") as out:
            out.write(self.header + self.code)
