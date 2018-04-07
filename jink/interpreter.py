from .classes import *

TYPES = {
  'int': int,
  'float': float,
  'string': str
}

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
    for expr in ast:
      self.evaluate_top(expr)

  def evaluate_top(self, expr):
    if isinstance(expr, IdentLiteral):
      return self.env.get_var(expr.name)

    elif isinstance(expr, (StringLiteral, IntegerLiteral, FloatingPointLiteral)):
      return self.unwrap_value(expr)
    
    elif isinstance(expr, BinaryOperator):
      left, right = self.evaluate_top(expr.left), self.evaluate_top(expr.right)
      return BINOP_EVALS[expr.operator](self.unwrap_value(left), self.unwrap_value(right)) or 'null'

    elif isinstance(expr, Assignment):
      self.env.set_var(expr.ident.name, expr.type, self.unwrap_value(self.evaluate_top(expr.value)))

    elif isinstance(expr, CallExpression):
      func = self.evaluate_top(expr.name)
      return func([self.unwrap_value(self.evaluate_top(arg)) for arg in expr.args])

    elif isinstance(expr, Function):
      return self.make_function(expr)

    elif isinstance(expr, Return):
      result = self.evaluate_top(expr.expression) or None
      return { 'type': 'return', 'value': result }

  # Obtain literal values
  def unwrap_value(self, v):
    if hasattr(v, 'value'):
      return v.value
    elif hasattr(v, '__getitem__') and not isinstance(v, (str, list)):
      return v['value']
    else:
      return v

  # Make a function
  def make_function(self, expr):
    def function(*args):
      # Create a scope for the function parameters, arguments and body
      scope = self.env.extend()

      # Tuple overrides the list that we already pass to this
      args = args[0]
      _type = expr.return_type
      params = expr.params

      if len(args) > len(params):
        raise Exception(f"Function '{expr.name}' takes {len(params)} arguments but {len(args)} were given.")

      for p, a in zip(params, args):
        if p and a:
          try:
            scope.def_var(p.name, p.type, a or p.default or 'null')
          except:
            raise Exception(f"Improper function parameter or call value at function '{expr.name}'.")

      body = self.evaluate(expr.body, scope)
      if not body:
        return
      
      if _type and _type != 'void':
        for i in body:
          if hasattr(i, 'type') and i.type == 'return':
            if not isinstance(i.value, TYPES[_type]):
              raise Exception(f"Function '{expr.name}' returned item of incorrect type: '{i.value}'.")
            else:
              return i.expr

    env = self.env.extend()
    env.def_func(expr.name, function)
    return function
