import sys
import json
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
env.def_func('string', lambda scope, args: [str(x or 'null') for x in args][0] if len(args) == 1 else [str(x or 'null') for x in args])
env.def_func('input', lambda scope, args: input(' '.join(args)))

code = ''
if len(sys.argv) > 1 and '-v' not in sys.argv:
  sys.argv.pop(0)
  _path = ' '.join(sys.argv)
  if not _path.endswith('.jk'):
    _path += '.jk'
  code = open(_path).read()

  if not code:
    raise Exception(f"Error reading file {sys.argv[0]}")

  AST = optimize(parser.parse(lexer.parse(code)))

  # For testing (printing the AST)
  # _AST = ""
  # for expr in AST:
  #   _AST += (f"{expr}, ").replace("'", '"')
  # print(_AST[:-2])

  interpreter.evaluate(AST, env)
else:
  if '-v' in sys.argv:
    repl = REPL(sys.stdin, sys.stdout, env, verbose=True)
  else:
    repl = REPL(sys.stdin, sys.stdout, env)
  while True:
    repl.main_loop()
