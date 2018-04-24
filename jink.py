import sys
from jink.lexer import Lexer
from jink.parser import Parser
from jink.optimizer import optimize
from jink.interpreter import Interpreter
from jink.utils.classes import Environment
from jink.repl import REPL
lexer = Lexer()
parser = Parser()
interpreter = Interpreter()
env = Environment()

env.def_func('print', lambda scope, args: print('\n'.join([str(x) for x in args]) or 'null'))
env.def_func('string', lambda args: [str(x or 'null') for x in args][0] if len(args) == 1 else [str(x or 'null') for x in args])

code = ''
if len(sys.argv) > 1:
  if not sys.argv[1].endswith('.jk'):
    sys.argv[1] += '.jk'
  code = open(sys.argv[1]).read()

  if not code:
    raise Exception(f"Error reading file {sys.argv[1]}")

  AST = optimize(parser.parse(lexer.parse(code)))
  interpreter.evaluate(AST, env)
else:
  repl = REPL(sys.stdin, sys.stdout, env)
  while True:
    repl.main_loop()
