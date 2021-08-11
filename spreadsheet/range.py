import string

class Reference(object):
    @staticmethod
    # convert a number into a letter column
    def colStr(colNum):
        if colNum < 26:
            return chr(ord("A") + colNum)
        else:
            return chr(ord("A") + ((colNum // 26) - 1)) + chr(ord("A") + (colNum % 26))

    @staticmethod
    # convert a letter column (e.g. "A" or "AB") into a number, with A = 0, B = 1, AA = 26, AB = 27
    def colNum(colStr):
        if len(colStr) == 1:
            return ord(colStr) - ord("A")
        else:
            tens = ord(colStr[0]) - ord("A")
            ones = ord(colStr[1]) - ord("A")
            return (tens + 1) * 26 + ones

    def __init__(self, col, row=None):

        # single arg such as "A4" or "AA19"
        if row == None:
            buffer = ""
            colMode = True
            for c in col:
                if colMode and c not in string.ascii_uppercase:
                    col = buffer
                    buffer = ""
                    colMode = False
                buffer += c
            row = int(buffer)
        if isinstance(col, str):
            col = Reference.colNum(col)
        self.col = col
        self.row = row

    def __repr__(self):
        return f'Ref({Reference.colStr(self.col)}{self.row})'

    def __eq__(self, other):
        return isinstance(other, Reference) \
               and self.col == other.col and self.row == other.row


class Range(object):
    def __init__(self, fromRef, toRef):
        self.fromRef = fromRef
        self.toRef = toRef

    def __repr__(self):
        return f'Range({Reference.colStr(self.fromRef.col)}{self.fromRef.row}:{Reference.colStr(self.toRef.col)}{self.toRef.row})'

    def __eq__(self, other):
        return isinstance(other, Range) \
               and self.fromRef == other.fromRef and self.toRef == other.toRef

def testReferenceColNum():
    print("Testing Reference static methods...", end = "")
    stringForm = ["A", "B", "C", "Z", "AA", "AB", "AC",       "AZ",        "ZZ"]
    numberForm = [  0,   1,   2,  25,   26,   27,   28, 26 * 2 - 1, 26 * 27 - 1]

    for i in range(len(stringForm)):
        try:
            assert (Reference.colNum(stringForm[i]) == numberForm[i])
            assert (Reference.colStr(numberForm[i]) == stringForm[i])
        except:
            print(f'Failed case {i}')
    print("Passed!")


if (__name__ == '__main__'):
    testReferenceColNum()