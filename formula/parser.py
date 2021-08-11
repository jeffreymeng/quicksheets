from lexer import lex, LexerError
from formulas import runFunction, FormulaNameError

class ASTNode(object):
    def __init__(self, token):
        self.token = token

    def eval(self):
        raise Exception("Eval was not overwritten by a subclass")

    def __repr__(self):
        print(f'<Node: {repr(self.token)}>')

class NumberNode(ASTNode):
    def __init__(self, token):
        assert(token.type == "number")
        super().__init__(token)

    def eval(self):
        return self.token.symbol

class StringNode(ASTNode):
    def __init__(self, token):
        assert(token.type == "string")
        super().__init__(token)

    def eval(self):
        return self.token.symbol

class UnaryPlusNode(ASTNode):
    def __init__(self, left, token):
        self.left = left
        super().__init__(token)
    def eval(self):
        return self.left.eval()

class UnaryMinusNode(ASTNode):
    def __init__(self, left, token):
        self.left = left
        super().__init__(token)
    def eval(self):
        return -1 * self.left.eval()

class BinaryOpNode(ASTNode):
    def __init__(self, left, token, right):
        self.left = left
        self.right = right
        super().__init__(token)

class ExponentNode(BinaryOpNode):
    def eval(self):
        return self.left.eval() ** self.right.eval()

class AddNode(BinaryOpNode):
    def eval(self):
        return self.left.eval() + self.right.eval()

class SubtractNode(BinaryOpNode):
    def eval(self):
        return self.left.eval() - self.right.eval()

class MultiplyNode(BinaryOpNode):
    def eval(self):
        return self.left.eval() * self.right.eval()

class DivideNode(BinaryOpNode):
    def eval(self):
        return self.left.eval() / self.right.eval()

class RangeNode(ASTNode):
    def __init__(self, token, spreadsheet):
        super().__init__(token)
        self.spreadsheet = spreadsheet

    def eval(self):
        return self.spreadsheet.get(self.token.symbol)

class FunctionCallNode(ASTNode):
    def __init__(self, token, arguments):
        assert(token.type == "function")
        super().__init__(token)
        self.arguments = arguments

    def eval(self):
        evaluatedArguments = []
        for arg in self.arguments:
            evaluatedArguments.append(arg.eval())
        return runFunction(self.token, evaluatedArguments)


class ParserSyntaxError(Exception):
    def __init__(self, msg, token = None):
        super().__init__(self, msg)
        self.msg = msg
        self.token = token

    def __repr__(self):
        return "Error: " + self.msg

class SpreadsheetReferenceError(ParserSyntaxError):
    def __init__(self, msg, token = None):
        super().__init__(self, msg)
        self.msg = msg
        self.token = token

    def __repr__(self):
        return "ReferenceError: " + self.msg

