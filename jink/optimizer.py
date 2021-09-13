from jink.utils.classes import *
from jink.utils.evals import *

def optimize(ast):
  optimized = []
  if ast is None:
    raise Exception("AST not found")
  for expr in ast:
    optimized.append(const_fold(expr))
  return optimized

def const_fold(expr):
  if isinstance(expr, UnaryOperator):
    left = const_fold(expr.value)

    if isinstance(left, IntegerLiteral):
      return IntegerLiteral(int(UNOP_EVALS[expr.operator](left.value)))

    elif isinstance(left, FloatingPointLiteral):
      return FloatingPointLiteral(UNOP_EVALS[expr.operator](left.value))

  elif isinstance(expr, BinaryOperator):
    left, right = const_fold(expr.left), const_fold(expr.right)

    # Evaluate result of binop
    evaled = BINOP_EVALS[expr.operator](left.value, right.value)

    # Return corresponding value
    if isinstance(evaled, int):
      return IntegerLiteral(evaled)
    elif isinstance(evaled, float):
      return FloatingPointLiteral(evaled)

    # String concatenation
    elif isinstance(left, StringLiteral) and isinstance(right, StringLiteral):
      if expr.operator != '+':
        raise Exception(f"Only '+' operator can be used for string/string binop.")
      return StringLiteral(str(left.value) + str(right.value))

    # String multiplication
    elif isinstance(left, StringLiteral) and isinstance(right, IntegerLiteral):
      if expr.operator != '*':
        raise Exception(f"Only '*' operator can be used for string/int binop.")
      return StringLiteral(str(left.value)*right.value)

  elif isinstance(expr, Assignment):
    expr.value = const_fold(expr.value)

  elif isinstance(expr, Function):
    expr.body = const_fold(expr.body)

  elif isinstance(expr, CallExpression):
    expr.args = [const_fold(e) for e in expr.args]

  return expr
