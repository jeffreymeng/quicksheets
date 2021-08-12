import string
from spreadsheet.range import Range, Reference

tokenColors = {
    "number": "blue",
    "operator": "red3",
    "function": "purple",
    "control": "black",
    "range": "orange",
    "string": "goldenrod3",
    "reference": "orange"
}

class Token(object):
    types = ["number", "operator", "function", "control", "range", "string", "reference"]
    def __init__(self, type, symbol, startPosition, endPosition):
        if type not in Token.types:
            raise LexerError("Unknown Token type: " + type, startPosition)
        self.type = type
        self.startPosition = startPosition
        self.endPosition = endPosition
        self.symbol = symbol

    # check if the token matches the given symbol and type
    def matches(self, type, symbol):
        return self.type == type and self.symbol == symbol

    def __eq__(self, other):

        return isinstance(other, Token) and \
               self.type == other.type and \
               self.symbol == other.symbol and \
               self.startPosition == other.startPosition and \
               self.endPosition == other.endPosition


    def __repr__(self):
        return f'Token<{self.type}>({repr(self.symbol)})'


# expected lexer output (not including position)
# "128 + SUM(A1:B2) - 2 * 7 / VALUE('7')" =>
# Token("number", 128)
# Token("operator", "+")
# Token("function", "SUM")
# Token("control", "(")
# Token("range", ("A", 1, "B", 2))
# Token("operator", "-")
# Token("number", 2)
# Token("operator", "*")
# Token("number", 7)
# Token("operator", "/")
# Token("function", "VALUE"),
# Token("control", "("),
# Token("string", "7"),
# Token("control", ")")

# returns the longest prefix of string s containing only characters in the string whitelistedCharacters
def whitelistedPrefix(s, whitelistedCharacters):
    return prefixWhile(s, lambda c: c in whitelistedCharacters)


# returns the longest prefix of the string s containing only characters passing
# a predicate function
def prefixWhile(s, predicate):
    buffer = ""
    for c in s:
        if predicate(c):
            buffer += c
        else:
            break
    return buffer

class LexerError(Exception):
    def __init__(self, msg, position):
        super().__init__(msg)
        self.position = position

    def __repr__(self):
        return "SyntaxError: " + str(super())

# a basic lexer
# Some resources I looked at:
# https://stackoverflow.com/questions/37346934/designing-a-language-lexer
# https://medium.com/young-coder/how-i-wrote-a-lexer-39f4f79d2980
# https://ruslanspivak.com/lsbasi-part1/
def lex(str):

    pos = 0
    while pos < len(str):
        c = str[pos]

        if c in "(),":
            yield Token("control", c, pos, pos + 1)
            pos += 1
            continue

        if c in "." + string.digits:

            buffer = whitelistedPrefix(str[pos:], string.digits + '.')
            endPosition = pos - 1 + len(buffer)
            if buffer.count(".") > 1:
                raise LexerError("Expected zero or one decimal point in the number.", pos)
            elif len(buffer) > 0 and buffer[-1] == ".":
                buffer += "0"
            yield Token("number", float(buffer), pos, endPosition + 1)

            # set the position to the character after the number
            pos = endPosition + 1
            continue

        # Operators
        if c in "+-*/^":
            yield Token("operator", c, pos, pos + 1)
            pos += 1
            continue

        # Ranges (A1 is treated as A1:A1). Other ranges include: A3, A194, AD1:B3
        if c in string.ascii_uppercase:
            col1 = whitelistedPrefix(str[pos:], string.ascii_uppercase)
            nextStartPos = pos + len(col1)
            row1 = whitelistedPrefix(str[nextStartPos:], string.digits)
            nextStartPos = nextStartPos + len(row1)
            # if row1 is not empty, then this is a valid range

            if row1 != "":
                if nextStartPos >= len(str) or str[nextStartPos] != ":":
                    yield Token("reference", Reference(col1, int(row1)), pos, nextStartPos)
                    pos = nextStartPos
                    continue
                else:
                    nextStartPos += 1
                    col2 = whitelistedPrefix(str[nextStartPos:], string.ascii_uppercase)
                    nextStartPos = nextStartPos + len(col2)
                    row2 = whitelistedPrefix(str[nextStartPos:], string.digits)
                    nextStartPos = nextStartPos + len(row2)
                    if col2 == row2 == "":
                        raise LexerError("Expected reference after ':'", nextStartPos)
                    if col2 == "":
                        col2 = -1
                    if row2 == "":
                        row2 = -1
                    yield Token("range", Range(Reference(col1, int(row1)), Reference(col2, int(row2))), pos, nextStartPos)
                    pos = nextStartPos
                    continue
        # strings
        if c in "\'\"":
            quoteType = c
            if quoteType not in str[pos + 1:]:
                raise LexerError("Expected string to be closed", pos)
            buffer = prefixWhile(str[pos + 1:], lambda ch: ch != quoteType)

            firstCharInString = pos + 1
            lastCharInString = firstCharInString - 1 + len(buffer)
            # add 1 for the ending quote
            endPosition = lastCharInString + 1
            yield Token("string", buffer, pos, endPosition + 1)

            pos = endPosition + 1
            continue


        if c in "_" + string.ascii_letters:
            buffer = whitelistedPrefix(str[pos:], "_" + string.ascii_letters)
            endPosition = pos - 1 + len(buffer)
            yield Token("function", buffer, pos, endPosition + 1)

            # set the position to the character after the number
            pos = endPosition + 1
            continue

        if c in string.whitespace:
            pos += 1
            continue
        raise LexerError("Unexpected character: " + repr(c), pos)
    pass


