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

    elif isinstance(expr, Null):
      return { 'type': 'null', 'value': 'null' }

    elif isinstance(expr, UnaryOperator):
      value = self.evaluate_top(expr.value)
      return UNOP_EVALS[expr.operator](self.unwrap_value(value)) or 0

    elif isinstance(expr, BinaryOperator):
      left, right = self.evaluate_top(expr.left), self.evaluate_top(expr.right)
      return BINOP_EVALS[expr.operator](self.unwrap_value(left), self.unwrap_value(right)) or 0

    elif isinstance(expr, Assignment):
      value = self.unwrap_value(self.evaluate_top(expr.value))
      if value is None:
        return self.env.def_var(expr.ident.name, expr.type)
      return self.env.set_var(expr.ident.name, expr.type, value)

    elif isinstance(expr, Conditional):
      if hasattr(expr, 'expression') and expr.expression != None:
        result = self.evaluate_condition(self.evaluate_top(expr.expression))
        if result not in ('true', 'false'):
          raise Exception("Conditional improperly used.")
        elif result == 'true':
          return self.evaluate(expr.body, self.env)
        elif result == 'false' and expr.else_body:
          return self.evaluate_top(expr.else_body[0])
        else:
          return
      self.evaluate(expr.body, self.env)

    elif isinstance(expr, CallExpression):
      scope = self.env.extend('call')
      func = self.evaluate_top(expr.name)
      return func(scope, [self.unwrap_value(self.evaluate_top(arg)) for arg in expr.args])

    elif isinstance(expr, Function):
      return self.make_function(expr)

    elif isinstance(expr, Return):
      result = self.evaluate_top(expr.expression)
      return { 'type': 'return', 'value': self.unwrap_value(result) }

  def evaluate_condition(self, cond):
    if cond in ('true', 'false'):
      return cond
    elif cond in (True, False):
      return 'true' if True else 'false'
    elif 'type' in cond:
      if cond['type'] == 'null':
        return 'false'
      elif cond['type'] != 'bool':
        return 'true'

  # Make a function
  def make_function(self, func):
    def function(scope, args):
      params = func.params

      # Exception upon overload
      if len(args) > len(params):
        raise Exception(f"Function '{func.name}' takes {len(params)} arguments but {len(args)} were given.")

      # Apply arguments to this call's scope, otherwise use function defaults if any
      # TODO Exception handling in the case of an argument not passed when there is no default
      for p, a in zip(params, args):
        default = None
        if p.default:
          default = self.unwrap_value(p.default)
        value = a if a not in (None, 'null') else default or 'null'
        if value != None:
          try:
            scope.set_var(p.name, p.type, value)
          except:
            raise Exception(f"Improper function parameter or call argument at function '{func.name}'.")

      _return = None
      for e in func.body:
        if func.return_type and func.return_type != 'void':
          result = self.evaluate([e], scope)[0]
          if isinstance(result, list):
            result = result[0] if len(result) > 0 else []
          if result and hasattr(result, '__getitem__') and not isinstance(result, str) and result['type'] == 'return':
            if isinstance(result['value'], bool):
              _return = 'true' if result['value'] == True else 'false'
            elif isinstance(result['value'], (int, float)):
              _return = result['value'] if result['value'] != None else 0
            elif isinstance(result['value'], TYPES[func.return_type]):
              _return = result['value']
            else:
              raise Exception(f"Function '{func.name}' of return type {func.return_type} returned item of incorrect type: '{result['value'] or 'null'}'.")
            break
        else:
          self.evaluate([e], scope)

      # Step back out of this scope
      self.env = self.env.parent

      if _return is None or (isinstance(_return, list) and (_return[0] in (None, 'null') or _return[0]['value'] is None)):
        return 'null'
      else:
        return _return

    self.env.def_func(func.name, function)
    return function

  # Obtain literal values
  def unwrap_value(self, v):
    if hasattr(v, 'value'):
      return v.value
    elif hasattr(v, '__getitem__') and not isinstance(v, (str, list)):
      return v['value']
    else:
      return v
