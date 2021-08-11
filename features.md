# Feature Tracker

**Done**

- Basic UI
- Circular Reference Detection (#CIR_REF)
- Error handling (#ERROR)
- Only update what needs to be updated. e.g. don't reevaluate cells that don't need re-evaluation, but do reevaluate them when the value of a referenced cell changes
- Some Formulas
    - Basic Math Operators: `+` `-` `*` `/` `^`
    - Parenthetical Expressions: `(` expression `)`
    - SUM(values...) Returns the sum
    - MIN(values...) Returns the lowest number
    - MAX(values...) Returns the highest number
    - AVERAGE(values...) Returns the average
    - MEDIAN(values...) Returns the median
    - COUNT(values...) Count number of cells with numeric values
    - COUNTA(values...) Count number of non-empty cells
    - COUNTIF(range, criterion) Returns the count of cells in range that match criterion.
        If the value of the cell is not a number, then it matches the criterion if the
        cell's value is equal to the criterion. If the value of the cell is a number, 
        the criterion can be a number in a string, optionally prefixed with a comparator
        `>=`, `<=`, `>`, `<`, or `=` to check the number against.
    - SUMIF(range, criterion) Returns the sum of all cells that would have been
      counted if COUNTIF(range, criterion) was called.
    - NTHPRIME(n) Returns the nth prime. The 0th prime is 2, the 1st prime is 3, etc.
