import os, sys
from jink.lexer import Lexer
from jink.parser import Parser
from jink.optimizer import Optimizer
from jink.interpreter import Interpreter, Environment
from jink.utils.classes import TokenType

class REPL:
  def __init__(self, stdin, stdout, environment=Environment(), lexer=Lexer(), parser=Parser(), interpreter=Interpreter(), verbose=False, file_dir=None):
    self.stdin = stdin
    self.stdout = stdout
    self.verbose = verbose
    self.dir = file_dir
    self.env = environment
    self.lexer = lexer
    self.parser = parser
    self.interpreter = interpreter

  def main_loop(self):
    while True:
      self.stdout.write("> ")
      self.stdout.flush()
      try:
        line = input()
      except KeyboardInterrupt:
        sys.exit(0)
      if not line:
        break
      self.run(line)

  def run(self, code):
    if code == 'exit':
      sys.exit(0)
    try:
      lexed = self.lexer.parse(code)
      if len(lexed) == 1 and lexed[0].type == TokenType.IDENTIFIER:
        var = self.env.get_var(lexed[0].value)
        ret = var['value'] if var != None and isinstance(var, (dict)) else var or 'null'
        print(ret)
      else:
        AST = Optimizer().optimize(self.parser.parse(lexed, verbose=self.verbose), verbose=self.verbose)
        e = self.interpreter.evaluate(AST, self.env, verbose=self.verbose, file_dir=self.dir)
        if len(e) == 1:
          print(e[0] if e[0] is not None else 'null')
        else:
          print(e[0] if e[0] is not None else 'null')
    except Exception as exception:
      print("Exception: {}".format(exception))
