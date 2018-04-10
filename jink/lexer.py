from .utils.classes import LexerToken as Token
from .utils import future_iter
FutureIter = future_iter.FutureIter

TYPES = (
  'int',
  'float',
  'string',
  'bool',
  'void'
)

KEYWORDS = (
  'if', 'else', 'elseif',
  'import', 'export',
  'return', 'delete',
  'true', 'false', 'null'
)

KEYWORDS = KEYWORDS + TYPES

OPERATORS = (
  '.', '=', '!', '?',
  '+', '-', '*', '/',
  '%', '>', '<', '|',
  '&', '^', '~', '#',
  '>=', '<=', '==', '++', '--'
  '!=', '&&', '||'
)

# One lexer boi
class Lexer:
  def __init__(self):
    self.pos = 0
    self.line = 1
    self.line_pos = 0

  def parse(self, code):
    self.code = FutureIter(code)
    self.code_end = len(str(self.code)) - 1
    return [token for token in self.parse_tokens()]

  def parse_literal(self, code):
    return str(self.parse(code))

  def parse_tokens(self):
    while self.code.next is not None:

      # All good, increment positions
      self.line_pos += 1
      self.pos += 1
      
      char = self.code._next()

      if char == '\\':
        if self.code.next == '\n':
          self.line += 1
          self.line_pos = 0
        self.code._next()
        char = self.code.next
        continue

      if char.isspace():
        if char == '\n':
          self.line_pos = 0
          self.line += 1
          yield Token('newline', 'newline', self.line, self.pos)

      elif char == ':':
        if self.code.next in [':', '>']:
          self.process_comment()
        else:
          yield Token('colon', ':', self.line, self.pos)
      elif char == '(':
        yield Token('lparen', '(', self.line, self.pos)
      elif char == ')':
        yield Token('rparen', ')', self.line, self.pos)
      elif char == '[':
        yield Token('lbracket', '[', self.line, self.pos)
      elif char == ']':
        yield Token('rbracket', ']', self.line, self.pos)
      elif char == '{':
        yield Token('lbrace', '{', self.line, self.pos)
      elif char == '}':
        yield Token('rbrace', '}', self.line, self.pos)

      elif char == ',':
        yield Token('comma', ',', self.line, self.pos)

      elif char in ("'", '"'):
        yield self.parse_string(char)

      elif char.isalpha() or char in ('_', '$'):
        yield self.parse_ident(char)

      elif char.isdigit() or char == '.':
        yield self.parse_number(char)

      elif char in OPERATORS:
        yield self.parse_operator(char)

      else:
        raise Exception('Invalid character on {0}:{1}\n  {2}\n  {3}'.format(
          self.line, self.line_pos, str(self.code).split('\n')[self.line - 1], f"{' ' * (self.line_pos - 1)}^"
        ))

  # Variables are fun, especially when you name them ridiculous things.
  def parse_ident(self, char):
    ident = char
    while self.code.next is not None and (self.code.next.isalnum() or self.code.next in ('_', '$')):
      ident += self.code.next
      self.code._next()
      self.line_pos += 1

    if ident in KEYWORDS:
      return Token('keyword', ident, self.line, self.pos)
    return Token('ident', ident, self.line, self.pos)

  # 2 + 2 = 4 - 1 = 3 big maffs.
  def parse_operator(self, operator):
    line_start = self.line_pos
    start = self.pos
    while self.code.next is not None and self.code.next in OPERATORS:
      operator += self.code.next
      self.line_pos += 1
      self.code._next()
    if not operator in OPERATORS:
      raise Exception('Invalid operator on {0}:{1}\n  {2}\n  {3}'.format(
        self.line, line_start, str(self.code).split('\n')[self.line - 1], f"{' ' * (line_start - 1)}^"
      ))
    return Token('operator', operator, self.line, start)

  # Yay, I can "Hello world" now!
  def parse_string(self, char):
    string = ''
    end = False
    start = self.pos
    while self.code.next is not None:
      # Oh boy, are we escaping?
      if self.code.next == '\\':
        self.code._next()
        self.line_pos += 1

        # Get escaped character
        nxt = self.code._next()

        # Newline is a special case
        if nxt == '\n':
          self.line += 1
          self.line_pos = 0

        # Add escaped character and move on
        else:
          string += nxt
          self.line_pos += 1
      else:
        string += self.code._next()
        self.line_pos += 1

      # Ending the string? So soon? Aw. :(
      if self.code.next == char:
        end = True
        self.code._next()
        self.line_pos += 1
        break

    if self.code.next == None and end == False:
      raise Exception('A string was not properly enclosed at {0}:{1}\n  {2}\n  {3}'.format(
        self.line, start, str(self.code).split('\n')[self.line - 1], f"{' ' * (start - 1)}^"
      ))

    return Token('string', string, self.line, start)

  # Crunch those numbers.
  def parse_number(self, char):
    num = char
    line_start = self.line_pos
    while self.code.next is not None and not self.code.next.isspace() and (self.code.next.isdigit() or self.code.next == '.'):
      num += self.code.next
      self.code._next()
      self.line_pos += 1

    # The heck?
    if not num.replace('.', '', 1).isdigit():
      raise Exception('Invalid number on {0}:{1}\n  {2}\n  {3}'.format(
        self.line, line_start, str(self.code).split('\n')[self.line - 1], f"{' ' * (line_start - 1)}^"
      ))
    else:
      return Token('number', num, self.line, self.pos)

  # Do I really need to comment on comments?
  def process_comment(self):
    cur = self.code.next
    # Single-line comment
    if self.code.next == ':':
      while not self.code.next in ('\r', '\n', None):
        self.line_pos += 1
        self.code._next()
    # Multi-line comment
    elif self.code.next == '>':
      while self.code.next is not None and (cur != '<' and self.code.next != ':'):
        self.line_pos += 1
        if self.code.next in ('\r', '\n'):
          self.line_pos = 0
          self.line += 1
        cur = self.code._next()

      if self.code.next is None or self.code.next is not ':':
        raise Exception('A multi-line comment was not closed.')
      self.code._next()
