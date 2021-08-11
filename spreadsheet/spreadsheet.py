from spreadsheet.cell import Cell
from spreadsheet.range import Range, Reference

def parseCSV(text, spreadsheet):
    arr = []
    row = 0
    for line in text.splitlines():
        cells = line.split(",")
        col = 0
        for i in range(len(cells)):
            cells[i] = Cell(cells[i], row, col, spreadsheet)
            col += 1
        arr.append(cells)
        row += 1

    return arr

class Spreadsheet(object):
    def __init__(self, rows, cols, data = ""):
        self.data = parseCSV(data, self)
        for i in range(len(self.data), rows):
            self.data.append([])

        for row in range(len(self.data)):
            for col in range(len(self.data[row]), cols):
                self.data[row].append(Cell("", row, col, self))

    def getValue(self, ref):
        if not isinstance(ref, Reference):
            raise Exception("Spreadsheet getValue expects a reference, but got " + ref)
        return self.get(ref).get()

    def get(self, refOrRange):
        if isinstance(refOrRange, Reference):
            ref = refOrRange
            return self.data[ref.row - 1][ref.col]
        elif isinstance(refOrRange, Range):
            givenRange = refOrRange
            res = []
            for row in range(givenRange.fromRef.row, givenRange.toRef.row + 1):
                res = res + self.data[row - 1][givenRange.fromRef.col:givenRange.toRef.col + 1]
            return res
        else:
            raise Exception("Spreadsheet.get expected a Reference or Range, got " + repr(refOrRange))

    def setValue(self, ref, val):
        return self.data[ref.row - 1][ref.col].set(val)