# https://ruslanspivak.com/lsbasi-part7/
# https://ruslanspivak.com/lsbasi-part8/
class Parser(object):
    def __init__(self, lexer, spreadsheet):
        self.peekedNext = None
        self.lexer = lexer
        self.spreadsheet = spreadsheet

    # Get the next token without moving on to the next token. If there are
    # no more tokens, returns EndOfInputToken()
    def peek(self):
        try:
            if self.peekedNext == None:
                self.peekedNext = next(self.lexer)
            return self.peekedNext
        except StopIteration:
            raise ParserSyntaxError(f'Reached end of formula unexpectedly')

    def hasNextToken(self):
        try:
            self.peek()
            return True
        except ParserSyntaxError:
            return False

    # Get the next token & move on to the next token.
    # Accepts an optional parameter assertType, which
    # throws a syntax error if the type of the next token does not match
    # the given type
    def next(self, expectedType = None, expectedSymbol = None):
        try:
            if self.peekedNext:
                nextToken = self.peekedNext
                self.peekedNext = None
            else:
                nextToken = next(self.lexer)
            if (expectedSymbol != None and nextToken.symbol != expectedSymbol):
                raise ParserSyntaxError(f'Expected {repr(expectedSymbol)} '
                        + f'but got {repr(nextToken.symbol)} at position '
                        + f'{nextToken.startPosition}:{nextToken.endPosition}', nextToken)
            if (expectedType != None and nextToken.type != expectedType):
                raise ParserSyntaxError(f'Expected token {repr(expectedType)} '
                                        + f'but got token {repr(nextToken.type)} at position '
                                        + f'{nextToken.startPosition}:{nextToken.endPosition}', nextToken)
            return nextToken
        except StopIteration as e:
            raise ParserSyntaxError(f'Reached end of formula unexpectedly')

    # If the next token matches expectedType and (optional) expectedSymbol,
    #  get the token, move on to the next token, and return True.
    # Otherwise, do nothing and return False
    def tryNext(self, expectedType, expectedSymbol = None):
        if self.hasNextToken() and self.peek().matches(expectedType, expectedSymbol):
            self.next()
            return True
        else:
            return False

    """
    BNF (except for number, function, range, and string)
    <number>          ::= a number from the lexer
    <function>        ::= a function from the lexer
    <string>          ::= a string from the lexer
    <range>           ::= a range from the lexer
    
    <expression>      ::= <term> | <term> "+" <expression> | <term> "-" <expression>
    <term>            ::= <factor> | <factor> "*" <term> | <factor> "/" <term>
    <factor>          ::= <base> | <base> "^" <exponent>
    <base>            ::= "(" <expression> ")" | <number> | <function> | <range> | <string> | "+" <base> | "-" <base>
    <exponent>        ::= <base>
    """


    # <expression> ::= <term> | <term> "+" <expression> | <term> "-" <expression>
    def getExpression(self):
        leftNode = self.getTerm()

        if self.hasNextToken() and \
            (self.peek().matches("operator", "+") or self.peek().matches("operator", "-")):
            operator = self.next("operator")
            rightNode = self.getExpression()
            if operator.symbol == "+":
                return AddNode(leftNode, operator, rightNode)
            else:
                return SubtractNode(leftNode, operator, rightNode)
        return leftNode

    # <term> ::= <factor> | <factor> "*" <term> | <factor> "/" <term>
    def getTerm(self):
        leftNode = self.getFactor()
        if self.hasNextToken() and \
            (self.peek().matches("operator", "*") or self.peek().matches("operator", "/")):
            operator = self.next("operator")
            rightNode = self.getTerm()
            if operator.symbol == "*":
                return MultiplyNode(leftNode, operator, rightNode)
            else:
                return DivideNode(leftNode, operator, rightNode)
        return leftNode

    # <factor> ::= <base> | <base> "^" <exponent>
    def getFactor(self):
        leftNode = self.getBase()
        if self.hasNextToken() and self.peek().matches("operator", "^"):
            operator = self.next("operator", "^")
            rightNode = self.getExponent()
            return ExponentNode(leftNode, operator, rightNode)
        return leftNode

    # <base> ::= "(" <expression> ")" | <number> | <function> | <range> | "+" <base> | "-" <base>
    def getBase(self):
        if self.hasNextToken() and self.peek().matches("operator", "+"):
            operatorToken = self.next("operator", "+")
            return UnaryPlusNode(self.getBase(), operatorToken)
        elif self.hasNextToken() and self.peek().matches("operator", "-"):
            operatorToken = self.next("operator", "-")
            return UnaryMinusNode(self.getBase(), operatorToken)
        elif self.hasNextToken() and self.peek().type == "function":
            functionToken = self.next("function")
            self.next("control", "(")
            arguments = []
            if not self.peek().matches("control", ")"):
                arguments.append(self.getExpression())
                while not self.peek().matches("control", ")"):
                    self.next("control", ",")
                    arguments.append(self.getExpression())
            self.next("control", ")")
            return FunctionCallNode(functionToken, arguments)
        elif self.tryNext("control", "("):
            expressionNode = self.getExpression()
            self.next("control", ")")
            return expressionNode
        elif self.peek().type == "string":
            return StringNode(self.next("string"))
        elif self.peek().type == "number":
            return NumberNode(self.next("number"))
        elif self.peek().type == "range":
            if self.spreadsheet == None:
                raise SpreadsheetReferenceError("ReferenceError: ranges are not accessible in the REPL", self.next("range"))
            return RangeNode(self.next("range"), self.spreadsheet)
        else:
            invalidToken = self.next()
            raise ParserSyntaxError(f'Unexpected token {repr(invalidToken.symbol)} ' +
                                    f'{invalidToken.startPosition}:{invalidToken.endPosition}',
                                    invalidToken)

    # <exponent> ::= <base>
    def getExponent(self):
        return self.getBase()

def repl():
    expr = ""
    print("Formula REPL: type exit to exit")
    prompt = " > "
    while expr != "exit":
        expr = input(prompt).strip()
        if expr == "":
            continue
        try:
            evalResult = Parser(lex(expr), None).getExpression().eval()
            print(" " * len(prompt) + repr(evalResult))
        except (ParserSyntaxError, SpreadsheetReferenceError, LexerError, FormulaNameError) as e:
            if isinstance(e, LexerError):
                print(" " * len(prompt) + " " * e.position + "^")
                print(e)
            else:
                if e.token != None:
                    print(" " * len(prompt) + " " * e.token.startPosition +
                          "^" * (e.token.endPosition - e.token.startPosition + 1))
                print(repr(e))

if (__name__ == '__main__'):
    repl()



