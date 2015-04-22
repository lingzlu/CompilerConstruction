from collections import OrderedDict
class Bookkeeper:
    """
    Responsible for maintaining a symbol table to store tokens passed from scanner
    that are identifier or constant, each token appear only once
    """
    def __init__(self):
        """
        The Constructor to create a token with lexeme, type, and line number
        """
        # initialize an empty ordered dictionary set
        self.symtab = OrderedDict()

    def insert(self, token):
        """
        key-value pairs, key: token, value: token type
        Set will automatically maintains an unique table
        """
        self.symtab[token.lexeme] = token.type  # insert new entry

    def printTable(self): # print the symbol table to a file
        with open("symbolTable.txt", "w") as output:
            output.write ("Symbol Table\n")
            output.write ('{0:<8}{1:>12}\n'.format("Symbol", "Type"))
            output.write ("-"*25+"\n")

            for token in self.symtab:
                output.write ('{0:<8}{1:>12}\n'.format(token, self.symtab[token]))

