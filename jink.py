import os
import sys
import argparse
from pathlib import Path
from jink import optimizer
from jink.lexer import Lexer
from jink.parser import Parser
from jink.optimizer import Optimizer
from jink.interpreter import Interpreter, Environment
from jink.repl import REPL
# from jink.compiler import Compiler

help_str = '\n'.join([
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
])

if len(sys.argv) >= 1 and sys.argv[0].endswith('.py'):
  sys.argv.pop(0)

verbose = False
to_compile = False

if '-v' in sys.argv:
  sys.argv.remove('-v')
  verbose = True
if '-c' in sys.argv:
  sys.argv.remove('-c')
  to_compile = True

# Launch REPL
if len(sys.argv) == 0 or (len(sys.argv) == 1 and sys.argv[0] == '-v'):
  print("jink REPL - use '[jink] help' for help - type 'exit' to exit.")
  repl = REPL(sys.stdin, sys.stdout, verbose=verbose, file_dir=Path('.'))
  repl.main_loop()

elif len(sys.argv) >= 1:
  if sys.argv[0] == 'help':
    print(help_str)

  else:
    path = Path(' '.join(sys.argv))
    path = path.resolve()

    if path.is_dir():
      raise Exception(f"File expected, was given dir: {path}")

    code = path.open().read()
    if to_compile:
      raise NotImplementedError("Compiler not yet implemented.")
      # Compiler()._eval(code, optimize=True, verbose=verbose)
    else:
      AST = Optimizer().optimize(Parser().parse(Lexer().parse(code), verbose=verbose), verbose=verbose)
      env = Environment()
      env.add_builtins()
      Interpreter().evaluate(AST, env, verbose=verbose, file_dir=path.parent)

if __name__ == "__main__":
  pass
