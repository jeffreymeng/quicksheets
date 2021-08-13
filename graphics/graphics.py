from tkinter import filedialog, Menu, simpledialog, messagebox
from graphics.cmu_112_graphics import *
from spreadsheet.spreadsheet import Spreadsheet
from spreadsheet.range import Reference
from formula.lexer import lex, tokenColors, LexerError
from formula.formulae import formulae, FormulaNameError
from formula.parser import Parser, ParserSyntaxError, SpreadsheetReferenceError

dataPath = None

def initCellDimensions(app):
    rows, cols = app.rows, app.cols
    marginTop, marginBottom, marginLeft, marginRight = app.margins
    headerHeight = 20
    headerWidth = 25
    app.rowHeights = [headerHeight] + [(app.height - marginTop - marginBottom - headerHeight) // rows] * rows
    app.colWidths = [headerWidth] + [(app.width - marginLeft - marginRight - headerWidth) // cols] * cols

# readFile and writeFile from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


def appStarted(app):

    init(app, dataPath)


def init(app, path):
    app.cellMargin = 5

    app.rows = 20
    app.cols = 10

    #               T   B   L   R (top bottom left right)
    app.margins = (70, 10, 10, 10)

    app.loadButton = app.margins[2], 10, app.margins[2] + 50, app.margins[0] - 40
    app.saveButton = app.loadButton[2] + 10, app.loadButton[1], app.loadButton[2] + 60, app.loadButton[3]

    initCellDimensions(app)

    if path == None:
        data = ""
    else:
        data = readFile(path)

    app.spreadsheet = Spreadsheet(app.rows, app.cols, data)

    app.value = ""
    app.highlightedValue = highlight(app.value)
    app.focusCol = -1
    app.focusRow = -1

    app.frameRate = 20
    app.timerDelay = 1000 // app.frameRate
    app.timeSinceLastKey = 0
    app.frame = 0

def sizeChanged(app):
    initCellDimensions(app)

def mousePressed(app, event):

    x0, y0, x1, y1 = app.loadButton
    if x0 < event.x < x1 and y0 < event.y < y1:
        loadPath = filedialog.askopenfilename(initialdir=os.getcwd())
        if loadPath == "":
            return
        init(app, loadPath)
        return
    x0, y0, x1, y1 = app.saveButton
    if x0 < event.x < x1 and y0 < event.y < y1:
        def spreadsheetIsEmpty():
            for spreadsheetRow in app.spreadsheet.data:
                for cell in spreadsheetRow:
                    if cell.getRaw() != "":
                        return False
            return True
        if spreadsheetIsEmpty() and not messagebox.askyesno("Continue?", "You will lose all unsaved changes. Continue?"):
            return
        savePath = filedialog.asksaveasfilename(initialdir=os.getcwd(), filetypes= [('CSV','.csv')])
        if savePath == "":
            return
        writeFile(savePath, app.spreadsheet.exportCSV())
        return

    row, col = getCell(app, event.x, event.y)

    if row <= 0 or col <= 0:
        return

    # save previously focused cell
    app.spreadsheet.setValue(Reference(app.focusCol - 1, app.focusRow), app.value)

    currentValue = app.spreadsheet.get(Reference(col - 1, row)).getRaw()
    app.value = currentValue
    app.highlightedValue = highlight(app.value)
    app.focusCol = col
    app.focusRow = row
    # don't subtract 1 from row because the row is 1 indexed for references
    # newValue = app.getUserInput("Change value from '" + app.spreadsheet.get(Reference(col - 1, row)).getRaw() + "' to:")
    # if newValue == None:
    #     # cancelled
    #     cell = app.spreadsheet.get(Reference(col - 1, row))
    #     print(cell.dependents, cell.dependencies)
    #     return
    # app.spreadsheet.setValue(Reference(col - 1, row), newValue)


def createMulticolorText(canvas, x, y, text, **kwargs):
    currentX = x
    for (partValue, partColor) in text:
        textId = canvas.create_text(currentX, y, text=partValue, fill=partColor, anchor="w", **kwargs)
        x0, y0, x1, y1 = canvas.bbox(textId)

        currentX = x1 - 2

def keyPressed(app, event):
    app.timeSinceLastKey = 0
    if len(event.key) == 1:

        app.value = app.value + event.key
        app.highlightedValue = highlight(app.value)
    elif event.key == "Space":
        app.value = app.value + " "
        app.highlightedValue = highlight(app.value)
    elif event.key == "Delete":
        app.value = app.value[:-1]
        app.highlightedValue = highlight(app.value)
    elif event.key in ["Enter", "Tab", "Up", "Down", "Right", "Left"]:
        dy = 0
        dx = 0
        app.spreadsheet.setValue(Reference(app.focusCol - 1, app.focusRow), app.value)
        shiftKey = False # leaving this in in case I find a way in the future to detect this
        if (event.key == "Enter" and shiftKey) or event.key == "Up":
            dy = -1
        elif (event.key == "Enter" and not shiftKey) or event.key == "Down":
            dy = 1
        elif (event.key == "Tab" and shiftKey) or event.key == "Left":
            dx = -1
        elif (event.key == "Tab" and not shiftKey) or event.key == "Right":
            dx = 1

        if 1 <= app.focusCol + dx <= app.spreadsheet.cols and \
                1 <= app.focusRow + dy <= app.spreadsheet.rows:

            app.value = ""
            app.highlightedValue = highlight(app.value)
            app.focusCol += dx
            app.focusRow += dy
            app.value = app.spreadsheet.get(Reference(app.focusCol - 1, app.focusRow)).getRaw()
            app.highlightedValue = highlight(app.value)
   
    # else:
        # print(event.key)

def highlight(text):
    if len(text) == 0 or text[0] != "=":
        return [(text, "black")]
    text = text[1:]
    res = [("=", "black")]
    currentIndex = 0
    try:
        for token in lex(text):
            start = token.startPosition
            end = token.endPosition
            if start > currentIndex:
                res.append((text[currentIndex:start], "black"))
            color = tokenColors[token.type]
            if token.type == "function" and token.symbol not in formulae:
                color = "black"
            res.append((text[start:end], color))
            currentIndex = end
    except LexerError as e:
        res.append((text[currentIndex:], "black"))
    return res

def timerFired(app):
    app.timeSinceLastKey += (1000 // app.frameRate)
    # app.frame = (app.frame + 1) % 1000000 # mod a million so the number doesn't get too big

# getCell adapted from the grid animation notes
def getCell(app, x, y):
    row = None
    currentTop = app.margins[0]
    for r in range(len(app.rowHeights)):
        currentBottom = currentTop + app.rowHeights[r]
        if currentBottom > y >= currentTop:
            row = r
            break
        currentTop = currentBottom

    col = None
    currentLeft = app.margins[2]
    for c in range(len(app.colWidths)):
        currentRight = currentLeft + app.colWidths[c]
        if currentRight > x >= currentLeft:
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
    rows, cols, margins = app.rows, app.cols, app.margins
    rowHeights = app.rowHeights
    colWidths = app.colWidths

    return (margins[2] + sum(colWidths[:col]),
            margins[0] + sum(rowHeights[:row]),
            margins[2] + sum(colWidths[:col + 1]),
            margins[0] + sum(rowHeights[:row + 1]))

def drawCells(app, canvas):
    cellMargin = app.cellMargin
    for row in range(app.rows + 1):
        for col in range(app.cols + 1):

            rectangleKwargs = dict()
            if app.focusCol == col and app.focusRow == row:
                rectangleKwargs = {
                    "outline": "blue",
                    "width": 3
                }
            elif (row == 0 and col == app.focusCol) or (col == 0 and row == app.focusRow):
                rectangleKwargs = {
                    "fill": "lightgray",
                }

            x0, y0, x1, y1 = getCellBounds(app, row, col)
            yAvg = (y0 + y1) // 2
            canvas.create_rectangle(x0, y0, x1, y1, **rectangleKwargs)

            if row == 0 and col == 0:
                # just draw the rectangle; no text
                continue

            if row == 0:  # top header
                canvas.create_text((x0 + x1) // 2, yAvg,
                                   text=chr(ord("A") + col - 1),
                                   anchor="c")
            elif col == 0:  # side header
                canvas.create_text((x0 + x1) // 2, yAvg,
                                   text=int(row),
                                   anchor="c")
            else:
                cell = app.spreadsheet.get(Reference(col - 1, row))

                if cell.isNumber:
                    canvas.create_text(x1 - cellMargin, yAvg,
                                       text=cell.getRounded(),
                                       anchor="e")
                else:
                    canvas.create_text(x0 + cellMargin, yAvg,
                                       text=cell.getRounded(),
                                       anchor="w")

def drawButtons(app, canvas):
    marginTop, marginBottom, marginLeft, marginRight = app.margins
    x0, y0, x1, y1 = app.loadButton
    canvas.create_rectangle(x0, y0, x1, y1)
    canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text="Load")
    x02, y02, x12, y12 = app.saveButton
    canvas.create_rectangle(x02, y02, x12, y12)
    canvas.create_text((x02 + x12) // 2, (y02 + y12) // 2, text="Save")

def drawInputBox(app, canvas):
    inputMargin = 5
    marginTop, marginBottom, marginLeft, marginRight = app.margins
    # canvas.create_text(marginLeft + inputMargin, (marginTop // 2), text = app.value, anchor="w")

    x0, y0, x1, y1 = marginLeft, 40, marginLeft + sum(app.colWidths), marginTop - 10
    canvas.create_rectangle(x0, y0, x1, y1)

    createMulticolorText(canvas, x0 + inputMargin, ((y0 + y1) // 2), app.highlightedValue)

    if app.focusCol <= 0 and app.focusRow <= 0:
        return
    cell = app.spreadsheet.get(Reference(app.focusCol - 1, app.focusRow))

    if app.value != "" and app.value[0] == "=":
        try:
            res = Parser(lex(app.value[1:]), app.spreadsheet).getExpression().eval()
            canvas.create_text(x1 - app.cellMargin, (y0 + y1) // 2,
                               text=f'= {res}',
                               anchor="e", fill="black")
        except Exception as e:
            if cell.getRaw() == app.value or app.timeSinceLastKey >= 1000:
                canvas.create_text(x1 - app.cellMargin, (y0 + y1) // 2,
                           text=str(e),
                           anchor="e", fill="red")

def redrawAll(app, canvas):
    drawButtons(app, canvas)
    drawInputBox(app, canvas)
    drawCells(app, canvas)
    # ovalId = canvas.create_oval(100,100,200,200,fill="red")
    # canvas.delete(ovalId)
    
def main(filename = None):
    global dataPath
    dataPath = filename
    runApp(width=800, height=500)


if (__name__ == '__main__'):
    main()