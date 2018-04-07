import sys
from jink.lexer import Lexer
from jink.parser import Parser
from jink.validator import validate
from jink.optimizer import optimize
from jink.interpreter import Interpreter
from jink.classes import Environment

lexer = Lexer()
parser = Parser()
interpreter = Interpreter()

code = """
int add(int a, int b, int c) {
  int result = a + b + c
  return result
}

int result = add(1, 2, 3)
print(result)
"""

code2 = """
int hi() {
  return 1
}

print(hi())
"""

code3 = """
float my_function(int make_float) {
  make_float = make_float + 0.0
  float(make_float)
}

my_function(hey_earth) :: Returns 1337.0
"""

# if len(sys.argv) > 1:
#   code = open(sys.argv[1]).read()

env = Environment(None)
AST = validate(optimize(parser.parse(lexer.parse(code))))
interpreter.evaluate(AST, env)
