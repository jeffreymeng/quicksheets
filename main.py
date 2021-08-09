from cmu_112_graphics import *

"""
TODOS: (top first)
- Add labels / headers for rows and cols
- Parse formulas
- organize code
- Edit textbox?
=== TP1 Goal ===

"""


class Cell(object):
    def __init__(self, text):
        self.text = text
        self.isNumber = text.isnumeric()

    def __repr__(self):
        return f'Cell<{repr(self.text)}>'

def parseCSV(text):
    arr = []
    for line in text.splitlines():
        cells = line.split(",")
        for i in range(len(cells)):
            cells[i] = Cell(cells[i])
        arr.append(cells)

    return arr

def appStarted(app):
    app.rows = 20
    app.cols = 10
    app.margin = 10
    testData = parseCSV("""
one,,three,,5,6,7
3,5,71,4
hello,goodbye,,
    """)

    for i in range(app.rows - len(testData)):
        testData.append([])

    for row in testData:
        for i in range(app.cols - len(row)):
            row.append(Cell(""))

    app.data = testData
    print(testData)

def mousePressed(app, event):
    row, col = getCell(app, event.x, event.y)
    if row == -1 or col == -1:
        return
    newValue = app.getUserInput("Enter new cell value:")
    if newValue == None:
        return
    app.data[row][col] = Cell(newValue)

def keyPressed(app, event):
    pass

def timerFired(app):
    pass

# pointInGrid taken from the grid animation notes
def pointInGrid(app, x, y):
    return ((app.margin <= x <= app.width - app.margin) and
            (app.margin <= y <= app.height - app.margin))

# getCell adapted from the grid animation notes
def getCell(app, x, y):
    if (not pointInGrid(app, x, y)):
        return (-1, -1)

    rows, cols, margin = app.rows, app.cols, app.margin
    width = (app.width - margin - margin) // cols
    height = (app.height - margin - margin) // rows

    row = int((y - app.margin) / height)
    col = int((x - app.margin) / width)

    return row, col


# getCellBounds is adapted from my hw9, and also the grid animation notes
def getCellBounds(app, row, col):
    rows, cols, margin = app.rows, app.cols, app.margin
    width = (app.width - margin - margin) // cols
    height = (app.height - margin - margin) // rows
    return (margin + width * col,
            margin + height * row,
            margin + width * (col + 1),
            margin + height * (row + 1))


def redrawAll(app, canvas):
    cellMargin = 5
    for row in range(app.rows):
        for col in range(app.cols):
            x0, y0, x1, y1 = getCellBounds(app, row, col)
            yAvg = (y0 + y1) // 2
            canvas.create_rectangle(x0, y0, x1, y1)
            cell = app.data[row][col]

            if cell.isNumber:
                canvas.create_text(x1 - cellMargin, yAvg,
                                        text=cell.text,
                                        anchor="e")
            else:
                canvas.create_text(x0 + cellMargin, yAvg,
                                       text=cell.text,
                                       anchor="w")
def main():
    runApp(width=800, height=500)


if (__name__ == '__main__'):
    main()