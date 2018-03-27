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

class Parser:
  def __init__(self, tokens):
    self.tokens = FutureIter(tokens)

  def skip_newlines(self):
    while self.tokens.next != None and self.tokens.next.type == 'newline':
      self.tokens._next()
    return self.tokens.next
  
  def parse_literal(self):
    return str(self.parse())

  def parse_to_console(self):
    program = self.parse()
    for expr in program:
      print(expr)

  def parse(self):
    program = []
    while self.tokens.next is not None:
      if self.tokens.next.type != 'newline':
        program.append(self.parse_top())
      else:
        self.tokens._next()
    return program
    
  def parse_top(self):
    init = self.tokens.next

    if init == None:
      return
    elif init.type != 'keyword':
      return self.parse_expr()
    else:
      if init.text in TYPES or init.text == 'void':
        self.tokens._next()
        cur = self.tokens.next

        # Assignment / declaration
        if cur.type == 'ident':
          self.tokens._next()
          nxt = self.tokens.next

          # Assignment
          if nxt.text == '=' and init.text != 'void':
            return self.parse_assignment(init.text, cur.text)
          
          # Function declaration
          elif nxt.text == '(':
            return self.parse_function(init.text, cur.text)
          
          # Function parameter
          elif nxt.text in (',', ')', ':'):
            if nxt.text == ':':
              self.tokens._next()
              default = self.parse_expr()
              return FunctionParameter(init.text, cur.text, default)
            return FunctionParameter(init.text, cur.text, None)
        
        # Keyword functions
        elif cur.text == '(' and init.text != 'void':
          return self.parse_call(init.text)

      elif init.text == 'return':
        return self.parse_return()
      else:
        self.tokens._next()
        cur = self.tokens.next

        if cur.text == 'if':
          return self.parse_conditional()

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
        raise Exception("Expected )")
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
    args = []
    while True:
      args.append(self.parse_top())
      if self.tokens.next.text == ',':
        self.tokens._next()
      elif self.tokens._next().text == ')':
        break
      else:
        raise Exception("Expected )")
    return CallExpression(func_name, args)

  def parse_function(self, return_type, name):
    init = self.tokens._next()
    params = []
    body = []

    # Parameters
    while True:
      params.append(self.parse_top())
      if self.tokens.next.text == ',':
        self.tokens._next()
      elif self.tokens._next().text == ')':
        break
      else:
        raise Exception(f"Expected ) on line {self.tokens.next.line}")

    # Function body
    if self.tokens.next.text == '{':
      self.tokens._next()
      while True:
        self.skip_newlines()
        body.append(self.parse_top())
        self.skip_newlines()
        if self.tokens._next().text == '}':
          break
        else:
          raise Exception(f"Expected }} on line {self.tokens.next.line}")
    
    # Single line functions
    else:
      body.append(self.parse_top())
    
    return Function(return_type, name, params, body)

  def parse_return(self):
    self.tokens._next()
    expr = self.parse_expr()
    return Return(expr)

  # TODO conditional parsing
  def parse_conditional(self):
    init = self.tokens._next()
    cur = self.tokens.next
    
    if cur.text != '(':
      raise Exception(f"Expected ( on line {init.line}.")
    else:
      print('hi')
