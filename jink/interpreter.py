from .utils.classes import *
from .utils.evals import *

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
    
    elif isinstance(expr, BooleanLiteral):
      return True if self.unwrap_value(expr) == 'true' else False

    elif isinstance(expr, UnaryOperator):
      value = self.evaluate_top(expr.value)
      return UNOP_EVALS[expr.operator](self.unwrap_value(value)) or 0

    elif isinstance(expr, BinaryOperator):
      left, right = self.evaluate_top(expr.left), self.evaluate_top(expr.right)
      return BINOP_EVALS[expr.operator](self.unwrap_value(left), self.unwrap_value(right)) or 0

    elif isinstance(expr, Assignment):
      value = self.unwrap_value(self.evaluate_top(expr.value))
      if value is None:
        return self.env.def_var(expr.ident.name, expr.type, self.env)
      return self.env.set_var(expr.ident.name, expr.type, value, self.env)

    elif isinstance(expr, Conditional):
      if hasattr(expr, 'expression') and expr.expression != None:
        result = self.evaluate_top(expr.expression)
        if result not in ('true', 'false'):
          raise Exception("Conditional improperly used.")
        if result == 'true':
          return self.evaluate(expr.body, self.env)
        return self.evaluate_top(expr.else_body[0])
      self.evaluate(expr.body, self.env)

    elif isinstance(expr, CallExpression):
      func = self.evaluate_top(expr.name)
      return func([self.unwrap_value(self.evaluate_top(arg)) for arg in expr.args])

    elif isinstance(expr, Function):
      return self.make_function(expr)

    elif isinstance(expr, Return):
      result = self.evaluate_top(expr.expression)
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
            scope.set_var(p.name, p.type, a or p.default or 'null', scope)
          except:
            raise Exception(f"Improper function parameter or call argument at function '{func.name}'.")

      _return = None
      for e in func.body:
        if func.return_type and func.return_type != 'void':
          result = self.evaluate([e], scope)[0]
          if result and hasattr(result, '__getitem__') and result['type'] == 'return':
            if isinstance(result['value'], bool):
              _return = 'true' if result['value'] == True else 'false'
            elif isinstance(result['value'], TYPES[func.return_type]):
              _return = result['value']
            else:
              raise Exception(f"Function '{func.name}' of return type {func.return_type} returned item of incorrect type: '{result['value']}'.")
        else:
          self.evaluate([e], scope)

      if _return is None or (isinstance(_return, list) and (_return[0] in (None, 'null') or _return[0]['value'] is None)):
        return 'null'
      else:
        return _return

    env = self.env.extend()
    env.def_func(func.name, function)
    return function
