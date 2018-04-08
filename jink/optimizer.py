from .classes import *

BINOP_EVALS = {
  '+': lambda x, y: x + y,
  '-': lambda x, y: x - y,
  '/': lambda x, y: x / y,
  '*': lambda x, y: x * y
}

def optimize(ast):
  optimized = []
  if ast is None:
    raise Exception("AST not found")
  for expr in ast:
    optimized.append(const_fold(expr))
  return optimized

def const_fold(expr):
  if isinstance(expr, BinaryOperator):
    left, right = const_fold(expr.left), const_fold(expr.right)

    if isinstance(left, IntegerLiteral) and isinstance(right, IntegerLiteral):
      return IntegerLiteral(int(BINOP_EVALS[expr.operator](left.value, right.value)))

    elif isinstance(left, (FloatingPointLiteral, IntegerLiteral)) and isinstance(right, (FloatingPointLiteral, IntegerLiteral)):
      return FloatingPointLiteral(BINOP_EVALS[expr.operator](left.value, right.value))

    elif isinstance(left, StringLiteral) or isinstance(right, StringLiteral):
      if expr.operator != '+':
        raise Exception(f"Only '+' operator can be used with strings.")
      return StringLiteral(str(left.value) + str(right.value))

  elif isinstance(expr, Assignment):
    expr.value = const_fold(expr.value)

  elif isinstance(expr, Function):
    expr.body = const_fold(expr.body)

  elif isinstance(expr, CallExpression):
    expr.args = [const_fold(e) for e in expr.args]

  return expr
