from .utils import future_iter
FutureIter = future_iter.FutureIter

TYPES = (
  'int',
  'float',
  'string',
  'bool'
)

KEYWORDS = (
  'if', 'else', 'elseif',
  'import', 'export',
  'void', 'return', 'delete',
  'true', 'false', 'null'
)

class BinaryOperator:
  __slots__ = ('operator', 'left', 'right')
  def __init__(self, operator, left, right):
    self.operator, self.left, self.right = \
      operator, left, right
  def __str__(self):
    return f'{{BinaryOperator {self.operator} {{left: {self.left}, right: {self.right}}}}}'
  __repr__ = __str__

class UnaryOperator:
  __slots__ = ('operator', 'value')
  def __init__(self, operator, value):
    self.operator, self.value = operator, value
  def __str__(self):
    return f'{{UnaryOperator {self.operator} {self.value}}}'
  __repr__ = __str__

class IntegerLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f'{{IntegerLiteral {self.value}}}'
  __repr__ = __str__

class FloatingPointLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f'{{FloatingPointLiteral {self.value}}}'
  __repr__ = __str__

class StringLiteral:
  __slots__ = ('value')
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return f'{{StringLiteral {self.value}}}'
  __repr__ = __str__

class IdentLiteral:
  __slots__ = ('name')
  def __init__(self, name):
    self.name = name
  def __str__(self):
    return f'{{IdentLiteral {self.name}}}'
  __repr__ = __str__

class Assignment:
  __slots__ = ('type', 'name', 'value')
  def __init__(self, type, name, value):
    self.type, self.name, self.value = \
      type, name, value
  def __str__(self):
    return f'{{Assignment {self.name} {self.value}}}'
  __repr__ = __str__

class CallExpression:
  __slots__ = ('name', 'args')
  def __init__(self, name, args):
    self.name, self.args = name, args
  def __str__(self):
    return f'{{CallExpression {self.name} {self.args}}}'
  __repr__ = __str__

class Function:
  __slots__ = ('return_type', 'name', 'params', 'body')
  def __init__(self, return_type, name, params, body):
    self.return_type, self.name, self.params, self.body = \
      return_type, name, params, body
  def __str__(self):
    return f'{{Function {self.name} {self.params} {self.body}}}'
  __repr__ = __str__

class FunctionParameter:
  __slots__ = ('type', 'name', 'default')
  def __init__(self, type, name, default):
    self.type, self.name, self.default = type, name, default
  def __str__(self):
    return f'{{FunctionParameter {self.type} {self.name}}}'
  __repr__ = __str__

class Return:
  __slots__ = ('expression')
  def __init__(self, expression):
    self.expression = expression
  def __str__(self):
    return f'{{Return {self.expression}}}'
  __repr__ = __str__

class Conditional:
  __slots__ = ('type', 'expression', 'body', 'else_body')
  def __init__(self, type, expression, body, else_body):
    self.type, self.expression, self.body, self.else_body = \
      type, expression, body, else_body
  def __str__(self):
    return f'{{Conditional {self.type} {self.expression} {self.body} {self.else_body}}}'
  __repr__ = __str__
