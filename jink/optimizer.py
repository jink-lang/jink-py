from jink.utils.classes import *
from jink.utils.evals import *

class Optimizer:
  def optimize(self, ast, verbose=False):
    self.verbose = verbose
    optimized = []
    if ast is None:
      raise Exception("AST not found")
    for expr in ast:
      folded = self.const_fold(expr)
      if isinstance(folded, list):
        for f in folded:
          optimized.append(f)
      else:
        optimized.append(folded)
    return optimized

  def const_fold(self, expr):
    if isinstance(expr, UnaryOperator):
      left = self.const_fold(expr.value)

      if isinstance(left, IntegerLiteral):
        return IntegerLiteral(int(UNOP_EVALS[expr.operator](left.value)))

      elif isinstance(left, FloatingPointLiteral):
        return FloatingPointLiteral(UNOP_EVALS[expr.operator](left.value))

    elif isinstance(expr, BinaryOperator):
      left, right = self.const_fold(expr.left), self.const_fold(expr.right)

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
      expr.value = self.const_fold(expr.value)

    elif isinstance(expr, Function):
      expr.body = self.const_fold(expr.body)

    elif isinstance(expr, CallExpression):
      expr.args = [self.const_fold(e) for e in expr.args]

    return expr
