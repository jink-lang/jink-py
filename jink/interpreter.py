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
      if None in (expr.index['type'], expr.index['index']):
        return self.env.get_var(expr.name)
      elif expr.index['type'] == 'prop':
        var = self.env.get_var(expr.name)

        if var['type'] != 'obj':
          raise Exception(f"Variable '{expr.name}' of type {var['type']} does not support indexing")

        obj = var['value']
        if isinstance(expr.index['index'], IdentLiteral):
          if expr.index['index'].name not in obj:
            raise Exception(f"Object '{expr.name}' does not contain the property '{expr.index['index'].name}'")
          else:
            return obj[expr.index['index'].name]
        elif isinstance(expr.index['index'], CallExpression):
          pass

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
      value = self.evaluate_top(expr.value)
      try:
        value = self.unwrap_value(value)
      except KeyError:
        pass
      return self.env.set_var(expr.ident.name, value if value != None else 'null', expr.type)

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
    
    elif isinstance(expr, dict):
      return expr

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
      i = 0

      for p in params:
        default = None

        if isinstance(p, Assignment):
          default = p.value or 'null'
          name = p.ident.name
          _type = p.type
          class Object(): pass
          p = Object()
          setattr(p, 'name', name)
          setattr(p, 'type', _type)
        elif p.default:
          default = self.unwrap_value(p.default)

        if len(args) > i:
          value = args[i] if args[i] not in (None, 'null') else default or 'null'
        else:
          value = default if default not in (None, 'null') else 'null'

        if value != None:
          try:
            scope.set_var(p.name, value, p.type)
          except:
            raise Exception(f"Improper function parameter or call argument at function '{func.name}'.")
        i += 1

      # Ensure returning of the correct value
      _return = None
      for e in func.body:
        result = self.evaluate([e], scope)[0]
        if isinstance(result, list):
          result = result[0] if len(result) > 0 else []
        if result and isinstance(result, dict) and result['type'] == 'return':
          if isinstance(result['value'], bool):
            _return = 'true' if result['value'] == True else 'false'
          elif isinstance(result['value'], (int, float)):
            _return = result['value'] if result['value'] != None else 0
          else:
            _return = result['value']
          break

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
