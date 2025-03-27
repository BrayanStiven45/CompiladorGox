from typing import List
from dataclasses import dataclass
from model import ( 
	Assignment, Program, Statement, Location,
	BreakStmt, ContinueStmt, Binary, Literal,
	Unary, TypeConversion, FuncCall, Vardecl,
	Funcdecl, Parameter, Expression
)
import sys
import os

from rich import print

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Analizador_lexico.analizador_lexico import Token



# -------------------------------
# Implementación del Parser
# -------------------------------
class Parser:
	def __init__(self, tokens: List[Token]):
		self.tokens = tokens
		self.current = 0

	def parse(self) -> Program:
		statements = []
		while self.peek() and self.peek().type != "EOF":
			statements.append(self.statement())
		return Program(stmts = statements)

	# -------------------------------
	# Análisis de declaraciones
	# -------------------------------
	def statement(self) -> Statement:
		if self.match("ID") or self.match("BACKTICK"): #BACKTICK: '`'
			return self.assignment()
		elif self.match("VAR") or self.match("CONST"):
			return self.vardecl()
		elif self.match("FUNC"):
			return self.funcdecl()
		elif self.match("IF"):
			return self.if_stmt()
		elif self.match("WHILE"):
			return self.while_stmt()
		elif self.match("BREAK"):
			return BreakStmt()
		elif self.match("CONTINUE"):
			return ContinueStmt()
		elif self.match("RETURN"):
			return self.return_stmt()
		elif self.match("PRINT"):
			return self.print_stmt()
		else:
			print(self.tokens[self.current])
			raise SyntaxError(f"Línea {self.peek().lineno}: Declaración inesperada")
			
	def assignment(self) -> Assignment:
		location = None

		if self.previous().type == "ID":
			location = Location(self.previous().value)
		elif self.previous().type == "BACKTICK":
			location = Location(self.expression())
		
		self.consume("ASSIGN", "Se esperaba un signo igual '='")

		expr = self.expression()
		

		self.consume("SEMI", "Se esperaba un signo de punto y coma ';'")

		return Assignment(location, expr)
		
	def vardecl(self) -> Vardecl:
		
		kind = self.previous().value
		
		name = self.consume("ID", "Se esperaba un identificador").value
		type = None
		expr = None
		if self.match("INT") or self.match("FLOAT") or self.match("CHAR") or self.match("BOOL"): # Para type
			type = self.previous().value

		if self.match("ASSIGN"):
			expr = self.expression()
		
		self.consume("SEMI", "Se esperaba un punto y como ';'")

		return Vardecl(kind, type, name, expr)


	def funcdecl(self) -> Funcdecl:
		
		name = self.consume("ID", "Se esperaba un identificador").value
		self.consume("LPAREN", "Se esperaba un parentesis izquierdo '(' ")
		param = self.parameters()
		self.consume("RPAREN", "Se esperaba un parentesis derecho ')' ")
		return_type = self.advance().value
		self.consume("LBRACE", "Se esperaba una llave izquierda '{' ")
		stat = []
		while self.peek().type != "RBRACE":
			stat.append(self.statement())
		# stat = self.parse()
		self.consume("RBRACE", "Se esperaba una llave derecha '}' ")

		return Funcdecl(name, param, return_type, stat)
		
	def if_stmt(self):
		pass

	def while_stmt(self):
		pass
		
	def return_stmt(self):
		pass
		
	def print_stmt(self):
		pass
		
	# -------------------------------
	# Análisis de expresiones
	# -------------------------------
	def expression(self) -> Expression:
		
		expre = self.orterm()
		while self.match("OR"):
			right = self.orterm()
			expre = Binary("||", expre, right)
		return expre
		
	def orterm(self) -> Expression:
		
		orterm = self.andterm()
		while self.match("AND"):
			right = self.andterm()
			orterm = Binary("&&", orterm, right)
		return orterm

		
	def andterm(self) -> Expression:
		
		andterm = self.relterm()
		while self.match("NE") or self.match("EQ") or self.match("GE") or self.match("LE") or self.match("GT") or self.match("LT"):
			op = self.previous().value
			right = self.relterm()
			andterm = Binary(op, andterm, right)
		return andterm
		
	def relterm(self) -> Expression:
		
		relterm = self.addterm()
		while self.match("PLUS") or self.match("MINUS"):
			op = self.previous().value
			right = self.addterm()
			relterm = Binary(op, relterm, right)
		return relterm
		
	def addterm(self) -> Expression:
		
		addterm = self.factor()
		while self.match("DIVIDE") or self.match("TIMES"):
			op = self.previous().value
			right = self.factor()
			addterm = Binary(op, addterm, right)
		return addterm
		
	def binary_op(self, operators, next_rule):
		pass
		
	def factor(self) -> Expression:
		
		if self.match("INTEGER") or self.match("FLOAT") or self.match("CHAR") or self.match("TRUE") or self.match("FALSE"):
			return Literal(self.previous().value)
		elif self.match("PLUS") or self.match("MINUS") or self.match("GROW"):
			return Unary(self.previous().value, self.expression())
		elif self.match("LPAREN"):
			expr = self.expression()
			self.consume("RPAREN", "Se esperaba un parentesis derecho ')'")
			return expr
		elif self.match("INT") or self.match("FLOAT") or self.match("CHAR") or self.match("BOOL"): # Para type
			type = self.previous().value
			self.consume("LPAREN", "Se esperaba un parentesis izquierdo '('")
			expr = self.expression()
			self.consume("RPAREN", "Se esperaba un parentesis derecho ')'")
			return TypeConversion(type, expr)
		elif self.match("ID"):
			id = self.previous().value
			if self.tokens[self.current].type == "LPAREN":
				self.consume("LPAREN", "Se esperaba un perentesis izquierdo '('")
				args = self.arguments()
				self.consume("RPAREN", "Se esperaba un parentesis derecho ')'")
				return FuncCall(id, args)
			else:
				return Location(id)
		elif self.match("BACKTICK"):
			return Location(self.expression())
		else:
			raise SyntaxError(f"Línea {self.peek().lineno}: Factor inesperado")

			
	def parameters(self) -> List[Parameter]:

		params = []
		if self.peek() and self.peek().type == "ID":
            # Primer parámetro
			name = self.consume("ID", "Se esperaba un identificador para el parámetro").value
			type_str = self.consume("INT", "Se esperaba un tipo para el parámetro").value
			params.append(Parameter(name=name, type=type_str))
            # Parámetros adicionales separados por coma
			while self.match("COMMA"):
				name = self.consume("ID", "Se esperaba un identificador para el parámetro").value
				type_str = self.consume("INT", "Se esperaba un tipo para el parámetro").value
				params.append(Parameter(name=name, type=type_str))
		return params


	def arguments(self) -> List[Expression]:

		expr = [self.expression()]
		while self.match("COMMA"):
			expr.append(self.expression())
		
		return expr

	# # -------------------------------
	# # Analisis de Localizaciones
	# # -------------------------------
	# def location(self):
	# 	pass

	def previous(self) -> Token:
		return self.tokens[self.current - 1]

	# -------------------------------
	# Trate de conservar este codigo
	# -------------------------------

	def peek(self) -> Token:
		return self.tokens[self.current] if self.current < len(self.tokens) else None
		
	def advance(self) -> Token:
		token = self.peek()
		self.current += 1
		return token
		
	def match(self, token_type: str) -> bool:
		if self.peek() and self.peek().type == token_type:
			self.advance()
			return True
		return False
		
	def consume(self, token_type: str, message: str):
		if self.match(token_type):
			return self.previous()
		raise SyntaxError(f"Línea {self.peek().lineno}: {message}")
	
	
