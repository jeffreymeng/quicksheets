from formula.parser import Parser
from formula.lexer import lex, getReferences
from spreadsheet.range import Reference
import string
class Cell(object):
    def __init__(self, rawValue, row, col, parentSpreadsheet):
        self.dependents = set() # cells that depend on this cell's value
        self.dependencies = set() # cells that this cell depends on
        self.row = row
        self.col = col
        self.spreadsheet = parentSpreadsheet
        self._rawValue = ""
        self._computedValue = ""
        self.isNumber = False
        self.set(rawValue)
        self.error = False

    def __repr__(self):
        return f'Cell<{repr(Reference(self.col, self.row + 1))}, {repr(self._computedValue)}>'

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return isinstance(other, Cell) and self.row == other.row and self.col == other.col

    # Set the raw value of the cell. If it starts with an equal sign, it will
    # be parsed as a formula
    def set(self, rawValue):
        if self._rawValue == rawValue:
            return
        self._rawValue = rawValue
        self.update()

    # recompute the cell's computedValue
    def update(self, blacklist = None):
        if blacklist == None:
            blacklist = set()
        self.error = False
        if self in blacklist:
            self.error = True
            self._computedValue = "#CIR_DEP"
            return
        else:
            blacklist.add(self)

        if self._rawValue != "" and self._rawValue[0] == "=":
            try:
                self._computedValue = str(Parser(lex(self._rawValue[1:]), self.spreadsheet).getExpression().eval())
                if Cell.isNumeric(self._computedValue) and float(self._computedValue) // 1 == float(self._computedValue):
                    self._computedValue = str(int(float(self._computedValue)))
                updatedDependencyTokens = getReferences(lex(self._rawValue[1:]))
                updatedDependencies = set()
                for token in updatedDependencyTokens:
                    if token.type == "reference":
                        updatedDependencies.add(self.spreadsheet.get(token.symbol))
                    elif token.type == "range":
                        for cell in self.spreadsheet.get(token.symbol):
                            updatedDependencies.add(cell)
                dependenciesToDelete = self.dependencies - updatedDependencies
                dependenciesToAdd = updatedDependencies - self.dependencies
                for d in dependenciesToDelete:
                    self.removeDependency(d)
                for d in dependenciesToAdd:
                    self.addDependency(d)

            except Exception as e:
                print(e)
                self.errorMsg = e
                self._computedValue = "#ERROR"
                self.error = True

        else:
            for d in list(self.dependencies):
                self.removeDependency(d)
            if Cell.isNumeric(self._rawValue) and float(self._rawValue) // 1 == float(self._rawValue):
                self._computedValue = str(int(float(self._rawValue)))
            else:
                self._computedValue = self._rawValue

        self.isNumber = Cell.isNumeric(self._computedValue)


        for dependent in self.dependents:
            dependent.update(blacklist)

    @staticmethod
    def isNumeric(s):
        for c in s:
            if c not in string.digits + ".":
                return False
        return s != "" and s.count(".") <= 1

    def addDependent(self, cell):
        self.dependents.add(cell)
        cell.dependencies.add(self)

    def removeDependent(self, cell):
        self.dependents.remove(cell)
        cell.dependencies.remove(self)

    def addDependency(self, cell):
        self.dependencies.add(cell)
        cell.dependents.add(self)

    def removeDependency(self, cell):
        self.dependencies.remove(cell)
        cell.dependents.remove(self)

    # Returns the computed value of the cell.
    def get(self):

        return self._computedValue

    # Returns the raw value of the cell
    def getRaw(self):
        return self._rawValue

    # Returns the number rounded to 10 decimal places, which mostly avoids floating point precision errors.
    def getRounded(self):
        if self.isNumber and self.getConverted() // 1 != self.getConverted():
            return str(round(self.getConverted(), 10))
        return self.get()

    # returns the computed value of the cell, converted into a number if it is a number
    def getConverted(self):
        if self.isNumber:
            return float(self.get())
        else:
            return self.get()