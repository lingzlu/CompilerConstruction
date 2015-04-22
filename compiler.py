"""
CS 4323 Programming Assignment #1
This project builds the first component of a compiler, the lexical analyzer,
for so-called Simple-Scala language

Author: Lingzhou Lu
"""

import re
import sys
import collections
from scanner import Scanner
from bookkeeper import Bookkeeper
from parser import Parser

sourceFile = "source.txt"
outputFile = "tokenOutput.txt"

def main():
    # symtab = Bookkeeper()
    # step = 1
    # scanner = Scanner(sourceFile)  # pass source file to the scanner
    # output = open(outputFile, "w")  # open the output file
    # output.write("Steps\tTokens\tTypes\tLine #\n")  # write header line
    # while True:
    #     token = scanner.nextToken()
    #     if not token :  # this only true when end of file reached
    #         break
    #    # for token in tokens:  # might have 2 tokens when a special symbol follows
    #     if not token.lexicalError:
    #         output.write ("%d\t%s\t%s\t%d\n"% (step, token.lexeme, token.type, token.lineNum))
    #     else:
    #         errorMessage = scanner.errorHandler(token.lexicalError)
    #         output.write ("%d\t%s\t%s\t%d\n"% (step, token.lexeme, errorMessage, token.lineNum))

    #     if token.type == "ID" or token.type == "CONST":
    #         symtab.insert(token)

    #     step += 1
    # symtab.printTable()

    parser = Parser()
    parser.parsing()



if __name__ == '__main__':
    main()
