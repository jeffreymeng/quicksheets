import string


class Token(object):
    types = ["number", "operator", "function", "control", "range", "string"]
    def __init__(self, type, symbol, startPosition, endPosition):
        if type not in Token.types:
            raise Exception("Unknown Token " + type)
        self.type = type
        self.startPosition = startPosition
        self.endPosition = endPosition
        self.symbol = symbol

    def __eq__(self, other):
        return isinstance(other, Token) and self.type == other.type \
               and self.pos == other.pos and self.symbol == other.symbol

    def __repr__(self):
        symbol = self.symbol
        if self.type == "range":
            symbol = f'{symbol[0]}{symbol[1]}:{symbol[2]}{symbol[3]}'
        return f'Token<{self.type}>({repr(symbol)})'


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

# returns the longest prefix of str containing only characters in the string whitelistedCharacters
def whitelistedPrefix(str, whitelistedCharacters):
    return prefixWhile(str, lambda c: c in whitelistedCharacters)

# returns the longest prefix of the string containing only characters passing
# a predicate function
def prefixWhile(str, predicate):
    buffer = ""
    for c in str:
        if predicate(c):
            buffer += c
        else:
            break
    return buffer

# a basic lexer
# Some resources I looked at:
# https://stackoverflow.com/questions/37346934/designing-a-language-lexer
# https://medium.com/young-coder/how-i-wrote-a-lexer-39f4f79d2980
#
def lex(str):

    pos = 0
    while pos < len(str):
        c = str[pos]

        if c in "()":
            yield Token("control", c, pos, pos + 1)
            pos += 1
            continue

        # Operators
        if c in "+-*/%^":
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
                if str[nextStartPos] != ":":
                    yield Token("range", (col1, row1, col1, row1), pos, endPosition)
                    pos = nextStartPos + 1
                    continue
                else:
                    nextStartPos += 1
                    col2 = whitelistedPrefix(str[nextStartPos:], string.ascii_uppercase)
                    nextStartPos = nextStartPos + len(col2)
                    row2 = whitelistedPrefix(str[nextStartPos:], string.digits)
                    nextStartPos = nextStartPos + len(row2)
                    if col2 == row2 == "":
                        raise Exception("Expected reference after ':'")
                    if col2 == "":
                        col2 = col1
                    if row2 == "":
                        row2 = row1
                    yield Token("range", (col1, row1, col2, row2), pos, nextStartPos)
                    pos = nextStartPos + 1
                    continue
        # strings
        if c in "\'\"":
            quoteType = c
            if quoteType not in str[pos + 1:]:
                raise Exception("Expected string to be closed")
            buffer = prefixWhile(str[pos + 1:], lambda ch: ch != quoteType)

            firstCharInString = pos + 1
            lastCharInString = firstCharInString - 1 + len(buffer)
            # add 1 for the ending quote
            endPosition = lastCharInString + 1
            yield Token("string", buffer, pos, endPosition)

            pos = endPosition + 1
            continue

        if c in string.digits:
            buffer = whitelistedPrefix(str[pos:], string.digits)
            endPosition = pos - 1 + len(buffer)
            yield Token("number", int(buffer), pos, endPosition)

            # set the position to the character after the number
            pos = endPosition + 1
            continue

        if c in "_" + string.ascii_letters:
            buffer = whitelistedPrefix(str[pos:], "_" + string.ascii_letters)
            endPosition = pos - 1 + len(buffer)
            yield Token("function", buffer, pos, endPosition)

            # set the position to the character after the number
            pos = endPosition + 1
            continue

        if c in string.whitespace:
            pos += 1
            continue
        raise Exception("Unexpected character: " + repr(c))
    pass


# pad a str to toLength with withCharacter
def pad(str, toLength, withCharacter, direction = "right"):
    if direction == "right":
        return str + withCharacter * (toLength - len(str))
    else:
        return withCharacter * (toLength - len(str)) + str


def testLexer():
    for token in lex("128 + SUM(A1:B2) - 2 * 7 / VALUE('72')"):
        print(f'{pad(token.type, 10, " ")} {pad(str(token.startPosition), 2, "0", "left")}' +
              f':{pad(str(token.endPosition), 2, "0", "left")} {repr(token.symbol)}')

if (__name__ == '__main__'):
    testLexer()