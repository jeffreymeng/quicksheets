class Cell(object):
    def __init__(self, text):
        self.text = text
        self.isNumber = text.isnumeric()

    def __repr__(self):
        return f'Cell<{repr(self.text)}>'