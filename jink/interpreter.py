# Major credit to http://lisperator.net

from .classes import *

TYPES = {
  'int': int,
  'float': float,
  'string': str
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
      return self.env._get(expr.name)

    elif isinstance(expr, (StringLiteral, IntegerLiteral, FloatingPointLiteral)):
      return self.unwrap_value(expr)

    elif isinstance(expr, Assignment):
      self.env.set_var(expr.ident.name, expr.type, self.unwrap_value(expr.value))

    elif isinstance(expr, CallExpression):
      func = self.evaluate_top(expr.name)
      return func([self.unwrap_value(self.evaluate_top(arg)) for arg in expr.args])

    elif isinstance(expr, Function):
      return self.make_function(expr)

    elif isinstance(expr, Return):
      r = { 'type': 'return', 'expr': expr.expression }
      return r
  
  # Cheeky way of getting the value out of things
  def unwrap_value(self, v):
    if hasattr(v, 'value'):
      return v.value
    elif hasattr(v, '__getitem__') and not isinstance(v, str):
      return v['value']
    else:
      return v

  def make_function(self, expr):
    def function(*args):
      _type = expr.return_type
      params = expr.params
      scope = self.env.extend()
      for i in params:
        try:
          scope.def_var(i.name, i.type, i.default)
        except:
          raise Exception(f"Improper function parameter at function '{expr.name}'.")
      
      for i in self.evaluate(expr.body, scope):
        if _type:
          if hasattr(i, 'type') and i.type == 'return':
            if not isinstance(i.expr, TYPES[_type]):
              raise Exception("Gay")
            else:
              return i.expr

    env = self.env.extend()
    env.def_func(expr.name, function)
    return function