# pad a str to toLength with withCharacter
def pad(str, toLength, withCharacter, direction = "right"):
    if direction == "right":
        return str + withCharacter * (toLength - len(str))
    else:
        return withCharacter * (toLength - len(str)) + str

# Prints the result of lex(someString) in a formatted way
def printLexResult(tokens):
    for token in tokens:
        print(f'{pad(token.type, 10, " ")} {pad(str(token.startPosition), 2, "0", "left")}' +
              f':{pad(str(token.endPosition), 2, "0", "left")} {repr(token.symbol)}')

# tests the lexer
def testLexer():
    def test(res, expected):
        for i in range(len(res)):
            expType, expSymbol = expected[i]
            if res[i].type != expType or res[i].symbol != expSymbol:
                raise Exception(f'{i}: Expected Token<{expType}>({repr(expSymbol)}) but ' +
                                f'got {repr(res[i])}')
        if len(res) != len(expected):
            raise Exception(f'Expected number of tokens to be {len(expected)}, but got {len(res)} tokens')
    print("Testing lex()...", end="")
    test1Res = list(lex("1 + 1 + -5"))
    test1Expected = [("number", 1), ("operator", "+"), ("number", 1),
                     ("operator", "+"), ("operator", "-"), ("number", 5)]
    test(test1Res, test1Expected)
    test2Res = list(lex("9385 + (COUNT(A2, ZZ1:AB5324) ^ 2) + DAY('monday')"))
    test2ResNoWhitespace = list(lex("9385+(COUNT(A2,ZZ1:AB5324)^2)+DAY('monday')"))
    test2ResWeirdWhitespace = list(lex("9385   +(COUNT\t(A2 ,ZZ1:AB5324\t\t\t\t)^2)+ DAY('monday')"))
    test2Expected = [
        ("number", 9385),
        ("operator", "+"),
        ("control", "("),
        ("function", "COUNT"),
        ("control", "("),
        ("reference", Reference("A2")),
        ("control", ","),
        ("range", Range(Reference("ZZ1"), Reference("AB5324"))),
        ("control", ")"),
        ("operator", "^"),
        ("number", 2),
        ("control", ")"),
        ("operator", "+"),
        ("function", "DAY"),
        ("control", "("),
        ("string", "monday"),
        ("control", ")")
    ]
    test(test2Res, test2Expected)
    test(test2ResNoWhitespace, test2Expected)
    test(test2ResWeirdWhitespace, test2Expected)
    test3Res = list(lex("128 + SUM(A1:B2) - 2 * 7 / VALUE('72')"))
    test3ResNoWhitespace = list(lex("128+SUM(A1:B2)-2*7/VALUE('72')"))
    test3Expected = [("number", 128.0),
                     ("operator", "+"),
                     ("function", "SUM"),
                     ("control", "("),
                     ("range", Range(Reference("A1"), Reference("B2"))),
                     ("control", ")"),
                     ("operator", "-"),
                     ("number", 2.0),
                     ("operator", "*"),
                     ("number", 7.0),
                     ("operator", "/"),
                     ("function", "VALUE"),
                     ("control", "("),
                     ("string", "72"),
                     ("control", ")")]
    test(test3Res, test3Expected)
    test(test3ResNoWhitespace, test3Expected)
    print("Passed!")

def getReferences(lexer):
    res = []
    for token in lexer:
        if token.type == "range" or token.type == "reference":
            res.append(token)
    return res

if (__name__ == '__main__'):
    testLexer()
