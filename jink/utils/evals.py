BINOP_EVALS = {
  '+': lambda x, y: 0 if x + y is None else x + y,
  '-': lambda x, y: 0 if x - y is None else x - y,
  '/': lambda x, y: 0 if x / y is None else x / y,
  '//': lambda x, y: 0 if x // y is None else x // y,
  '*': lambda x, y: 0 if x * y is None else x * y,
  '^': lambda x, y: 0 if x ** y is None else x ** y,
  '==': lambda x, y: 'true' if x == y else 'false',
  '!=': lambda x, y: 'true' if x != y else 'false',
  '>=': lambda x, y: 'true' if x >= y else 'false',
  '<=': lambda x, y: 'true' if x <= y else 'false'
}

UNOP_EVALS = {
  '-': lambda x: 0 if x - x * 2 is None else x - x * 2,
  '++': lambda x: 0 if x + 1 is None else x + 1
}