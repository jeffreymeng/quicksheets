from spreadsheet.cell import Cell
from spreadsheet.range import Range, Reference
from formula.parser import SpreadsheetReferenceError

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
        self.rows = rows
        self.cols = cols
        for i in range(len(self.data), rows):
            self.data.append([])

        for row in range(len(self.data)):
            for col in range(len(self.data[row]), cols):
                self.data[row].append(Cell("", row, col, self))

        # update all formulas now that everything has been loaded
        for row in self.data:
            for cell in row:
                cell.update()

    def exportCSV(self):
        res = ""
        for row in self.data:
            rowCSV = ""
            for cell in row:
                if cell.getRaw().count(",") != 0:
                    rowCSV = rowCSV + '"' + cell.getRaw() + '",'
                else:
                    rowCSV = rowCSV + cell.getRaw() + ","
            res += rowCSV[:-1] + "\n" # cut out last ,
        return res
    def getValue(self, ref):
        if not isinstance(ref, Reference):
            raise Exception("Spreadsheet getValue expects a reference, but got " + ref)
        return self.get(ref).get()

    def get(self, refOrRange):

        if isinstance(refOrRange, Reference):
            ref = refOrRange
            if not (0 <= ref.row - 1 < self.rows and 0 <= ref.col < self.cols):
                raise SpreadsheetReferenceError(f"Reference not in spreadsheet: {Reference.colStr(ref.col)}{ref.row}")
            return self.data[ref.row - 1][ref.col]
        elif isinstance(refOrRange, Range):
            givenRange = refOrRange
            res = []
            if not (0 <= givenRange.fromRef.row - 1 < self.rows and 0 <= givenRange.fromRef.col < self.cols \
                    and 0 <= givenRange.toRef.row - 1 < self.rows and 0 <= givenRange.toRef.col < self.cols):
                raise SpreadsheetReferenceError(f"Range not in spreadsheet: {Reference.colStr(givenRange.fromRef.col)}" \
                   + f"{givenRange.fromRef.row}:{Reference.colStr(givenRange.toRef.col)}{givenRange.toRef.row}")
            for row in range(givenRange.fromRef.row, givenRange.toRef.row + 1):
                res = res + self.data[row - 1][givenRange.fromRef.col:givenRange.toRef.col + 1]
            return res
        else:
            raise SpreadsheetReferenceError("Spreadsheet.get expected a Reference or Range, got " + repr(refOrRange))

    def setValue(self, ref, val):
        return self.data[ref.row - 1][ref.col].set(val)