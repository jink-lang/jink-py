import sys
from jink.lexer import Lexer
from jink.parser import Parser
from jink.optimizer import optimize
from jink.interpreter import Interpreter
from jink.utils.classes import Environment


class REPL:
  def __init__(self, stdin, stdout, environment=Environment(), lexer=Lexer(), parser=Parser(), interpreter=Interpreter()):
    self.stdin = stdin
    self.stdout = stdout
    self.env = environment
    self.lexer = lexer
    self.parser = parser
    self.interpreter = interpreter

  def mainLoop(self):
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
    try:
      AST = optimize(self.parser.parse(self.lexer.parse(code)))
      e = self.interpreter.evaluate(AST, self.env)
      if len(e) == 1:
        print(e[0])
      else:
        print(e[0])
    except Exception as exception:
      print("Exception: {}".format(exception))
