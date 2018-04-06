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
string print(string hello) {
  print(hello)
}

print('hi')
"""

code2 = """
int jew = 5
print(string(jew))
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

#   lexed = lexer.parse(code)
#   print(lexed)
#   print('\n')
#   parsed = parser.parse(lexed)
#   print(parsed)

env = Environment(None)

AST = validate(optimize(parser.parse(lexer.parse(code))))
# print(AST)
interpreter.evaluate(AST, env)
