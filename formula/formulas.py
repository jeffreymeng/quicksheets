class FormulaNameError(Exception):
    def __init__(self, msg, token):
        super().__init__(self, msg)
        self.token = token

    def __repr__(self):
        return "Error: function not found: " + self.token.symbol

def SUM(*args):
    return sum(args)

def MAX(*args):
    return max(args)

def MIN(*args):
    return min(args)



def runFunction(token, arguments):
    name = token.symbol
    functions = {
        "SUM": SUM,
        "MAX": MAX,
        "MIN": MIN
    }
    if name not in functions:
        raise FormulaNameError("", token)
    return functions[name](*arguments)