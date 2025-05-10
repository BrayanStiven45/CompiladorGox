from dataclasses import dataclass, field
from multimethod import multimeta
from typing      import List, Union

class Visitor(metaclass=multimeta):
  pass

@dataclass(kw_only=True)
class Node:
  lineno : int = None
  type : str = None

  def accept(self, v:Visitor, env):
    return v.visit(self, env)
  

@dataclass
class Statement(Node):
  pass

@dataclass
class Program(Statement):
    stmts: List[Statement] = field(default_factory=list)

@dataclass
class Expression(Node):
  pass

@dataclass
class Location(Node):
  pass

# Para tipo '`'
@dataclass
class LocationMem(Location):
  expr: Expression
  usage : str = None

# Para tipo 'ID'
@dataclass
class LocationPrimi(Location):
  name: str
  usage : str = None
# 1.1 Assignment
#
#     location = expression ;
@dataclass
class Assignment(Statement):
  location : Location
  expr : Expression

#
# 1.2 Printing
#     print expression ;
@dataclass
class PrintStmt(Statement):
  expr: Expression

# 1.3 Conditional
#     if test { consequence } else { alternative }
@dataclass
class IfStmt(Statement):
  condition: Expression
  consequence: List[Statement]
  alternative: List[Statement] = None

# 1.4 While Loop
#     while test { body }
@dataclass
class WhileStmt(Statement):
  condition: Expression
  body: Statement

# 1.5 Break y Continue
#     while test {
#         ...
#         break;   // continue
#     }
@dataclass
class BreakStmt(Statement):
  pass

# 1.5 Break y Continue
#     while test {
#         ...
#         break;   // continue
#     }
@dataclass
class ContinueStmt(Statement):
  pass

# 1.6 Return un valor
#     return expresion ;
@dataclass
class ReturnStmt(Statement):
  expr: Expression

# 2.1 Variables.  Las Variables pueden ser declaradas de varias formas.
#
#     const name = value;
#     const name [type] = value;
#     var name type [= value];
#     var name [type] = value;

#Todos los campos con valor por defecto deben ser pasados por nombre (keyword)
@dataclass(kw_only=True) 
class Vardecl(Statement):
  kind: str
  type: str
  name: str
  value: Expression = None

# 2.3 Function Parameters
#
#     func square(x int) int { return x*x; }
@dataclass(kw_only=True)
class Parameter(Node):
  name: str
  type: str
  # value: Expression = None

# 2.2 Function definitions.
#
#     func name(parameters) return_type { statements }
@dataclass
class Funcdecl(Statement):
  is_import: bool
  name: str
  parameters: List[Parameter]
  statements: List[Statement] #Esto debe ser o una lista de statements o un none

# Observar bien esta clase como debe de ser y a quien debe de heredar
# dataclass
# class Import(Statement):
#   pass


# 3.1 Literals
#     23           (Entero)
#     4.5          (Flotante)
#     true,false   (Booleanos)
#     'c'          (Carácter)
@dataclass(kw_only=True)
class Literal(Expression):
  value: str
  type: str

# 3.2 Binary Operators
#     left + right   (Suma)
#     left - right   (Resta)
#     left * right   (Multiplicación)
#     left / right   (División)
#     left < right   (Menor que)
#     left <= right  (Menor o igual que)
#     left > right   (Mayor que)
#     left >= right  (Mayor o igual que)
#     left == right  (Igual a)
#     left != right  (Diferente de)
#     left && right  (Y lógico)
#     left || right  (O lógico)

@dataclass
class Binary(Expression):
  op: str
  left: Expression
  right: Expression

# 3.3 Unary Operators
#     +operand  (Positivo)
#     -operand  (Negación)
#     !operand  (Negación lógica)
#     ^operand  (Expandir memoria)

@dataclass
class Unary(Expression):
  op: str
  expr: Expression


# 3.5 Conversiones de tipo
#     int(expr)
#     float(expr)
@dataclass(kw_only=True)
class TypeConversion(Expression):
  type: str
  expr : Expression

# 3.6 Llamadas a función
#     func(arg1, arg2, ..., argn)
@dataclass
class FuncCall(Expression):
  name: str
  arg: List[Expression]

# #Para tipo 'ID'
# @dataclass
# class LocationPrimi(Location):
#   name: str

# #Para tipo '`'
# @dataclass
# class LocationMem(Location):
#   expr: Expression
