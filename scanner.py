from token import Token
import re
from enum import Enum

class LexicalError(Enum):
    InvalidSyntax = 1 # any error not defined
    InvalidIdentifier = 2  # identifier contains some unrecognized symbol
    InvalidConstant = 3  # Starting with constant follow by a letter
    UnrecognizedSymbol = 4  # symbol not recognized in our special symbols
    MultipleDecimals = 5  # constant contains multiple decimal points


class Scanner:
    """
    The scanner module for compiler
    """
    def __init__(self, sourceFile):
        self.sourceCode = open(sourceFile, 'r')  #source code to be scanned
        self.lineNum = 1  # counter for line number
        self.lexeme = ""  #buffer to store scanned character
        self.tokens = []  # store next recognized tokens
        self.lexicalError = None

    def getNextValidChar(self):
        """
        returns next non-space and non-comment character
        """
        char = self.sourceCode.read(1)  # read next character

        while True:
            if char == '\t' or char == ' ':  # tab or space
                char = self.sourceCode.read(1)
            elif char == '\n' or char == '\r':  # newline or carriage return
                self.lineNum += 1
                char = self.sourceCode.read(1)
            elif char == '#':  # comment character, ignore everything after it
                self.sourceCode.readline()  # skip rest of this line
                self.lineNum += 1  # increment line number
                char = self.sourceCode.read(1)  # read first character of next line
            else:
                break  # anything none space or comment line will break
        return char

    def nextToken(self):
        """
        scan character by character to find the next token using DFA
        token separators are space and special symbols
        this function might return up to 2 tokens when a special symbol is
        concatenate with another token
        """

        # initial variables for new token
        self.lexeme = ""
        self.tokens = []
        self.lexicalError = None

        char = self.getNextValidChar()
        if not char:  # end of the file found
            self.tokens = None
            return

        self.lexeme += char  # keep track of scanned char before a token found

        # side comments indicate starting symbol might lead to possible keyword or SS
        if char == 'p':  # package, private, protected, print
            self.block_p()
        elif char == 'i':  # import, if, in, int
            self.block_i()
        elif char == 'a':  # abstract, and
            self.block_a()
        elif char == 'f':  # final, false
            self.block_f()
        elif char == 's':  # sealed
            self.block_s()
        elif char == 'c':  # class, case
            self.block_c()
        elif char == 'o':  # object, or
            self.block_o()
        elif char == 'v':  # val
            self.block_v()
        elif char == 'd':  # def
            self.block_d()
        elif char == 'e':  # else
            self.block_e()
        elif char == 'n':  # not
            self.block_n()
        elif char == 'w':  # while
            self.block_w()
        elif char == 'r':  # return, real
            self.block_r()
        elif char == 't':  # true
            self.block_t()
        elif char == 'b':  # bool
            self.block_b()
        elif char == '<':  # <=
            self.block_leftAssignment()
        elif char == '=':  # =>
            self.block_rightAssignment()
        elif re.match("[a-zA-Z]", char):  # identifier start with english letter
            self.block_identifiers()
        elif re.match("[;{}():,=+*@]", char):  # a special symbol
            token = Token(self.lexeme, "SS", self.lineNum)
            self.tokens.append(token)
        elif re.match("[0-9]", char):  # constants
            self.block_constants()
        else:
            token = Token(char, "INVALID", self.lineNum)
            token.lexicalError = LexicalError.UnrecognizedSymbol
            self.tokens.append(token)

        return self.tokens

    def errorHandler(self, error):
        """
        produce appropriate error messages for the token
        """
        if error == LexicalError.InvalidSyntax:
            return "Invalid Syntax"
        elif error == LexicalError.InvalidIdentifier:
            return "Identifier contains invalid symbol"
        elif error == LexicalError.InvalidConstant:
            return "Constant follow by none digit or decimal character"
        elif error == LexicalError.UnrecognizedSymbol:
            return "Invalid symbol"
        elif error == LexicalError.MultipleDecimals:
            return "constant contains more than one decimal point"

    def invalidToken(self):
        while True:  # keep scanning until a token separator is found
            char = self.sourceCode.read(1)
            self.lexeme += char
            if char == ' ':
                token = Token(self.lexeme[:-1], "INVALID", self.lineNum)
                token.lexicalError = self.lexicalError
                self.tokens.append(token)
                break
            elif re.match("[#;{}():,=+*@]", char):
                token = Token(self.lexeme[:-1], "INVALID", self.lineNum)
                token.lexicalError = self.lexicalError
                ssToken = Token(char, "SS", self.lineNum)
                self.tokens.append(token)
                self.tokens.append(ssToken)
                break

    def block_constants(self):
        """
        states for any possible combination of constants
        that is string of digits have no more than one decimal point
        """
        decimalPointUsed = False
        char = self.sourceCode.read(1)
        self.lexeme += char
        while True:  # keep scanning as long as it form a valid constant
            if re.match("[0-9]", char):  #regular expression to match any digit
                char = self.sourceCode.read(1)
                self.lexeme += char
            elif char == '.' and not decimalPointUsed:
                char = self.sourceCode.read(1)
                self.lexeme += char
                decimalPointUsed = True
            else:
                break

        if char == ' ':  # space found, return the token
            token = Token(self.lexeme[:-1], "CONST", self.lineNum)
            self.tokens.append(token)  #add token to the list
        elif re.match("[#;{}():,=+*@]", char):  # next char is a special symbol
            token = Token(self.lexeme[:-1], "CONST", self.lineNum)
            ssToken = Token(char, "SS", self.lineNum)
            self.tokens.append(token)  # add both token and special symbol to the list
            self.tokens.append(ssToken)
        elif char == '.':
            self.lexicalError = LexicalError.MultipleDecimals
            self.invalidToken()
        else:
            self.lexicalError = LexicalError.InvalidConstant
            self.invalidToken()

    def block_identifiers(self):
        """
        States for any possible combination of identifiers:
        Any nonempty string fo English letters, digits, and/or periods that
        begins with a letter and is not a a keyword
        """
        char = self.sourceCode.read(1)
        self.lexeme += char
        while re.match("[a-zA-Z0-9.]", char):  #consume next char as long it forms valid ID
            char = self.sourceCode.read(1)
            self.lexeme += char

        if char == ' ':
            token = Token(self.lexeme[:-1], "ID", self.lineNum)
            self.tokens.append(token)
        elif re.match("[#;{}():,=+*@]", char):  # next char is a special symbol
            token = Token(self.lexeme[:-1], "ID", self.lineNum)
            ssToken = Token(char, "SS", self.lineNum)
            self.tokens.append(token)
            self.tokens.append(ssToken)
        else:
            self.lexicalError = LexicalError.InvalidIdentifier
            self.invalidToken()

    def block_identifierOrError(self, char):
        """
        This helper function handles the case when scanned character does not lead to a keyword,
        it takes one parameter of previously scanned char
        """
        if char == ' ':  # space, return as identifier
            token = Token(self.lexeme[:-1], "ID", self.lineNum)  #remove last char (space) and store token
            self.tokens.append(token)
        elif re.match("[a-zA-Z0-9.]", char):  # some ongoing identifier
            self.block_identifiers()
        elif re.match("[;{}():,=+*@]", char):
            # treat special symbol as a token separator, store both token and ss
            token = Token(self.lexeme[:-1], "ID", self.lineNum)
            ssToken = Token(char, "SS", self.lineNum)
            self.tokens.append(token)
            self.tokens.append(ssToken)
        else:
            self.lexicalError = LexicalError.InvalidIdentifier
            self.invalidToken()

    def keyAcceptingState(self):
        """
        This function is called when scanned characters lead to a accepting state as a keyword
        """
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == ' ':  # token separator, token is a keyword
            token = Token(self.lexeme[:-1], "KEY", self.lineNum)
            self.tokens.append(token)
        elif re.match("[;{}():,=+*@]", char):  # keyword token follow by a SS
            token = Token(self.lexeme[:-1], "KEY", self.lineNum)
            ssToken = Token(char, "SS", self.lineNum)
            self.tokens.append(token)
            self.tokens.append(ssToken)
        elif re.match("[a-zA-Z0-9.]", char):  # some ongoing identifier
            self.block_identifiers()
        else:
            self.lexicalError = LexicalError.InvalidSyntax
            self.invalidToken()


    # each block_XXX function indicate a state that might lead to a keyword token
    def block_rightAssignment(self):  # =>
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == '>':
            token = Token(self.lexeme, "KEY", self.lineNum)
            self.tokens.append(token)
        else:
            token = Token(self.lexeme[:-1], "SS", self.lineNum)
            self.tokens.append(token)
            self.sourceCode.seek(self.sourceCode.tell() - 1)

    def block_leftAssignment(self):  # <=
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == '=':
            token = Token(self.lexeme, "KEY", self.lineNum)
            self.tokens.append(token)
        else:
            token = Token(self.lexeme[:-1], "INVALID", self.lineNum)
            token.lexicalError = LexicalError.UnrecognizedSymbol
            self.tokens.append(token)
            self.sourceCode.seek(self.sourceCode.tell() - 1)

    def block_boo(self):  # bool
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_bo(self):  # bool
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'o':
            self.block_boo()
        else:
            self.block_identifierOrError(char)

    def block_b(self):  # bool
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'o':
            self.block_bo()
        else:
            self.block_identifierOrError(char)

    def block_tru(self):  # true
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_tr(self):  # true
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'u':
            self.block_tru()
        else:
            self.block_identifierOrError(char)

    def block_t(self):  # true
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'r':
            self.block_tr()
        else:
            self.block_identifierOrError(char)

    def block_retur(self):  # return
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'n':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_retu(self):  # return
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'r':
            self.block_retur()
        else:
            self.block_identifierOrError(char)

    def block_ret(self):  # return
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'u':
            self.block_retu()
        else:
            self.block_identifierOrError(char)

    def block_rea(self):  # real
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_re(self):  # return, real
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':
            self.block_rea()
        elif char == 't':
            self.block_ret()
        else:
            self.block_identifierOrError(char)

    def block_r(self):  # return, real
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.block_re()
        else:
            self.block_identifierOrError(char)

    def block_whil(self):  # while
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_whi(self):  # while
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.block_whil()
        else:
            self.block_identifierOrError(char)

    def block_wh(self):  # while
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'i':
            self.block_whi()
        else:
            self.block_identifierOrError(char)

    def block_w(self):  # while
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'h':
            self.block_wh()
        else:
            self.block_identifierOrError(char)

    def block_no(self):  # not
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_n(self):  # not
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'o':
            self.block_no()
        else:
            self.block_identifierOrError(char)

    def block_els(self):  # else
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_el(self):  # else
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 's':
            self.block_els()
        else:
            self.block_identifierOrError(char)

    def block_e(self):  # else
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.block_el()
        else:
            self.block_identifierOrError(char)

    def block_de(self):  # def
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'f':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_d(self):  # def
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.block_de()
        else:
            self.block_identifierOrError(char)

    def block_val(self):  # val
        char = self.sourceCode.read(1)
        if char == ' ':
            token = Token(self.lexeme, "KEY", self.lineNum)
            self.tokens.append(token)
        else:
            self.lexeme += char
            self.block_identifierOrError(char)

    def block_va(self):  # val
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_v(self):  # val
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':
            self.block_va()
        else:
            self.block_identifierOrError(char)

    def block_objec(self):  # object
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_obje(self):  # object
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'c':
            self.block_objec()
        else:
            self.block_identifierOrError(char)

    def block_obj(self):  # object
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.block_obje()
        else:
            self.block_identifierOrError(char)

    def block_ob(self):  # object
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'j':
            self.block_obj()
        else:
            self.block_identifierOrError(char)

    def block_o(self):  # object, or
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'b':
            self.block_ob()
        elif char == 'r':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_cas(self):  # case
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_ca(self):  # case
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 's':
            self.block_cas()
        else:
            self.block_identifierOrError(char)

    def block_clas(self):  # class
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 's':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_cla(self):  # class
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 's':
            self.block_clas()
        else:
            self.block_identifierOrError(char)

    def block_cl(self):  # class
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':
            self.block_cla()
        else:
            self.block_identifierOrError(char)

    def block_c(self):  # class, case
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':  # class
            self.block_cl()
        elif char == 'a':  #case
            self.block_ca()
        else:
            self.block_identifierOrError(char)

    def block_seale(self):  # sealed
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'd':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_seal(self):  # sealed
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.block_seale()
        else:
            self.block_identifierOrError(char)

    def block_sea(self):  # sealed
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.block_seal()
        else:
            self.block_identifierOrError(char)

    def block_se(self):  # sealed
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':
            self.block_sea()
        else:
            self.block_identifierOrError(char)

    def block_s(self):  # sealed
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.block_se()
        else:
            self.block_identifierOrError(char)

    def block_fals(self):  # false
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_fal(self):  # false
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 's':
            self.block_fals()
        else:
            self.block_identifierOrError(char)

    def block_fa(self):  # false
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.block_fal()
        else:
            self.block_identifierOrError(char)

    def block_final(self):  # final
        char = self.sourceCode.read(1)
        if char == ' ':
            token = Token(self.lexeme, "KEY", self.lineNum)
            self.tokens.append(token)
        else:
            self.lexeme += char
            self.block_identifierOrError(char)

    def block_fina(self):  # final
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'l':
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_fin(self):  # final
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':
            self.block_fina()
        else:
            self.block_identifierOrError(char)

    def block_fi(self):  # final
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'n':
            self.block_fin()
        else:
            self.block_identifierOrError(char)

    def block_f(self):  # final, false
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'i':
            self.block_fi()
        elif char == 'a':
            self.block_fa()
        else:
            self.block_identifierOrError(char)

    def block_abstract(self):  # abstract
        char = self.sourceCode.read(1)
        if char == ' ':
            token = Token(self.lexeme, "KEY", self.lineNum)
            self.tokens.append(token)
        else:
            self.lexeme += char
            self.block_identifierOrError(char)

    def block_abstrac(self):  # abstract
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':  # abstract
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_abstra(self):  # abstract
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'c':  # abstract
            self.block_abstrac()
        else:
            self.block_identifierOrError(char)

    def block_abstr(self):  # abstract
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':  # abstract
            self.block_abstra()
        else:
            self.block_identifierOrError(char)

    def block_abst(self):  # abstract
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'r':  # abstract
            self.block_abstr()
        else:
            self.block_identifierOrError(char)

    def block_abs(self):  # abstract
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':  # abstract
            self.block_abst()
        else:
            self.block_identifierOrError(char)

    def block_ab(self):  # abstract
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 's':  # abstract
            self.block_abs()
        else:
            self.block_identifierOrError(char)

    def block_and(self):
        char = self.sourceCode.read(1)
        if char == ' ':  # and
            token = Token(self.lexeme, "KEY", self.lineNum)
            self.tokens.append(token)
        else:
            self.lexeme += char
            self.block_identifierOrError(char)

    def block_an(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'd':  # abstract
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_a(self):  # abstract, and
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'b':  # abstract
            self.block_ab()
        elif char == 'n':
            self.block_an()
        else:
            self.block_identifierOrError(char)

    def block_in(self):  # in, int
        char = self.sourceCode.read(1)
        self.lexeme += char

        if char == ' ':  # in
            token = Token(self.lexeme[:-1], "KEY", self.lineNum)
            self.tokens.append(token)
        elif char == 't':  # int
            self.keyAcceptingState()
        elif re.match("[#;{}():,=+*@]", char):  # next char is a special symbol
            self.token = Token(self.lexeme[:-1], "KEY", self.lineNum)
            self.specialSymbol = char
        else:
            self.block_identifierOrError(char)

    def block_if(self):
        char = self.sourceCode.read(1)
        if char == ' ':  # if
            token = Token(self.lexeme, "KEY", self.lineNum)
            self.tokens.append(token)
        else:
            self.lexeme += char
            self.block_identifierOrError(char)

    def block_impor(self):  # import
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':  # import
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_impo(self):  # import
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'r':  # import
            self.block_impor()
        else:
            self.block_identifierOrError(char)

    def block_imp(self):  # import
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'o':  # import
            self.block_impo()
        else:
            self.block_identifierOrError(char)

    def block_im(self):  # import
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'p':  # import
            self.block_imp()
        else:
            self.block_identifierOrError(char)

    def block_i(self):  # import, if, in, int
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'm':  # import
            self.block_im()
        elif char == 'f':  # if
            self.keyAcceptingState()
        elif char == 'n':  # in, int
            self.block_in()
        else:
            self.block_identifierOrError(char)

    def block_packag(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':  # package
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_packa(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'g':  # package
            self.block_packag()
        else:
            self.block_identifierOrError(char)

    def block_pack(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':  # package
            self.block_packa()
        else:
            self.block_identifierOrError(char)

    def block_pac(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'k':  # package
            self.block_pack()
        else:
            self.block_identifierOrError(char)

    def block_pa(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'c':  # package
            self.block_pac()
        else:
            self.block_identifierOrError(char)

    def block_protecte(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'd':  # protected
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_protect(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':  # protected
            self.block_protecte()
        else:
            self.block_identifierOrError(char)

    def block_protec(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':  # protected
            self.block_protect()
        else:
            self.block_identifierOrError(char)

    def block_prote(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'c':  # protected
            self.block_protec()
        else:
            self.block_identifierOrError(char)

    def block_prot(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':  # protected
            self.block_prote()
        else:
            self.block_identifierOrError(char)

    def block_pro(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':  # protected
            self.block_prot()
        else:
            self.block_identifierOrError(char)

    def block_privat(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'e':  # private
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_priva(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':  # private
            self.block_privat()
        else:
            self.block_identifierOrError(char)

    def block_priv(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':  # private
            self.block_priva()
        else:
            self.block_identifierOrError(char)

    def block_prin(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 't':  # print
            self.keyAcceptingState()
        else:
            self.block_identifierOrError(char)

    def block_pri(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'v':  # private
            self.block_priv()
        elif char == 'n':  # print
            self.block_prin()
        else:
            self.block_identifierOrError(char)

    def block_pr(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'i':  # private, print
            self.block_pri()
        elif char == 'o':  # protected
            self.block_pro()
        else:
            self.block_identifierOrError(char)

    def block_p(self):
        char = self.sourceCode.read(1)
        self.lexeme += char
        if char == 'a':  # package
            self.block_pa()
        elif char == 'r':  # private, protected, print,
            self.block_pr()
        else:
            self.block_identifierOrError(char)
