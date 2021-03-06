import string

class FormulaNameError(Exception):
    def __init__(self, msg, token):
        super().__init__(msg)
        self.token = token

    def __repr__(self):
        return "Error: function not found: " + self.token.symbol

def flat(arr):
    res = []
    for el in arr:
        if isinstance(el, list) or isinstance(el, tuple):
            for innerEl in el:
                res.append(innerEl)
        else:
            res.append(el)
    return res

def flattenArgs(func):
    def wrapper(*args):
        return func(*flat(args))

    return wrapper

def ignoreEmptyStringArgs(func):
    def wrapper(*args):
        return func(*filter(lambda e: not isinstance(e, str) or e.strip() != "", args))
    return wrapper

def numericArgsOnly(func):
    def wrapper(*args):
        return func(*filter(lambda e: not isinstance(e, str), args))
    return wrapper

@flattenArgs
@numericArgsOnly
def SUM(*args):
    return sum(flat(args))

@flattenArgs
@numericArgsOnly
def MAX(*args):
    return max(args)

@flattenArgs
@numericArgsOnly
def MIN(*args):
    return min(args)

@flattenArgs
@numericArgsOnly
def AVERAGE(*args):
    print(repr(args))
    return sum(args) / len(args)

@flattenArgs
@numericArgsOnly
def MEDIAN(*args):
    sortedArgs = sorted(args)
    if len(sortedArgs) % 2 == 0:
        midLeft = len(sortedArgs) // 2 - 1
        midRight = len(sortedArgs) // 2
        return (sortedArgs[midLeft] + sortedArgs[midRight]) / 2
    else:
        return sortedArgs[len(sortedArgs) // 2]

@flattenArgs
def COUNT(*args):
    count = 0
    for arg in args:
        if isinstance(arg, int) or isinstance(arg, float):
            count += 1
    return count

@flattenArgs
def COUNTA(*args):
    count = 0
    for arg in args:
        if arg != "":
            count += 1
    return count

def COUNTIF(values, criterion):
    return countOrSumIf(values, criterion, "count")

@flattenArgs
@ignoreEmptyStringArgs
def COUNTUNIQUE(*args):
    S = set()
    for arg in args:
        S.add(arg)
    print(S)
    return len(S)

def SUMIF(values, criterion):
    return countOrSumIf(values, criterion, "sum")



def countOrSumIf(values, criterion, mode):
    if not isinstance(values, list) and not isinstance(values, tuple):
        values = [values]
    res = 0
    buffer = ""
    criterionValue = 0
    for c in criterion[::-1]:
        if c not in string.digits + ".":
            if buffer != "":
                criterionValue = float(buffer)
            break
        else:
            buffer = c + buffer
    for value in values:
        if isinstance(value, int) or isinstance(value, float):
            value = float(value)
            print(repr(value), repr(criterionValue), value >= criterionValue)
            if mode == "count":
                if criterion[0:2] == ">=":
                    res += 1 if value >= criterionValue else 0
                elif criterion[0:2] == "<=":
                    res += 1 if value <= criterionValue else 0
                elif criterion[0] == "=":
                    res += 1 if value == criterionValue else 0
                elif criterion[0] == ">":
                    res += 1 if value > criterionValue else 0
                elif criterion[0] == "<":
                    res += 1 if value < criterionValue else 0
                elif criterion[0] in string.digits + ".":
                    res += 1 if value == float(criterion) else 0
            elif mode == "sum":
                if criterion[0:2] == ">=":
                    res += value if value >= criterionValue else 0
                elif criterion[0:2] == "<=":
                    res += value if value <= criterionValue else 0
                elif criterion[0] == "=":
                    res += value if value == criterionValue else 0
                elif criterion[0] == ">":
                    res += value if value > criterionValue else 0
                elif criterion[0] == "<":
                    res += value if value < criterionValue else 0
                elif criterion[0] in string.digits + ".":
                    res += value if value == float(criterion) else 0
        elif mode == "count":
            res += 1 if value == criterion else 0
    return res

# isPrime is the fasterIsPrime from https://www.cs.cmu.edu/~112/notes/notes-loops.html#isPrime
def isPrime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    maxFactor = round(n ** 0.5)
    for factor in range(3, maxFactor + 1, 2):
        if n % factor == 0:
            return False
    return True

# nthPrime also from https://www.cs.cmu.edu/~112/notes/notes-loops.html#isPrime
def NTHPRIME(n):
    found = 0
    canidate = 0
    while found <= n:
        canidate += 1
        if isPrime(canidate):
            found += 1
    return canidate

formulae = {
    "SUM": SUM,
    "MIN": MIN,
    "MAX": MAX,
    "AVERAGE": AVERAGE,
    "MEDIAN": MEDIAN,
    "COUNT": COUNT,
    "COUNTA": COUNTA,
    "COUNTIF": COUNTIF,
    "COUNTUNIQUE": COUNTUNIQUE,
    "SUMIF": SUMIF,
    "NTHPRIME": NTHPRIME
}
def runFunction(token, arguments):
    name = token.symbol

    if name not in formulae:
        raise FormulaNameError(f'NameError: Function not found: {token.symbol}', token)
    return formulae[name](*arguments)