
def raiseError():
    x = 1/0

try:
    print(raiseError())
    print(1 + "ddsaf")
except ZeroDivisionError as e:
    print(f'Handled Error: {e}')