# -------------------------------
# Prueba del Parser con Tokens
# -------------------------------
tokens = [
    Token(type='FUNC', value='func', lineno=1),
    Token(type='ID', value='suma', lineno=1),
    Token(type='LPAREN', value='(', lineno=1),
    
    Token(type='ID', value='a', lineno=1),
    Token(type='INT', value='int', lineno=1),
    Token(type='COMMA', value=',', lineno=1),
    Token(type='ID', value='b', lineno=1),
    Token(type='INT', value='int', lineno=1),
    
    Token(type='RPAREN', value=')', lineno=1),
    Token(type='INT', value='int', lineno=1),
    Token(type='LBRACE', value='{', lineno=1),
    
    Token(type='ID', value='c', lineno=2),
	Token(type='ASSIGN', value='=', lineno=2),
    Token(type='ID', value='a', lineno=2),
    Token(type='PLUS', value='+', lineno=2),
    Token(type='ID', value='b', lineno=2),
    Token(type='SEMI', value=';', lineno=2),

	Token(type='ID', value='c', lineno=3),
	Token(type='ASSIGN', value='=', lineno=3),
    Token(type='ID', value='a', lineno=3),
    Token(type='PLUS', value='+', lineno=3),
    Token(type='ID', value='b', lineno=3),
    Token(type='SEMI', value=';', lineno=3),
    
    Token(type='RBRACE', value='}', lineno=4),
]

parser = Parser(tokens)
ast = parser.parse()

print(ast)

# Convertir el AST a una representación JSON para mejor visualización
import json

def ast_to_dict(node):
	if isinstance(node, list):
		return [ast_to_dict(item) for item in node]
	elif hasattr(node, "__dict__"):
		return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
	else:
		return node

ast_json = json.dumps(ast_to_dict(ast), indent=4)

# Guardar el AST como JSON
ast_file_path = "ast_updated.json"
with open(ast_file_path, "w", encoding="utf-8") as f:
	f.write(ast_json)

# Proporcionar el enlace de descarga
ast_file_path

