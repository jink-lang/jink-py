from jink.lexer import Lexer
from jink.parser import Parser
from jink.optimizer import Optimizer
from jink.utils.classes import *
from jink.utils.evals import *

TYPES = {
  int: 'int',
  float: 'float',
  str: 'string',
  dict: 'obj'
}

# The interpreter environment
class Environment:
  def __init__(self, parent=None, s_type=None, debug=False):
    self._id = parent._id + 1 if parent else 0
    self.index = {}
    self.parent = parent
    self.type = s_type
    self.debug = debug

  # To define builtin methods - only for use on the top level interpreter environment
  def add_builtins(self):
    self.def_func('print', lambda scope, args: print('\n'.join([str(x) for x in args]) or 'null'))
    self.def_func('string', lambda scope, args: [str(x or 'null') for x in args][0] if len(args) == 1 else [str(x or 'null') for x in args])
    self.def_func('input', lambda scope, args: input(' '.join(args)))

  def extend(self, s_type):
    return Environment(self, s_type)

  def find_scope(self, name):
    if self.debug:
      print(f"Searching for {name} in scopes..")
    scope = self
    while scope:
      if self.debug:
        print(f"Searching {scope._id}.. found {list(self.index.keys())}")
      if name in scope.index:
        return scope
      scope = scope.parent

  def get_var(self, name):
    scope = self.find_scope(name)
    if not scope:
      raise Exception(f"{name} is not defined.")

    elif name in scope.index:
      return scope.index[name]

    raise Exception(f"{name} is not defined.")

  # Functions override to update values
  # from parent scopes in local scope during their lifecycle
  def set_var(self, name, value, var_type=None, fn_scoped=False):
    scope = self.find_scope(name)

    for py_type, _type in TYPES.items():
      if isinstance(value, py_type):
        val_type = _type

    if fn_scoped:
      self.index[name] = { 'value': value, 'type': val_type, 'var_type': var_type }
      return value

    # Assignments
    if scope:
      v = scope.get_var(name)

      if var_type != None:
        raise Exception(f"{name} is already defined.")
      elif v['var_type'] == 'const':
        raise Exception(f"Constant {name} is not reassignable.")

      scope.index[name]['value'] = value
      scope.index[name]['type'] = val_type

    # Definitions
    else:
      if not var_type:
        raise Exception(f"Expected let or const, got 'null' for {name}.")
      self.index[name] = { 'value': value, 'type': val_type, 'var_type': var_type }

    return value

  def def_func(self, name, func):
    scope = self.find_scope(name)
    if scope:
      raise Exception(f"Function '{name}' is already defined!")

    if self.debug:
      print(f"Defining {name} in {self._id}")
    
    self.index[name] = func
    return func

  def __str__(self):
    return f"{self.parent or 'null'}->{self._id}:{list(self.index.keys())}"

class Interpreter:
  def __init__(self):
    self.ast = []

  def evaluate(self, ast, env, verbose=False, file_dir=None):
    self.env = env
    self.verbose = verbose
    self.dir = file_dir
    e = []
    for expr in ast:
      evaled = self.evaluate_top(expr)

      # Unpack modules
      if isinstance(evaled, list):
        for mod_expr in evaled:
          e.append(mod_expr)

      else:
        e.append(evaled)
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

        # TODO: Object methods, classes.

        elif isinstance(expr.index['index'], CallExpression):
          return self.call_function(expr.index['index'])

    elif isinstance(expr, (StringLiteral, IntegerLiteral, FloatingPointLiteral)):
      return self.unwrap_value(expr)

    elif isinstance(expr, BooleanLiteral):
      return True if self.unwrap_value(expr) == 'true' else False

    elif isinstance(expr, Null):
      return { 'type': 'null', 'value': 'null' }

    # TODO Properly evaluate unary operators modifying variables
    # (e.g. pre and post increment ++i and i++)
    elif isinstance(expr, UnaryOperator):
      # print(expr.value)
      value = self.evaluate_top(expr.value)
      return UNOP_EVALS[expr.operator](self.unwrap_value(value)) or 0

    elif isinstance(expr, BinaryOperator):
      left, right = self.evaluate_top(expr.left), self.evaluate_top(expr.right)
      return BINOP_EVALS[expr.operator](self.unwrap_value(left), self.unwrap_value(right)) or 0

    elif isinstance(expr, Module):

      # Get nested Modules
      index = []
      while expr:
        index.insert(0, expr.name)
        expr = expr.index

      # Relative import
      relative = False
      if index[0] == '.':
        index.pop()
        relative = True

      # Pretend like I know what I'm doing
      # TODO Standard Library

      try:
        if relative:
          module = (self.dir / f"{index[0]}.jk").open().read()
        else:
          # Is Directory
          if (self.dir / index[0]).is_dir():
            pass
          # Is File
          elif (self.dir / f"{index[0]}.jk").is_file():
            module = (self.dir / f"{index[0]}.jk").open().read()
          else:
            raise Exception(f"Module '{index[0]}' not found at '{self.dir}'.")
      except:
        raise Exception(f"Failed to import module {index[0]}.")

      lexed = Lexer().parse(module)
      parsed = Parser().parse(lexed, self.verbose)
      optimized = Optimizer().optimize(parsed, self.verbose)
      return self.evaluate(optimized, self.env, self.verbose, self.dir)

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
      return self.call_function(expr)

    elif isinstance(expr, Function):
      return self.make_function(expr)

    elif isinstance(expr, Return):
      result = self.evaluate_top(expr.value)
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

  # Call a function in a new scope
  def call_function(self, expr):
    scope = self.env.extend(f"call_{expr.name.name}")
    func = self.evaluate_top(expr.name)
    return func(scope, [self.unwrap_value(self.evaluate_top(arg)) for arg in expr.args])

  # Make a function
  def make_function(self, func):
    def function(scope, args):
      params = func.params

      # Exception upon overload
      if len(args) > len(params):
        raise Exception(f"Function '{func.name}' takes {len(params)} arguments but {len(args)} were given.")

      # Apply arguments to this call's scope
      # If argument doesn't exist use function default if it exists
      i = 0

      for p in params:
        default = None

        if p.default:
          default = self.unwrap_value(p.default)

        if len(args) > i:
          value = args[i] if args[i] not in (None, 'null') else default or 'null'

        else:
          value = default if default not in (None, 'null') else 'null'

        if value != None:
          try:
            scope.set_var(p.name, value, p.type, fn_scoped=True)
          except Exception as e:
            raise Exception(f"{e}\nException: Improper function parameter or call argument at function '{func.name}'.")
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
