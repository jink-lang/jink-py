from .classes import *

TYPES = {
  'int': int,
  'float': float,
  'string': str
}

def validate(ast):
  validated = []

  if ast is None:
    raise Exception("AST not found")

  for expr in ast:
    validated.append(validate_top(expr))
  return validated

def validate_top(expr):
  if isinstance(expr, Assignment):
    return validate_assignment(expr)
  return expr

def validate_assignment(expr):
  # _type = TYPES[expr.type]
  value = expr.value
  if isinstance(value, BinaryOperator):
    left, right = value.left, value.right

  return expr

def validate_type(expr):
  pass
