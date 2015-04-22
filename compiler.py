"""
CS 4323 Programming Assignment #2
Compiler Parser

Author: Lingzhou Lu
"""
from parser import Parser

sourceFile = "source.txt"
def main():
    # call parser
    parser = Parser()

    # start LL(1) parsing
    parser.parsing(sourceFile)

    # print out symbol table
    parser.symtab.printTable()


if __name__ == '__main__':
    main()
