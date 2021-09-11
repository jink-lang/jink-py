import unittest
from jink.lexer import Lexer
from jink.parser import Parser
from jink.utils.classes import *
from jink.utils.func import pickle

class LexerTest(unittest.TestCase):
  def setUp(self):
    self.lexer = Lexer()

  def test_string(self):
    """Ensures strings are interpreted properly."""
    code = "'hi'"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "['{TokenType.STRING hi}']", "Issue in string tokenization."

  def test_string_escape(self):
    """Ensures the escape character lexes properly."""
    code = "let hey_there = '\\'Hello world\\''"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "['{TokenType.KEYWORD let}', '{TokenType.IDENTIFIER hey_there}', '{TokenType.OPERATOR =}', \"{TokenType.STRING 'Hello world'}\"]", "Issue in escape character lexical analysis."

  def test_assignment_1(self):
    """Ensures variable declaration and assignment are lexed properly."""
    code = "let hello = 'world'"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "['{TokenType.KEYWORD let}', '{TokenType.IDENTIFIER hello}', '{TokenType.OPERATOR =}', '{TokenType.STRING world}']", "Issue in variable declaration tokenization."

  def test_assignment_2(self):
    """Ensures variable declaration and assignment are lexed properly."""
    code = "let pi = 3.14"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "['{TokenType.KEYWORD let}', '{TokenType.IDENTIFIER pi}', '{TokenType.OPERATOR =}', '{TokenType.NUMBER 3.14}']", "Issue in variable declaration tokenization."

  def test_call_1(self):
    """Ensures function calls are lexed properly."""
    code = "print('Hello world!')"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "['{TokenType.IDENTIFIER print}', '{TokenType.LPAREN (}', '{TokenType.STRING Hello world!}', '{TokenType.RPAREN )}']", "Issue in function call tokenization."


class ParserTest(unittest.TestCase):
  def setUp(self):
    self.lexer = Lexer()
    self.parser = Parser()

  def test_call(self):
    """Ensures function calls are parsed properly."""
    code = "print('hello')"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)[0]
    test = CallExpression(
      name=IdentLiteral(name='print'),
      args=[StringLiteral('hello')]
    )
    assert pickle(parsed) == pickle(test), "Issue in function call parsing."

  def test_math(self):
    """Ensures arithmetic is parsed properly."""
    code = "5 + 5 / 2"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)[0]
    test = BinaryOperator(operator='+',
      left=IntegerLiteral(5),
      right=BinaryOperator(operator='/',
        left=IntegerLiteral(5),
        right=IntegerLiteral(2)
      )
    )
    assert pickle(parsed) == pickle(test), "Issue in arithmetic parsing."

  def test_assignment_1(self):
    """Ensures variable declaration and assignment are parsed properly."""
    code = "let test = 5 * 5 / 5"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)[0]
    test = Assignment(_type='let',
      ident=IdentLiteral(name='test'),
      value=BinaryOperator(operator='/',
        left=BinaryOperator(operator='*',
          left=IntegerLiteral(5),
          right=IntegerLiteral(5)
        ),
        right=IntegerLiteral(5)
      )
    )
    assert pickle(parsed) == pickle(test), "Issue in assignment parsing."

  def test_conditional_1(self):
    """Ensures conditionals are parsed properly."""
    code = "if (1 == 1) return 1"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)[0]
    test = Conditional('if',
      expression=BinaryOperator(operator='==',
        left=IntegerLiteral(1),
        right=IntegerLiteral(1)
      ),
      body=[Return(IntegerLiteral(1))],
      else_body=[]
    )
    assert pickle(parsed) == pickle(test), "Issue in inline conditional parsing."


if __name__ == "__main__":
  unittest.main() # run all tests
