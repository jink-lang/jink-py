from .classes import *

BINOP_EVALS = {
  '+': lambda x, y: x + y,
  '-': lambda x, y: x - y,
  '/': lambda x, y: x / y,
  '*': lambda x, y: x * y
}

class Optimizer:
  def optimize(self, ast):
    self.ast = ast
    optimized = []

    if ast is None:
      raise Exception("AST not found")

    for expr in ast:
      optimized.append(self.const_fold(expr))
    return optimized

  def const_fold(self, expr):
    if isinstance(expr, BinaryOperator):
      left, right = self.const_fold(expr.left), self.const_fold(expr.right)
      if isinstance(left, IntegerLiteral) and isinstance(right, IntegerLiteral):
        return IntegerLiteral(int(BINOP_EVALS[expr.operator](left.value, right.value)))
      elif isinstance(left, (FloatingPointLiteral, IntegerLiteral)) and isinstance(right, (FloatingPointLiteral, IntegerLiteral)):
        return FloatingPointLiteral(BINOP_EVALS[expr.operator](left.value, right.value))
    elif isinstance(expr, Assignment):
      expr.value = self.const_fold(expr.value)
    elif isinstance(expr, Function):
      expr.body = self.const_fold(expr.body)
    return expr
