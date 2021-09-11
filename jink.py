import sys, argparse
from jink import optimizer
from jink.lexer import Lexer
from jink.parser import Parser
from jink.optimizer import optimize
from jink.interpreter import Interpreter, Environment
from jink.repl import REPL
# from jink.compiler import Compiler

def get_code_from_path(path):
  if not path.endswith('.jk'):
    path += '.jk'
  code = open(path).read()
  if not code:
    raise Exception(f"Error reading file {sys.argv[0]}")
  return code

if len(sys.argv) >= 1 and sys.argv[0] == 'jink.py':
  sys.argv.pop(0)

verbose = False
to_compile = False

if '-v' in sys.argv:
  sys.argv.remove('-v')
  verbose = True
if '-c' in sys.argv:
  sys.argv.remove('-c')

# Launch REPL
if len(sys.argv) == 0 or (len(sys.argv) == 1 and sys.argv[0] == '-v'):
  print("jink REPL - use '[jink] help' for help - type 'exit' to exit.")
  repl = REPL(sys.stdin, sys.stdout, verbose=verbose)
  repl.main_loop()

elif len(sys.argv) >= 1:
  if sys.argv[0] == 'help':
    print('\n'.join([
      "jink - strongly typed, JavaScript-like programming language.",
      "https://www.github.com/jink-lang/jink",
      "",
      "args:",
      "  > -v -- verbose; will output AST." # and if compiling, both optimized and unoptimized LLVM IR.",
      # "  > -c -- compile; will use compiler instead of interpreter."
      "",
      "usage:",
      "  > [jink] help                 -- shows this prompt.",
      "  > [jink] path/to/file[.jk]    -- executes interpreter on file.",
      "  > [jink] -v path/to/file[.jk] -- executes interpreter on file verbose mode.",
      # "  > [jink] -c path/to/file[.jk] -- executes compiler on file.",
      # "  > [jink] -c -v path/to/file[.jk] -- executes compiler on file in verbose mode.",
      "  > [jink]                      -- launches interpreted interactive REPL.",
      "  > [jink] -v                   -- launches interpreted interactive REPL in verbose mode."
    ]))

  else:
    path = ' '.join(sys.argv)
    code = get_code_from_path(path)

    if to_compile:
      raise NotImplementedError("Compiler not yet implemented.")
      # Compiler()._eval(code, optimize=True, verbose=verbose)
    else:
      AST = optimize(Parser().parse(Lexer().parse(code), verbose=verbose))
      env = Environment()
      env.add_builtins()
      Interpreter().evaluate(AST, env)

if __name__ == "__main__":
  pass
