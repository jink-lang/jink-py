from jink.utils.names import *
from jink.utils.classes import *
from jink.utils.future_iter import FutureIter
from jink.utils.func import pickle
import json

PRNTLINE = "\n--------------------------------\n"

class Parser:
  def __init__(self):
    self.tokens = None

  def consume(self, item, soft=False):
    """Removes expected token, given a type or a tuple of types."""
    current = self.tokens.current

    if not item:
      return self.tokens._next()

    # Doesn't error out if the token isn't found
    # But removes it if found
    if soft:
      if isinstance(item, tuple):
        if current.type in item:
          return self.tokens._next()
      elif current.type == item:
        return self.tokens._next()
    else:
      self.tokens._next()
      if isinstance(item, tuple):
        if current.type not in item:
          raise Exception(f"Expected {' or '.join(item)}, got '{current.type}' on line {current.line}.")
        else:
          return current
      else:
        # Strings have text that could be used to spoof this check so I account for them here
        if current.value == item and current.type != TokenType.STRING:
          return current
        elif current.type == item:
          return current
        raise Exception(f"Expected '{item}', got '{current.type}' on line {current.line}.")

  def parse(self, tokens, verbose=False):
    self.tokens = FutureIter(tokens)
    ast = []
    while self.tokens.current is not None:
      if self.tokens.current.type != TokenType.NEWLINE:
        ast.append(self.parse_top())
      else:
        self.tokens._next()

    if verbose:
      print("AST:", PRNTLINE, json.dumps(pickle(ast), indent=2), PRNTLINE)

    return ast

  def parse_literal(self, tokens):
    return self.parse(tokens)

  def parse_to_console(self, tokens):
    program = self.parse(tokens)
    for expr in program:
      print(expr)

  def skip_newlines(self, count=-1):
    while self.tokens.current != None and self.tokens.current.type == TokenType.NEWLINE and count != 0:
      count -= 1
      self.tokens._next()
    return self.tokens.current

  def parse_top(self):
    init = self.tokens.current

    if init == None:
      return

    elif init.type != TokenType.KEYWORD:
      return self.parse_expr()

    elif init.value in ('let', 'const'):
      self.tokens._next()
      ident = self.consume(TokenType.IDENTIFIER)
      cur = self.tokens.current

      # Assignments
      if (cur.type == TokenType.OPERATOR and cur.value == '=') or cur.type in (TokenType.NEWLINE, TokenType.SEMICOLON):
        self.tokens._next()
        return self.parse_assignment(init.value, ident.value)

    elif init.value == 'fun':
      self.tokens._next()
      return self.parse_function()

    # Return statements
    elif init.value == 'return':
      return self.parse_return()

    # Conditionals
    elif init.value == 'if':
      return self.parse_conditional()

    # Null
    elif init.value == 'null':
      self.tokens._next()
      return Null()

    else:
      raise Exception(f"Expected keyword, got '{init.value}' on line {init.line}.")

  def parse_expr(self, precedence=0):
    left = self.parse_primary()
    current = self.tokens.current

    while current and current.type == TokenType.OPERATOR and self.get_precedence(current) >= precedence:
      operator = self.tokens._next()
      if operator.value in ('++', '--'):
        return UnaryOperator(operator.value + ':post', left)

      next_precedence = self.get_precedence(operator)
      if self.is_left_associative(operator):
        next_precedence += 1

      right = self.parse_expr(next_precedence)
      left = BinaryOperator(operator.value, left, right)

      current = self.tokens.current

    if current and current.type == TokenType.SEMICOLON:
      self.consume(TokenType.SEMICOLON)

    return left

  def parse_primary(self):
    self.skip_newlines()
    current = self.tokens.current
    if current == None: return

    if self.is_unary_operator(current):
      operator = self.tokens._next()
      if operator.value in ('-', '+', '!'):
        value = self.parse_primary()
        return UnaryOperator(operator.value, value)
      value = self.parse_expr(self.get_precedence(operator))
      return UnaryOperator(operator.value, value)

    elif current.value == '(':
      self.consume(TokenType.LPAREN)
      value = self.parse_expr(0)
      self.consume(TokenType.RPAREN)
      return value

    elif current.value == '{':
      self.consume(TokenType.LBRACE)
      obj = self.parse_object()
      self.consume(TokenType.RBRACE)
      return obj

    elif current.type == TokenType.NUMBER:
      current = self.tokens._next()
      if current.value.count('.') > 0:
        return FloatingPointLiteral(float(current.value))
      return IntegerLiteral(int(current.value))

    elif current.type == TokenType.STRING:
      return StringLiteral(self.tokens._next().value)

    elif current.type == TokenType.IDENTIFIER:
      ident = self.tokens._next().value
      if self.tokens.current.value == '.':
        self.tokens._next()
        index = { 'type': 'prop', 'index': self.parse_top() }
        return IdentLiteral(ident, index)
      elif self.tokens.current.value == '(':
        return self.parse_call(ident)
      elif self.tokens.current.value == '=':
        self.tokens._next()
        return self.parse_assignment(None, ident)
      else:
        return IdentLiteral(ident)

    elif current.type == TokenType.KEYWORD:
      keyword = self.tokens._next().value
      if keyword in ('true', 'false'):
        return BooleanLiteral(keyword)
      elif self.tokens.current.value == '(':
        return self.parse_call(keyword)
      elif keyword == 'null':
        return Null()

    raise Exception(f"Expected primary expression, got '{current.value}' on line {current.line}.")

  def is_unary_operator(self, token):
    if hasattr(token, 'type'):
      if token.type == TokenType.STRING:
        return False
    return token.value in ('-', '+', '++', '--', '!')

  def is_left_associative(self, token):
    if hasattr(token, 'type'):
      if token.type == TokenType.STRING:
        return False
    return token.value not in ('++', '--', '+=', '-=', '=')

  def get_precedence(self, token):
    if token.value in ('+', '-'):
      return 1
    elif token.value in ('*', '/', '%'):
      return 2
    elif token.value in ('^'):
      return 3
    else:
      return 0

  def parse_assignment(self, var_type, name):
    if self.tokens.current.type in (TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.COMMA):
      assignment = Assignment(var_type, IdentLiteral(name), None)
    elif self.tokens.current.type == TokenType.RPAREN:
      assignment = Assignment(var_type, IdentLiteral(name), None)
      return assignment
    else:
      assignment = Assignment(var_type, IdentLiteral(name), self.parse_expr())

    if self.tokens.current != None and self.tokens.current.type != TokenType.COMMA:
      self.consume((TokenType.NEWLINE, TokenType.SEMICOLON))

    return assignment

  def parse_call(self, func_name):
    args = self.parse_args_params('args')
    return CallExpression(IdentLiteral(func_name), args)

  def parse_function(self):
    ident = self.consume(TokenType.IDENTIFIER)
    params = self.parse_args_params('params')
    body = self.parse_block()
    return Function(ident.value, params, body)

  # Parse function parameters and call arguments
  def parse_args_params(self, location):
    self.consume(TokenType.LPAREN)
    l = []

    # Function parameters
    if location == 'params':
      while True and self.tokens.current != None:
        if self.tokens.current.value == ')':
          self.consume(TokenType.RPAREN)
          break
        elif self.tokens.current.value == '{':
          break

        cur = self.tokens._next()
        if cur.type == TokenType.KEYWORD and cur.value in ('let', 'const'):
          ident = self.consume(TokenType.IDENTIFIER)
          _next = self.tokens.current

          # Close out function params
          if _next.type == TokenType.RPAREN:
            l.append(FunctionParameter(ident.value, cur.value, None))

          # Expect comma or colon
          # fun test(let a<,> let b<:> 10) {}
          elif _next.type in (TokenType.COMMA, TokenType.OPERATOR) and _next.value in (',', ':'):
            if _next.value == ':':
              self.tokens._next()
              default = self.parse_expr()
              l.append(FunctionParameter(ident.value, cur.value, default))
              self.tokens._next()
            elif _next.value == ',':
              l.append(FunctionParameter(ident.value, cur.value, None))
              self.tokens._next()
          else:
            raise Exception(f"Expected comma or colon, got '{cur.value}' on line {cur.line}.")
        else:
          raise Exception(f"Expected let or const, got '{cur.value}' on line {cur.line}.")

    # Call arguments
    else:
      while True and self.tokens.current != None:
        if self.tokens.current.value == ')':
          self.consume(TokenType.RPAREN)
          break
        l.append(self.parse_top())
        if self.tokens.current.value in (',', 'newline'):
          self.consume((TokenType.COMMA, TokenType.NEWLINE), soft=True)
        else:
          self.consume(TokenType.RPAREN)
          break
    return l

  # Return parsing
  def parse_return(self):
    self.tokens._next()
    if self.tokens.current.type == TokenType.SEMICOLON:
      self.tokens._next()
      return Return(None)
    if self.tokens.current.type == TokenType.NEWLINE:
      return Return(None)
    expr = self.parse_expr()
    return Return(expr)

  # Conditional parsing
  def parse_conditional(self):
    init = self.tokens._next()

    # Parse else first because it is unlike if/elseif
    if init.value == 'else':
      return Conditional(init.value, None, self.parse_block(), None)

    body = []
    else_body = []
    self.consume(TokenType.LPAREN)
    expr = self.parse_expr()
    self.consume(TokenType.RPAREN)
    body = self.parse_block()

    # If an else case is next
    self.skip_newlines()
    _next = self.tokens.current
    if _next and _next.type == TokenType.KEYWORD and _next.value in ('elseif', 'else'):
      else_body.append(self.parse_conditional())

    return Conditional(init.value, expr, body, else_body)

  # Parse blocks for functions and conditionals
  def parse_block(self):
    body = []
    if self.tokens.current.value == '{':
      self.consume(TokenType.LBRACE)
      self.skip_newlines()
      while self.tokens.current != None and self.tokens.current.value != '}':
        body.append(self.parse_top())
        self.skip_newlines()
      if self.tokens._next() == None:
        raise Exception(f"Expected '}}', got '{self.tokens.current.value}' on line {self.tokens.current.line}.")

    # One or two lined
    # ex: fun say_hi() return print("Hi")
    else:
      init = self.tokens.current
      # Skip only one line
      # If there is more space before an expression, you're doing it wrong kiddo
      self.skip_newlines(1)
      if self.tokens.current.type == TokenType.NEWLINE:
        raise Exception(f"Empty function body on line {init.line}.")
      body.append(self.parse_top())

    return body

  def parse_kv_pair(self):
    self.skip_newlines()
    k = self.consume((TokenType.IDENTIFIER, TokenType.STRING)).value
    self.consume(':')
    if self.tokens.current.type == TokenType.LBRACE:
      self.consume(TokenType.LBRACE)
      v = self.parse_object()
      self.consume(TokenType.RBRACE)
    else:
      v = self.consume((TokenType.IDENTIFIER, TokenType.STRING)).value
    return k, v

  def parse_object(self):
    obj = {}
    while self.tokens.current is not None and self.tokens.current.type is not TokenType.RBRACE:
      k, v = self.parse_kv_pair()
      obj[k] = v
      self.skip_newlines()
      if self.tokens.current.type == TokenType.RBRACE:
        break
      self.consume(TokenType.COMMA)

    if self.tokens.current.value != '}':
      raise Exception(f"Expected '}}', got '{self.tokens.current.value}' on line {self.tokens.current.line}.")
    return obj