class Parser:
  def parse(self, tokens):
    self.tokens = FutureIter(tokens)
    program = []
    while self.tokens.next is not None:
      if self.tokens.next.type != 'newline':
        program.append(self.parse_top())
      else:
        self.tokens._next()
    return program

  def parse_literal(self, tokens):
    return str(self.parse(tokens))

  def parse_to_console(self, tokens):
    program = self.parse(tokens)
    for expr in program:
      print(expr)

  def skip_newlines(self, count=-1):
    while self.tokens.next != None and self.tokens.next.type == 'newline' and count != 0:
      count -= 1
      self.tokens._next()
    return self.tokens.next
    
  def parse_top(self):
    init = self.tokens.next

    if init == None:
      return
    elif init.type != 'keyword':
      return self.parse_expr()
    elif init.text in TYPES or init.text == 'void':
      self.tokens._next()
      cur = self.tokens.next

      # We got an identifier?
      if cur.type == 'ident':
        self.tokens._next()
        nxt = self.tokens.next

        # Assignments
        if nxt.text == '=' and init.text != 'void':
          return self.parse_assignment(init.text, cur.text)
        
        # Function declarations
        elif nxt.text == '(':
          return self.parse_function(init.text, cur.text)
        
        # Function parameters
        elif nxt.text in (',', ')', ':'):
          if nxt.text == ':':
            self.tokens._next()
            default = self.parse_expr()
            return FunctionParameter(init.text, cur.text, default)
          return FunctionParameter(init.text, cur.text, None)
      
      # Keyword functions
      elif cur.text == '(' and init.text != 'void':
        return self.parse_call(init.text)
    
    # Returns
    elif init.text == 'return':
      return self.parse_return()
    
    # Conditionals
    elif init.text == 'if':
      return self.parse_conditional()
    
    else:
      raise Exception(f"Expected keyword, got '{init.text}' on line {init.line}")

  def parse_expr(self, precedence=0):
    self.skip_newlines()
    left = self.parse_primary()
    current = self.tokens.next

    while current and current.type == 'operator' and self.get_precedence(current.text) >= precedence:
      operator = current.text
      self.tokens._next()

      next_precedence = self.get_precedence(operator)
      if self.is_left_associative(operator):
        next_precedence += 1

      right = self.parse_expr(next_precedence)
      left = BinaryOperator(operator, left, right)

      current = self.tokens.next

    return left

  def parse_primary(self):
    current = self.tokens.next
    
    if current == None:
      raise Exception("Expected primary expression")
    
    elif self.is_unary_operator(current.text):
      operator = self.tokens._next().text
      value = self.parse_expr(self.get_precedence(operator))
      return UnaryOperator(operator, value)

    elif current.text == '(':
      self.tokens._next()
      value = self.parse_expr(0)
      if self.tokens._next().text is not ')':
        tk = self.tokens.next
        raise Exception(f"Expected ')', got '{tk.text}' on line {tk.line}")
      return value

    elif current.type == 'number':
      current = self.tokens._next()
      if current.text.count('.') > 0:
        return FloatingPointLiteral(float(current.text))
      return IntegerLiteral(int(current.text))

    elif current.type == 'string':
      return StringLiteral(self.tokens._next().text)

    elif current.type == 'ident':
      ident = self.tokens._next().text
      if self.tokens.next.text == '(':
        return self.parse_call(ident)
      elif self.tokens.next.text == '=':
        return self.parse_assignment(None, ident)
      else:
        return IdentLiteral(ident)

    raise Exception(f"Expected primary expression, got '{current.text}' on line {current.line}")

  def is_unary_operator(self, operator):
    return operator in ('-', '+', '++', '--', '!')

  def is_left_associative(self, operator):
    return operator not in ('++', '--', '+=', '-=', '=')

  def get_precedence(self, operator):
    if operator in ('+', '-'):
      return 1
    elif operator in ('*', '/', '%'):
      return 2
    else:
      return 0

  def parse_assignment(self, type, name):
    self.tokens._next()
    expr = self.parse_expr()
    return Assignment(type, IdentLiteral(name), expr)

  def parse_call(self, func_name):
    self.tokens._next()
    args = self.parse_args_params()
    return CallExpression(func_name, args)

  def parse_function(self, return_type, name):
    init = self.tokens._next()
    params = self.parse_args_params()
    body = self.parse_block()
    return Function(return_type, name, params, body)
  
  # Parse arguments and parameters
  # For both function calls and function definitions, respectively
  def parse_args_params(self):
    l = []
    while True:
      if self.tokens.next.text == ')':
        self.tokens._next()
        break
      l.append(self.parse_top())
      if self.tokens.next.text == ',':
        self.tokens._next()
      elif self.tokens._next().text == ')':
        break
      else:
        raise Exception(f"Expected ), got {self.tokens.next.text} on line {self.tokens.next.line}")

    return l

  # Return parsing
  def parse_return(self):
    self.tokens._next()
    expr = self.parse_expr()
    return Return(expr)

  # Conditional parsing
  def parse_conditional(self):
    init = self.tokens._next()

    # Parse else first because it is unlike if/elseif
    if init.text == 'else':
      return Conditional(init.text, None, self.parse_block(), None)
    
    body = []
    else_body = []
    cur = self.tokens.next
    if cur.text != '(':
      raise Exception(f"Expected '(', got '{cur.text}' on line {cur.line}")
    expr = self.parse_expr()
    body = self.parse_block()

    # If an else case is next
    self.skip_newlines()
    nxt = self.tokens.next
    if nxt and nxt.type == 'keyword' and nxt.text in ('elseif', 'else'):
      else_body.append(self.parse_conditional())

    return Conditional(init.text, expr, body, else_body)

  # Parse blocks for functions and conditionals
  def parse_block(self):
    body = []
    if self.tokens.next.text == '{':
      self.tokens._next()
      self.skip_newlines()
      while True:
        if self.tokens.next.text == '}':
          self.tokens._next()
          break
        body.append(self.parse_top())
        if self.tokens.next.type == 'newline':
          self.skip_newlines()
        elif self.tokens._next().text == '}':
          break
        else:
          raise Exception(f"Expected '}}', got {self.tokens.next.text} on line {self.tokens.next.line}")

    # One or two lined
    # ex: string say_hi() return print("Hi")
    else:
      # Skip only one line
      # If there is more space before an expression, you're doing it wrong kiddo
      self.skip_newlines(1)
      if self.tokens.next.type == 'newline':
        raise Exception(f"Empty function body on line {init.line}")
      body.append(self.parse_top())
    
    return body
