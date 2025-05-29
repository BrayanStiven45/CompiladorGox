# ircode.py
'''
Una Máquina Intermedia "Virtual"
================================
'''

from rich   import print
from typing import List, Union

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Checker.check  import Checker
from Parser.model import *
from Parser.parser import Parser

# Todo el código IR se empaquetará en un módulo. Un 
# módulo es un conjunto de funciones.

class IRModule:
	def __init__(self):
		self.functions = { }       # Dict de funciones IR 
		self.globals = { }         # Dict de variables global
		
	def dump(self):
		print("MODULE:::")
		for glob in self.globals.values():
			glob.dump()
			
		for func in self.functions.values():
			func.dump()
			
# Variables Globales
class IRGlobal:
	def __init__(self, name, type):
		self.name = name
		self.type = type
		
	def dump(self):
		print(f"GLOBAL::: {self.name}: {self.type}")

# Las funciones sirven como contenedor de las 
# instrucciones IR de bajo nivel específicas de cada
# función. También incluyen metadatos como el nombre 
# de la función, los parámetros y el tipo de retorno.

class IRFunction:
	def __init__(self, module, name, parmnames, parmtypes, return_type, imported=False):
		# Agreguemos la lista de funciones del módulo adjunto
		self.module = module
		module.functions[name] = self
		
		self.name = name
		self.parmnames = parmnames
		self.parmtypes = parmtypes
		self.return_type = return_type
		self.imported = imported
		self.locals = { }    # Variables Locales
		self.code = [ ]      # Lista de Instrucciones IR 
		
	def new_local(self, name, type):
		self.locals[name] = type
		
	def append(self, instr):
		self.code.append(instr)
		
	def extend(self, instructions):
		self.code.extend(instructions)
		
	def dump(self):
		print(f"FUNCTION::: {self.name}, {self.parmnames}, {self.parmtypes} {self.return_type}")
		print(f"locals: {self.locals}")
		for instr in self.code:
			print(instr)
			
# Mapeo de tipos de GoxLang a tipos de IR
_typemap = {
	'int'  : 'I',
	'float': 'F',
	'bool' : 'I',
	'char' : 'I',
}

# Generar un nombre de variable temporal único
def new_temp(n=[0]):
	n[0] += 1
	return f'$temp{n[0]}'

# Una función de nivel superior que comenzará a generar IRCode

