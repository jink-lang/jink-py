import sys
from jink.lexer import Lexer
from jink.parser import Parser
from jink.optimizer import optimize
from jink.interpreter import Interpreter
from jink.classes import Environment
lexer = Lexer()
parser = Parser()
interpreter = Interpreter()

code = ''
if len(sys.argv) > 1:
  if not sys.argv[1].endswith('.jk'):
    sys.argv[1] += '.jk'
  code = open(sys.argv[1]).read()
else:
  raise Exception("File path not given.")

if not code:
  raise Exception("Error in file reading.")

env = Environment()
AST = optimize(parser.parse(lexer.parse(code)))
interpreter.evaluate(AST, env)
