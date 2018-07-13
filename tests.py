import unittest
from jink.lexer import Lexer
from jink.parser import Parser
from jink.utils.future_iter import FutureIter

class LexerTest(unittest.TestCase):
  def setUp(self):
    self.lexer = Lexer()

  def test_string(self):
    """Ensures strings are interpreted properly."""
    code = "'hi'"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "[{string hi}]", "Issue in string tokenization."

  def test_string_escape(self):
    """Ensures the escape character lexes properly."""
    code = "let hey_there = '\\'Hello world\\''"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "[{keyword let}, {identifier hey_there}, {operator =}, {string 'Hello world'}]", "Issue in escape character lexical analysis."

  def test_assignment_1(self):
    """Ensures variable declaration and assignment are lexed properly."""
    code = "let hello = 'world'"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "[{keyword let}, {identifier hello}, {operator =}, {string world}]", "Issue in variable declaration tokenization."

  def test_assignment_2(self):
    """Ensures variable declaration and assignment are lexed properly."""
    code = "let pi = 3.14"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "[{keyword let}, {identifier pi}, {operator =}, {number 3.14}]", "Issue in variable declaration tokenization."
  
  def test_call_1(self):
    """Ensures function calls are lexed properly."""
    code = "print('Hello world!')"
    lexed = self.lexer.parse_literal(code)
    assert lexed == "[{identifier print}, {lparen (}, {string Hello world!}, {rparen )}]", "Issue in function call tokenization."


class ParserTest(unittest.TestCase):
  def setUp(self):
    self.lexer = Lexer()
    self.parser = Parser()

  def test_call(self):
    """Ensures function calls are parsed properly."""
    code = "print('hello')"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)
    assert parsed == "[{CallExpression {IdentLiteral print ()} [{StringLiteral hello}]}]", "Issue in function call parsing."

  def test_math(self):
    """Ensures arithmetic is parsed properly."""
    code = "5 + 5 / 2"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)
    assert parsed == "[{BinaryOperator + {left: {IntegerLiteral 5}, right: {BinaryOperator / {left: {IntegerLiteral 5}, right: {IntegerLiteral 2}}}}}]", "Issue in arithmetic parsing."
  
  def test_assignment_1(self):
    """Ensures variable declaration and assignment are parsed properly."""
    code = "let test = 5 * 5 / 5"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)
    assert parsed == "[{Assignment {IdentLiteral test ()} {BinaryOperator / {left: {BinaryOperator * {left: {IntegerLiteral 5}, right: {IntegerLiteral 5}}}, right: {IntegerLiteral 5}}}}]", "Issue in assignment parsing."
  
  def test_conditional_1(self):
    """Ensures conditionals are parsed properly."""
    code = "if (1 == 1) return 1"
    tokens = self.lexer.parse(code)
    parsed = self.parser.parse_literal(tokens)
    assert parsed == "[{Conditional if {BinaryOperator == {left: {IntegerLiteral 1}, right: {IntegerLiteral 1}}} [{Return {IntegerLiteral 1}}] []}]", "Issue in inline conditional parsing."


if __name__ == "__main__":
  unittest.main() # run all tests
