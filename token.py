class Token:
    """
    This represents a token.  It has a type, a lexeme, and line number
    """
    def __init__(self, lexeme, token_type, line_num):
        """
        The Constructor to create a token with lexeme, type, and line number
        """
        self.type = token_type
        self.lexeme = lexeme
        self.lineNum = line_num
        self.lexicalError = None
