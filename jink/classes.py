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

class IdentLiteral:
  __slots__ = ('name')
  def __init__(self, name):
    self.name = name
  def __str__(self):
    return f'{{IdentLiteral {self.name}}}'
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
  __slots__ = ('type', 'name', 'default')
  def __init__(self, type, name, default):
    self.type, self.name, self.default = type, name, default
  def __str__(self):
    return f'{{FunctionParameter {self.type} {self.name}}}'
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
