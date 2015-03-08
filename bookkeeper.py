class Bookkeeper:
    """
    This represents a token.  It has a type, a lexeme, and line number
    """
    def __init__(self):
        """
        The Constructor to create a token with lexeme, type, and line number
        """
        self.symtab = {}  # symbol table

    def insert(self, token):
        self.symtab[token.lexeme] = token.type

    def printTable(self):
        output = open("symbolTable.txt", "w")
        output.write ("Symbol Table\n")
        for token in self.symtab:
            output.write ("%s\t%s\n"% (token, self.symtab[token]))


