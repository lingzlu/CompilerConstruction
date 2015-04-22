from scanner import Scanner
from bookkeeper import Bookkeeper
import sys

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.insert(0, item)

    def pop(self):
        return self.items.pop(0)

    def peek(self):
        return self.items[0]

    def size(self):
        return len(self.items)

    def print_stack(self):
        print (self.items)


class Parser(object):

    token_lookup = ["Z0","[id]","[const]","package", "import","abstract","final","sealed","private",
                            "protected","class","object","val","def","<=","if","else","while","case","=>","in",
                            "print","return","not","true","false","and","or","int","real","bool",
                            ";","{","}","(", ")",":",",","=","+","*","@",
                            "<scala>","<packages>","<imports>","<scala-body>","<subbody>","<modifier>",
                            "<subbody-tail>","<tail-type>","<block>","<stmts>","<stmt>","<dcl>","<dcl-tail>",
                            "<ids>","<more-ids>","<type>","<asmt>","<if>","<while>","<case>","<in>","<out>",
                            "<return>","<expr>","<arith-expr>","<arith>","<bool-expr>","<bool>","$"]


    syntax_rules = {1:[43,44,45],
                            2:[3,1,31,43],
                            3:[-1],
                            4:[4,1,31,44],
                            5:[-1],
                            6:[46,45],
                            7:[-1],
                            8:[47,48],
                            9:[5],
                            10:[6],
                            11:[7],
                            12:[8],
                            13:[9],
                            14:[49,50],
                            15:[10],
                            16:[11],
                            17:[32,51,33],
                            18:[52,31,51],
                            19:[-1],
                            20:[53],
                            21:[58],
                            22:[59],
                            23:[60],
                            24:[61],
                            25:[62],
                            26:[63],
                            27:[64],
                            28:[50],
                            29:[12,54],
                            30:[13,1,34,55,35,50],
                            31:[55,36,57],
                            32:[1,56],
                            33:[37,1,56],
                            34:[-1],
                            35:[28],
                            36:[29],
                            37:[30],
                            38:[1,14,65],
                            39:[15,34,65,35,52,31,16,52],
                            40:[17,34,65,35,52],
                            41:[18,1,38,65,19,52],
                            42:[20,34,55,35],
                            43:[21,34,55,35],
                            44:[22,34,65,35],
                            45:[66],
                            46:[68],
                            47:[1,67],
                            48:[2,67],
                            49:[34,66,35,67],
                            50:[39,66],
                            51:[40,66],
                            52:[-1],
                            53:[23,34,68,35,69],
                            54:[24,69],
                            55:[25,69],
                            56:[41,66,66],
                            57:[26,68],
                            58:[27,68],
                            59:[-1],
                            }

    parse_table ={
        42: {
            3:1,
            4:1,
            5:1,
            6:1,
            7:1,
            8:1,
            9:1
        },
        43: {
            3:2,
            4:3,
            5:3,
            6:3,
            7:3,
            8:3,
            9:3
        },
        44: {
            4:4,
            5:5,
            6:5,
            7:5,
            8:5,
            9:5
        },
        45: {
            5:6,
            6:6,
            7:6,
            8:6,
            9:6,
            70:7
        },
        46: {
            5:8,
            6:8,
            7:8,
            8:8,
            9:8
        },
        47: {
            5:9,
            6:10,
            7:11,
            8:12,
            9:13
        },
        48: {
            10:14,
            11:14
        },
        49: {
            10:15,
            11:16
        },
        50: {
            32:17
        },
        51: {
            12:18,
            13:18,
            1:18,
            15:18,
            17:18,
            18:18,
            20:18,
            21:18,
            22:18,
            32:18,
            33:19
        },
        52: {
            12:20,
            13:20,
            1:21,
            15:22,
            17:23,
            18:24,
            20:25,
            21:26,
            22:27,
            32:28
        },
        53: {
            12:29,
            13:30
        },
        54: {
            1:31
        },
        55: {
            1:32
        },
        56: {
            37:33,
            36:34,
            35:34
        },
        57: {
            28:35,
            29:36,
            30:37
        },
        58: {
            1:38
        },
        59: {
            15:39
        },
        60:{
            17:40
        },
        61:{
            18:41
        },
        62:{
            20:42
        },
        63:{
            21:43
        },
        64:{
            22:44
        },
        65:{
            1:45,
            2:45,
            34:45,
            23:46,
            24:46,
            25:46,
            41:46
        },
        66:{
            1:47,
            2:48,
            34:49
        },
        67:{
            39:50,
            40:51,
            31:52,
            35:52,
            19:52,
            1:52,
            2:52
        },
        68:{
            23:53,
            24:54,
            25:55,
            41:56,
        },
        69:{
            26:57,
            27:58,
            31:59,
            35:59,
            19:59
        }
    }

    def __init__(self):
        self.stack = Stack()

    def executeRule(self,ruleNum):
        self.stack.pop()
        try:
            ruleItems = Parser.syntax_rules[ruleNum]
        except:
            print ("Rule not found: ", ruleNum)
            return 0

        for item in reversed(ruleItems):
            if item != -1:
                self.stack.push(item)

    def findRule(self, stackTop, lookahead):
        try:
            rule = Parser.parse_table[stackTop][lookahead]
        except:
            print ("Parse Table lookup failed: ", stackTop, " ", lookahead)
            return 0
        return rule

    def get_token(self, token):
        try:
            tokenValue = Parser.token_lookup.index(token)
        except:
            print ("in token: ", token)
            return -1

        return tokenValue

    def parsing(self):


        step = 1
        scanner = Scanner("source.txt")  # pass source file to the scanner
        output = open("parse_output", "w")  # open the output file
        output.write("Steps\tStack Top\tLookahead\tAction\n")  # write header line


        self.stack.push(0)
        stackTop = self.stack.peek()
        output.write ("%d\t%s %s\t%s %s\t%s\n"% (step, Parser.token_lookup[stackTop], stackTop,
           "-", "-", "push <scala>"))
        self.stack.push(42)

        token = scanner.nextToken()
        lookahead = self.get_token(token.lexeme)

        while True:
            stackTop = self.stack.peek()
            if (stackTop in range(1,42) and stackTop == lookahead):
                output.write ("%d\t%s %d\t%s %d\t%s\n"% (step, Parser.token_lookup[stackTop], stackTop,
                   Parser.token_lookup[lookahead], lookahead, "match"))

                self.stack.pop()
                token = scanner.nextToken()

                if token.type == "ID":
                    token = "[id]"

                elif token.type == "CONST":
                    token = "[const]"
                else:
                    token = token.lexeme

                lookahead = self.get_token(token)

                if token == "$":  # end of file marker
                    stackTop = self.stack.peek()
                    ruleNum = self.findRule(stackTop, lookahead)
                    self.executeRule(ruleNum)
                    output.write ("%d\t%s %s\t%s %s\tRule %s\n"% (step, Parser.token_lookup[stackTop], stackTop,
                       Parser.token_lookup[lookahead], lookahead, ruleNum))
                    return True

            else:
                ruleNum = self.findRule(stackTop, lookahead)

                self.executeRule(ruleNum)
                output.write ("%d\t%s %s\t%s %s\tRule %s\n"% (step, Parser.token_lookup[stackTop], stackTop,
                   Parser.token_lookup[lookahead], lookahead, ruleNum))

            step += 1



        # while True:
        #     tokens = scanner.nextToken()
        #     if not tokens:  # this only true when end of file reached
        #         break
        #     for token in tokens:  # might have 2 tokens when a special symbol follows
        #         if not token.lexicalError:
        #             output.write ("%d\t%s\t%s\t%d\n"% (step, token.lexeme, token.type, token.lineNum))
        #         else:
        #             errorMessage = scanner.errorHandler(token.lexicalError)
        #             output.write ("%d\t%s\t%s\t%d\n"% (step, token.lexeme, errorMessage, token.lineNum))

        #         if token.type == "ID" or token.type == "CONST":
        #             symtab.insert(token)

        #         step += 1
        # symtab.printTable()
