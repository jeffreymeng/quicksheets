from graphics.cmu_112_graphics import *
from spreadsheet.spreadsheet import Spreadsheet
from spreadsheet.range import Reference


"""
TODO: 
Text entry
drag and drop
syntax highlighting
laoding saving data
clipboard
"""

def initCellDimensions(app):
    rows, cols, margin = app.rows, app.cols, app.margin
    headerHeight = 20
    headerWidth = 25
    app.rowHeights = [headerHeight] + [(app.height - 2 * margin - headerHeight) // rows] * rows
    app.colWidths = [headerWidth] + [(app.width - 2 * margin - headerWidth) // cols] * cols

# readFile and writeFile from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


def appStarted(app):
    app.rows = 20
    app.cols = 10
    app.margin = 10
    initCellDimensions(app)

#     app.spreadsheet = Spreadsheet(app.rows, app.cols, """
# one,,three,,5,6,7
# 3,5,71,4
# hello,goodbye,,
#     """)

    app.spreadsheet = Spreadsheet(app.rows, app.cols,
"""1,2,3,4,5,,Rob
2,4,6,8,10,,David
3,6,9,12,15,,David
4,8,12,16,20,,Rob
5,10,15,20,25,,Rob
,,,,,,John
""" )
def sizeChanged(app):
    initCellDimensions(app)

def mousePressed(app, event):
    row, col = getCell(app, event.x, event.y)

    if row <= 0 or col <= 0:
        return
    print(repr(app.spreadsheet.get(Reference(col - 1, row)).getRaw()))
    # don't subtract 1 from row because the row is 1 indexed for references
    newValue = app.getUserInput("Change value from '" + app.spreadsheet.get(Reference(col - 1, row)).getRaw() + "' to:")
    if newValue == None:
        # cancelled
        cell = app.spreadsheet.get(Reference(col - 1, row))
        print(cell.dependents, cell.dependencies)
        return
    app.spreadsheet.setValue(Reference(col - 1, row), newValue)

def keyPressed(app, event):
    pass

def timerFired(app):
    pass


# getCell adapted from the grid animation notes
def getCell(app, x, y):
    row = None
    currentTop = app.margin
    for r in range(len(app.rowHeights)):
        currentBottom = currentTop + app.rowHeights[r]
        if currentBottom > y > currentTop:
            row = r
            break
        currentTop = currentBottom

    col = None
    currentLeft = app.margin
    for c in range(len(app.colWidths)):
        currentRight = currentLeft + app.colWidths[c]
        if currentRight > x > currentLeft:
            col = c
            break
        currentLeft = currentRight

    if row == None or col == None:
        return -1, -1

    return row, col

def getCellDimensions(app, row, col):
    return app.colWidths[col], app.rowHeights[row]

# getCellBounds is adapted from my hw9, and also the grid animation notes
def getCellBounds(app, row, col):
    rows, cols, margin = app.rows, app.cols, app.margin
    rowHeights = app.rowHeights
    colWidths = app.colWidths

    return (margin + sum(colWidths[:col]),
            margin + sum(rowHeights[:row]),
            margin + sum(colWidths[:col + 1]),
            margin + sum(rowHeights[:row + 1]))


def redrawAll(app, canvas):
    cellMargin = 5

    for row in range(app.rows + 1):
        for col in range(app.cols + 1):
            x0, y0, x1, y1 = getCellBounds(app, row, col)
            yAvg = (y0 + y1) // 2
            canvas.create_rectangle(x0, y0, x1, y1)

            if row == 0 and col == 0:
                # just draw the rectangle; no text
                continue

            if row == 0: # top header
                canvas.create_text((x0 + x1) // 2, yAvg,
                                   text=chr(ord("A") + col - 1),
                                   anchor="c")
            elif col == 0: # side header
                canvas.create_text((x0 + x1) // 2, yAvg,
                                   text=int(row),
                                   anchor="c")
            else:
                cell = app.spreadsheet.get(Reference(col - 1, row))

                if cell.isNumber:
                    canvas.create_text(x1 - cellMargin, yAvg,
                                            text=cell.get(),
                                            anchor="e")
                else:
                    canvas.create_text(x0 + cellMargin, yAvg,
                                           text=cell.get(),
                                           anchor="w")
    ovalId = canvas.create_oval(100,100,200,200,fill="red")
    canvas.delete(ovalId)
    
def main():
    runApp(width=800, height=500)


if (__name__ == '__main__'):
    main()