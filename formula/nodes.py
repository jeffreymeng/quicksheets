from formula.formulae import runFunction

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
        left = self.left.eval()
        right = self.right.eval()
        if not isinstance(left, str) and isinstance(right, str) and right.strip() == "":
            return left
        elif not isinstance(right, str) and isinstance(left, str) and left.strip() == "":
            return right
        return left + right

class SubtractNode(BinaryOpNode):
    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        if not isinstance(left, str) and isinstance(right, str) and right.strip() == "":
            return left
        elif not isinstance(right, str) and isinstance(left, str) and left.strip() == "":
            return right
        return left - right

class MultiplyNode(BinaryOpNode):
    def eval(self):
        return self.left.eval() * self.right.eval()

class DivideNode(BinaryOpNode):
    def eval(self):
        return self.left.eval() / self.right.eval()

class RefNode(ASTNode):
    def __init__(self, token, spreadsheet):
        super().__init__(token)
        self.spreadsheet = spreadsheet

    def eval(self):
        return self.spreadsheet.get(self.token.symbol).getConverted()

class RangeNode(ASTNode):
    def __init__(self, token, spreadsheet):
        super().__init__(token)
        self.spreadsheet = spreadsheet

    def eval(self):
        cells = self.spreadsheet.get(self.token.symbol)
        cellValues = []
        for cell in cells:
            cellValues.append(cell.getConverted())
        return cellValues

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
