from .classes import *

BINOP_EVALS = {
  '+': lambda x, y: x + y,
  '-': lambda x, y: x - y,
  '/': lambda x, y: x / y,
  '*': lambda x, y: x * y
}

class Interpreter:
  def __init__(self):
    self.ast = []

  def evaluate(self, ast, env):
    self.env = env
    e = []
    for expr in ast:
      e.append(self.evaluate_top(expr))
    return e

  def evaluate_top(self, expr):
    if isinstance(expr, IdentLiteral):
      return self.env.get_var(expr.name)

    elif isinstance(expr, (StringLiteral, IntegerLiteral, FloatingPointLiteral)):
      return self.unwrap_value(expr)
    
    elif isinstance(expr, BinaryOperator):
      left, right = self.evaluate_top(expr.left), self.evaluate_top(expr.right)
      return BINOP_EVALS[expr.operator](self.unwrap_value(left), self.unwrap_value(right)) or 'null'

    elif isinstance(expr, Assignment):
      self.env.set_var(expr.ident.name, expr.type, self.unwrap_value(self.evaluate_top(expr.value)), self.env)

    elif isinstance(expr, CallExpression):
      func = self.evaluate_top(expr.name)
      return func([self.unwrap_value(self.evaluate_top(arg)) for arg in expr.args])

    elif isinstance(expr, Function):
      return self.make_function(expr)

    elif isinstance(expr, Return):
      result = self.evaluate_top(expr.expression) or None
      return { 'type': 'return', 'value': self.unwrap_value(result) }

  # Obtain literal values
  def unwrap_value(self, v):
    if hasattr(v, 'value'):
      return v.value
    elif hasattr(v, '__getitem__') and not isinstance(v, (str, list)):
      return v['value']
    else:
      return v

  # Make a function
  def make_function(self, func):
    def function(*args):
      # Create a scope for the function parameters, arguments and body
      scope = self.env.extend()
      params = func.params
      # Tuple from *args contains the list of args we pass as its first item
      args = args[0]

      if len(args) > len(params):
        raise Exception(f"Function '{func.name}' takes {len(params)} arguments but {len(args)} were given.")

      for p, a in zip(params, args):
        if p and a:
          try:
            scope.def_var(p.name, p.type, a or p.default or 'null')
          except:
            raise Exception(f"Improper function parameter or call value at function '{func.name}'.")

      for e in func.body:
        if func.return_type and func.return_type != 'void':
          result = self.evaluate([e], scope)[0]
          if result:
            if hasattr(result, '__getitem__') and result['type'] == 'return':
              if isinstance(result['value'], TYPES[func.return_type]):
                return result['value']
              else:
                raise Exception(f"Function '{func.name}' returned item of incorrect type: '{result['value']}'.")
        else:
          self.evaluate([e], scope)

    env = self.env.extend()
    env.def_func(func.name, function)
    return function
