from jink.utils.evals import *
from enum import Enum

class TokenType(Enum):
  EOF = 0
  NEWLINE = 1
  KEYWORD = 2
  IDENTIFIER = 3
  NUMBER = 4
  STRING = 5
  OPERATOR = 6
  LPAREN = 7
  RPAREN = 8
  LBRACKET = 9
  RBRACKET = 10
  LBRACE = 11
  RBRACE = 12
  SEMICOLON = 13
  COLON = 14
  COMMA = 15


class Token:
  def __init__(self, _type, value, line, pos):
    self.type, self.value, self.line, self.pos = _type, value, line, pos
  def __str__(self):
    return f"{{ 'type': 'Token<{self.type}>', 'contents': {{ 'value': '{self.value}', 'line': {self.line}, 'pos': {self.pos} }} }}"
  def smallStr(self):
    return f"{{{self.type} {self.value}}}"
  __repr__ = __str__


class BinaryOperator:
  __slots__ = ('operator', 'left', 'right')
  def __init__(self, operator, left, right):
    self.operator, self.left, self.right = operator, left, right

class UnaryOperator:
  __slots__ = ('operator', 'value')
  def __init__(self, operator, value):
    self.operator, self.value = operator, value

class IntegerLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value

class FloatingPointLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value

class StringLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value

class BooleanLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value

class IdentLiteral:
  def __init__(self, name, index={ 'type': None, 'index': None }):
    self.name, self.index = name, index

class Null:
  def __init__(self, value):
    self.value = "null"


class Assignment:
  __slots__ = ('type', 'ident', 'value')
  def __init__(self, _type, ident, value):
    self.type, self.ident, self.value = _type, ident, value

class CallExpression:
  __slots__ = ('name', 'args')
  def __init__(self, name, args):
    self.name, self.args = name, args

class Function:
  __slots__ = ('name', 'params', 'body')
  def __init__(self, name, params, body):
    self.name, self.params, self.body = name, params, body

class FunctionParameter:
  __slots__ = ('name', 'type', 'default')
  def __init__(self, name, _type, default=None):
    self.name, self.type, self.default = name, _type, default

class Return:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value

class Conditional:
  __slots__ = ('type', 'expression', 'body', 'else_body')
  def __init__(self, _type, expression, body, else_body):
    self.type, self.expression, self.body, self.else_body = _type, expression, body, else_body

class Module:
  __slots__ = ('name', 'index')  
  def __init__(self, name, index):
    self.name, self.index = name, index
