class Bookkeeper:
    """
    Responsible for maintaining a symbol table to store tokens passed from scanner
    that are identifier or constant, each token appear only once
    """
    def __init__(self):
        """
        The Constructor to create a token with lexeme, type, and line number
        """
        self.symtab = {}  # initialize an empty dictionary set

    def insert(self, token):
        """
        key-value pairs, key: token, value: token type
        Set will automatically maintains an unique table
        """
        self.symtab[token.lexeme] = token.type  # insert new entry

    def printTable(self): # print the symbol table to a file
        output = open("symbolTable.txt", "w")
        output.write ("Symbol Table\n")
        for token in self.symtab:
            output.write ("%s\t%s\n"% (token, self.symtab[token]))