class IRCode(Visitor):
	_binop_code = {
		('int', '+', 'int')  : 'ADDI',
		('int', '-', 'int')  : 'SUBI',
		('int', '*', 'int')  : 'MULI',
		('int', '/', 'int')  : 'DIVI',
		('int', '<', 'int')  : 'LTI',
		('int', '<=', 'int') : 'LEI',
		('int', '>', 'int')  : 'GTI',
		('int', '>=', 'int') : 'GEI',
		('int', '==', 'int') : 'EQI',
		('int', '!=', 'int') : 'NEI',
		
		('float', '+',  'float') : 'ADDF',
		('float', '-',  'float') : 'SUBF',
		('float', '*',  'float') : 'MULF',
		('float', '/',  'float') : 'DIVF',
		('float', '<',  'float') : 'LTF',
		('float', '<=', 'float') : 'LEF',
		('float', '>',  'float') : 'GTF',
		('float', '>=', 'float') : 'GEF',
		('float', '==', 'float') : 'EQF',
		('float', '!=', 'float') : 'NEF',
		
		('char', '<', 'char')  : 'LTI',
		('char', '<=', 'char') : 'LEI',
		('char', '>', 'char')  : 'GTI',
		('char', '>=', 'char') : 'GEI',
		('char', '==', 'char') : 'EQI',
		('char', '!=', 'char') : 'NEI',
	}
	_unaryop_code = {
		('+', 'int')   : [],
		('+', 'float') : [],
		('-', 'int')   : [('CONSTI', -1), ('MULI',)],
		('-', 'float') : [('CONSTF', -1.0), ('MULF',)],
		('!', 'bool')  : [('CONSTI', -1), ('MULI',)],
		('^', 'int')   : [ ('GROW',) ]
	}
	_typecast_code = {
		# (from, to) : [ ops ]
		('int', 'float') : [ ('ITOF',) ],
		('float', 'int') : [ ('FTOI',) ],
	}

	@classmethod
	def gencode(cls, node:Program):
		'''
		El nodo es el nodo superior del árbol de 
		modelo/análisis.
		La función inicial se llama "_init". No acepta 
		argumentos. Devuelve un entero.
		'''
		ircode = cls()
		
		module = IRModule()
		func = IRFunction(module, 'main', [], [], 'I')
		for item in node.stmts:
			item.accept(ircode, func)
		if '_actual_main' in module.functions:
			func.append(('CALL', '_actual_main'))
		else:
			func.append(('CONSTI', 0))
		func.append(('RET',))
		return module
	
	# --- Statements

	def visit(self, n:PrintStmt, func:IRFunction):
		n.expr.accept(self, func)


		if n.type == 'int':
			func.append(('PRINTI',))
		elif n.type == 'float':
			func.append(('PRINTF',))
		elif (n.type == 'char') or (n.type == 'bool'):
			func.append(('PRINTB',))
		else:
			raise Exception(f'Error en la linea {n.lineno} en PrintStmt de codigo intermedio')
	
	def visit(self, n:Assignment, func:IRFunction):
		
		n.expr.accept(self, func)

		n.location.accept(self, func)



	def visit(self, n:IfStmt, func:IRFunction):
		
		n.condition.accept(self, func)

		func.append(('IF',))

		for item in n.consequence:
			item.accept(self, func)

		func.append(('ELSE',))

		if n.alternative != None:
			for item in n.alternative:
				item.accept(self, func)
		
		func.append(('ENDIF',))

	def visit(self, n:WhileStmt, func:IRFunction):
		func.extend([('LOOP',), ('CONSTI', 1)])

		n.condition.accept(self, func)

		func.extend([('SUBI',), ('CBREAK',)])

		for item in n.body:
			item.accept(self, func)

		func.append(('ENDLOOP',))

	def visit(self, n:BreakStmt, func:IRFunction):

		func.append(('CONSTI', 1))
		func.append(('CBREAK',))

	def visit(self, n:ContinueStmt, func:IRFunction):
		
		func.append(('CONTINUE',))

	def visit(self, n:ReturnStmt, func:IRFunction):
		n.expr.accept(self, func)

		func.append(('RET',))

	# --- Declaration
		
	def visit(self, n:Vardecl, func:IRFunction):

		if n.value != None:
			n.value.accept(self, func)

		if n.kind == 'const':
			n.type = n.value.type

		if func.name == 'main':
			# print(f'Esto es n {n}')
			var_global = IRGlobal(n.name, _typemap[n.type])
			func.module.globals[n.name] = var_global

			if n.value != None:
				func.append(('GLOBAL_SET', n.name))
		else:
			func.new_local(n.name, _typemap[n.type])

			if n.value != None:
				func.append(('LOCAL_SET', n.name))

		
	def visit(self, n:Funcdecl, func:IRFunction):
		parmnames = [p.name for p in n.parameters]
		parmtypes = [_typemap[p.type] for p in n.parameters]
		rettype = _typemap[n.type]

		if n.name == 'main':
			name = '_actual_main'
		else:
			name = n.name

		new_func = IRFunction(func.module, name, parmnames, parmtypes, rettype, n.is_import)
		
		if not n.is_import:
			for item in n.statements:
				item.accept(self, new_func)

	# --- Expressions

	def visit(self, n:Literal, func: IRFunction):
		value = None
		if n.type == 'int':
			func.append(('CONSTI', int(n.value)))
		elif n.type == 'float':
			func.append(('CONSTF', float(n.value)))
		elif n.type == 'char':
			value = eval(n.value) if isinstance(n.value, str) else n.value

			func.append(('CONSTI', ord(value)))
		elif n.type == 'bool':
			value = eval(n.value.capitalize()) #Para que python lo detecte como False o True y lo conviarta a 1 o 0
			func.append(('CONSTI', int(value)))
		else:
			raise Exception(f'Error en la linea {n.lineno} en Literal de codigo intermedio')

		return n.type
			


	def visit(self, n:Binary, func:IRFunction):
		
		
		if n.op == '&&':
			# Validar el circuito corto: A && B, si A es falso => no necesita evaluar B
			n.left.accept(self, func)
			func.append(('IF,',))
			n.right.accept(self, func)
			func.append(('ELSE',))
			func.append(('CONSTI', 0))
			func.append(('ENDIF',))

		elif n.op == '||':
			n.left.accept(self, func)
			func.append(('IF,',))
			func.append(('CONSTI', 1))
			func.append(('ELSE',))
			n.right.accept(self, func)
			func.append(('ENDIF',))
		else:
			n.left.accept(self, func)
			n.right.accept(self, func)
			# print(f'esto es n de Binary {n}')
			func.append((self._binop_code[n.left.type, n.op, n.right.type],))
		
	def visit(self, n:Unary, func:IRFunction):
		n.expr.accept(self, func)

		instructions = self._unaryop_code[n.op, n.type]
		func.extend(instructions)

		
	def visit(self, n:TypeConversion, func:IRFunction):
		# Preguntar si esta bien-------__----------------

		n.expr.accept(self, func)

		if isinstance(n.expr, LocationMem):
			return

		if (n.type != n.expr.type): # Preguntar para estos casos
			func.extend(self._typecast_code[n.expr.type, n.type])
		else:
			raise Exception(f'Error en la linea {n.lineno} en TypeConvertion de codigo intermedio')


	def visit(self, n:FuncCall, func:IRFunction):
		
		for item in n.arg:
			item.accept(self, func)

		func.append(('CALL', n.name))
	
	# def visit(self, n:NamedLocation, func:IRFunction):
	# 	# Revisar si la variable es para store
	# 	func.append(('LOCAL_SET', n.name)) / func.append(('GLOBAL_SET', n.name))
	# 	# else
	# 	func.append(('LOCAL_GET', n.name)) / func.append(('GLOBAL_GET', n.name))

	def visit(self, n:LocationPrimi, func:IRFunction):
		env = None

		if n.name in func.parmnames or n.name in func.locals:
			env = 'LOCAL'
		else:
			# print(f'entro aqui n {n}')
			env = 'GLOBAL'		
		
		op = None
		if n.usage == 'load':
			op = env + '_GET'
		elif n.usage == 'store':
			op = env + '_SET'

		func.append((op, n.name))
			

	def visit(self, n:LocationMem, func:IRFunction):
		if n.usage == 'load':
			n.expr.accept(self, func)
			if n.type in {'int', 'bool'}:
				func.append(('PEEKI',))
			elif n.type == 'float':
				func.append(('PEEKF',))
			elif n.type == 'char':
				func.append(('PEEKB',))
		elif n.usage == 'store':
			index_expr_store = len(func.code)
			n.expr.accept(self, func)

			expr_store = func.code.pop(index_expr_store-1)

			func.append(expr_store)
			
			if n.type in {'int', 'bool'}:
				func.append(('POKEI',))
			elif n.type == 'float':
				func.append(('POKEF',))
			elif n.type == 'char':
				func.append(('POKEB',))



if __name__ == '__main__':
	import sys

	# if len(sys.argv) != 2:
	# 	raise SystemExit("Usage: python ircode.py <filename>")
	parse = Parser('prueba.gox')
	
	ast = parse.parse()
	print(ast)

	check = Checker()
	_, env = check.check(ast)
		
	module = IRCode.gencode(ast)
	module.dump()
