from .evals import *

TYPES = {
  int: 'int',
  float: 'float',
  str: 'string',
  dict: 'obj'
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

  def get_var(self, name):
    scope = self.find_scope(name)
    if not scope:
      raise Exception(f"{name} is not defined.")

    elif name in scope.index:
      return scope.index[name]

    raise Exception(f"{name} is not defined.")

  def set_var(self, name, value, var_type=None):
    scope = self.find_scope(name)

    for py_type, _type in TYPES.items():
      if isinstance(value, py_type):
        val_type = _type

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
      self.index[name] = { 'value': value, 'type': val_type, 'var_type': var_type }

    return value

  def def_func(self, name, func):
    self.index[name] = func
    return func

  def __str__(self):
    return f"{self.parent or 'null'}->{self._id}:{self.index}"


class Token:
  def __init__(self, _type, value, line, pos):
    self.type, self.value, self.line, self.pos = _type, value, line, pos
  def __str__(self):
    return f"{{{self.type} {self.value}}}"
  __repr__ = __str__


class BinaryOperator:
  __slots__ = ('operator', 'left', 'right')
  def __init__(self, operator, left, right):
    self.operator, self.left, self.right = operator, left, right
  def __str__(self):
    return f"{{BinaryOperator {self.operator} {{left: {self.left}, right: {self.right}}}}}"
  __repr__ = __str__

class UnaryOperator:
  __slots__ = ('operator', 'value')
  def __init__(self, operator, value):
    self.operator, self.value = operator, value
  def __str__(self):
    return f"{{UnaryOperator {self.operator} {self.value}}}"
  __repr__ = __str__

class IntegerLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f"{{IntegerLiteral {self.value}}}"
  __repr__ = __str__

class FloatingPointLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f"{{FloatingPointLiteral {self.value}}}"
  __repr__ = __str__

class StringLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f"{{StringLiteral {self.value}}}"
  __repr__ = __str__

class BooleanLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f"{{BooleanLiteral {self.value}}}"
  __repr__ = __str__

class IdentLiteral:
  def __init__(self, name, index={ 'type': None, 'index': None }):
    self.name, self.index = name, index
  def __str__(self):
    return f"{{IdentLiteral {self.name} ({self.index['index'] or ''})}}"
  __repr__ = __str__

class Null:
  def __str__(self):
    return '{{Null}}'
  __repr__ = __str__


class Assignment:
  __slots__ = ('type', 'ident', 'value')
  def __init__(self, _type, ident, value):
    self.type, self.ident, self.value = _type, ident, value
  def __str__(self):
    return f"{{Assignment {self.ident} {self.value}}}"
  __repr__ = __str__

class CallExpression:
  __slots__ = ('name', 'args')
  def __init__(self, name, args):
    self.name, self.args = name, args
  def __str__(self):
    return f"{{CallExpression {self.name} {self.args}}}"
  __repr__ = __str__

class Function:
  __slots__ = ('name', 'params', 'body')
  def __init__(self, name, params, body):
    self.name, self.params, self.body = name, params, body
  def __str__(self):
    return f"{{Function {self.name} {self.params} {self.body}}}"
  __repr__ = __str__

class FunctionParameter:
  __slots__ = ('name', 'type', 'default')
  def __init__(self, name, _type, default=None):
    self.name, self.type, self.default = name, _type, default
  def __str__(self):
    return f"{{FunctionParameter {self.name} {self.type}}}"
  __repr__ = __str__

class Return:
  __slots__ = ('expression')
  def __init__(self, expression):
    self.expression = expression
  def __str__(self):
    return f"{{Return {self.expression}}}"
  __repr__ = __str__

class Conditional:
  __slots__ = ('type', 'expression', 'body', 'else_body')
  def __init__(self, _type, expression, body, else_body):
    self.type, self.expression, self.body, self.else_body = \
      _type, expression, body, else_body
  def __str__(self):
    return f"{{Conditional {self.type} {self.expression} {self.body} {self.else_body}}}"
  __repr__ = __str__
