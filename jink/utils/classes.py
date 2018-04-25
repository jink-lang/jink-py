from .evals import *

TYPES = {
  'int': int,
  'float': float,
  'string': str
}

class Environment:
  def __init__(self, parent=None, s_type=None):
    self._id = parent._id + 1 if parent else 0
    self.index = {}
    self.parent = parent
    self.type = s_type

  def extend(self, s_type):
    return Environment(self, s_type)

  def find_scope(self, name):
    scope = self
    while scope:
      if name in scope.index:
        return scope
      scope = scope.parent

  def validate_type(self, name, _type, value):
    if value == 'null':
      return value
    elif _type == 'int' and isinstance(value, float):
      raise Exception(f"Tried to assign value '{value}' to variable '{name}' of type {_type}.")
    elif _type == 'string' and (isinstance(value, (float, int, bool))):
      if isinstance(value, bool):
        value = str(value).lower()
      raise Exception(f"Tried to assign value '{value}' to variable '{name}' of type {_type}.")
    elif _type in TYPES:
      try:
        value = TYPES[_type](value)
      except:
        raise Exception(f"Tried to assign value '{value or 'null'}' to variable '{name}' of type {_type}.")
    return value

  def get_var(self, name):
    scope = self.find_scope(name)
    if not scope:
      raise Exception(f"{name} is not defined.")

    elif name in scope.index:
      return scope.index[name]

    raise Exception(f"{name} is not defined.")

  # Can be either definition or reassignment
  def set_var(self, name, _type, value):
    scope = self.find_scope(name)

    # Assignments
    if scope:
      v = scope.get_var(name)
      if _type and _type != v['type']:
        raise Exception(f"Variable {name} already exists.")
      _type = v['type']
      value = self.validate_type(name, _type, value)
      scope.index[name]['value'] = value

    # Definitions
    else:
      if not _type:
        raise Exception(f"{name} is not defined.")
      value = self.validate_type(name, _type, value)
      self.index[name] = { 'type': _type, 'value': value }
    return value

  def def_func(self, name, func):
    self.index[name] = func
    return func

  def __str__(self):
    return f"{self.parent or 'null'}->{self._id}:{self.index}"


class LexerToken:
  __slots__ = ('type', 'text', 'line', 'pos')
  def __init__(self, type, text, line, pos):
    self.type, self.text, self.line, self.pos = \
      type, text, line, pos
  def __str__(self):
    return f'{{{self.type} {self.text}}}'
  __repr__ = __str__


class BinaryOperator:
  __slots__ = ('operator', 'left', 'right')
  def __init__(self, operator, left, right):
    self.operator, self.left, self.right = \
      operator, left, right
  def __str__(self):
    return f'{{BinaryOperator {self.operator} {{left: {self.left}, right: {self.right}}}}}'
  __repr__ = __str__

class UnaryOperator:
  __slots__ = ('operator', 'value')
  def __init__(self, operator, value):
    self.operator, self.value = operator, value
  def __str__(self):
    return f'{{UnaryOperator {self.operator} {self.value}}}'
  __repr__ = __str__

class IntegerLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f'{{IntegerLiteral {self.value}}}'
  __repr__ = __str__

class FloatingPointLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f'{{FloatingPointLiteral {self.value}}}'
  __repr__ = __str__

class StringLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f'{{StringLiteral {self.value}}}'
  __repr__ = __str__

class BooleanLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f'{{BooleanLiteral {self.value}}}'
  __repr__ = __str__

class IdentLiteral:
  __slots__ = ('name')
  def __init__(self, name):
    self.name = name
  def __str__(self):
    return f'{{IdentLiteral {self.name}}}'
  __repr__ = __str__

class Null:
  def __str__(self):
    return '{{Null}}'
  __repr__ = __str__

class Assignment:
  __slots__ = ('type', 'ident', 'value')
  def __init__(self, type, ident, value):
    self.type, self.ident, self.value = \
      type, ident, value
  def __str__(self):
    return f'{{Assignment {self.ident} {self.value}}}'
  __repr__ = __str__

class CallExpression:
  __slots__ = ('name', 'args')
  def __init__(self, name, args):
    self.name, self.args = name, args
  def __str__(self):
    return f'{{CallExpression {self.name} {self.args}}}'
  __repr__ = __str__

class Function:
  __slots__ = ('return_type', 'name', 'params', 'body')
  def __init__(self, return_type, name, params, body):
    self.return_type, self.name, self.params, self.body = \
      return_type, name, params, body
  def __str__(self):
    return f'{{Function {self.name} {self.params} {self.body}}}'
  __repr__ = __str__

class FunctionParameter:
  __slots__ = ('name', 'type', 'default')
  def __init__(self, name, type, default=None):
    self.name, self.type, self.default = name, type, default
  def __str__(self):
    return f'{{FunctionParameter {self.name} {self.type}}}'
  __repr__ = __str__

class Return:
  __slots__ = ('expression')
  def __init__(self, expression):
    self.expression = expression
  def __str__(self):
    return f'{{Return {self.expression}}}'
  __repr__ = __str__

class Conditional:
  __slots__ = ('type', 'expression', 'body', 'else_body')
  def __init__(self, type, expression, body, else_body):
    self.type, self.expression, self.body, self.else_body = \
      type, expression, body, else_body
  def __str__(self):
    return f'{{Conditional {self.type} {self.expression} {self.body} {self.else_body}}}'
  __repr__ = __str__
