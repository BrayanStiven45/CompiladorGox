# check.py
'''
Este archivo contendrá la parte de verificación/validación de tipos
del compilador.  Hay varios aspectos que deben gestionarse para
que esto funcione. Primero, debe tener una noción de "tipo" en su compilador.
Segundo, debe administrar los entornos y el alcance para manejar los
nombres de las definiciones (variables, funciones, etc.).

Una clave para esta parte del proyecto es realizar pruebas adecuadas.
A medida que agregue código, piense en cómo podría probarlo.
'''
from rich    import print
from typing  import Union

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Parser.model   import *
from Parser.parser  import Parser
from symtab  import Symtab
from typesys import typenames, check_binop, check_unaryop


class Checker(Visitor):
	@classmethod
	def check(cls, n:Node):
		'''
		1. Crear una nueva tabla de simbolos
		2. Visitar todas las declaraciones
		'''
		check = cls()
		env = Symtab('global')
		n.accept(check, env)
		return check, env


	def visit(self, n:Program, env:Symtab):
		'''
		1. recorrer la lista de elementos
		'''
		for stmt in n.stmts:
			stmt.accept(self, env)

	# Statements

	def visit(self, n:Assignment, env:Symtab):
		'''
		1. Validar n.loc
		2. Visitar n.expr
		3. Verificar si son tipos compatibles
		'''

		if isinstance(n.location, LocationPrimi):
			symbol = env.get(n.location.name)
			if isinstance(symbol, Vardecl):
				# Si la variable es un constante, entonces no se puede assignar un valor
				if symbol.kind == 'const':
					raise Exception(f"AssignmentError: Linea {n.lineno}: No se puede asignar un valor a una constante '{n.location.name}' \n")

		# Si location es una asignación a memoria	
		if isinstance(n.location, LocationMem):
			return True

		type1 = n.location.accept(self, env)	

		
		type2 = n.expression.accept(self, env)

		# # Si la variable esta declarad pero no fue declaracada con 
		# # un tipo de dato
		# if type1.type is None: 
		# 	type1.type = type2
		# 	env.modify_table(name_loc, type1)
		

		# Si los tipos de datos de la variable y de la expresion no son iguales
		# entonces arroja un exepción
		
		# if check_binop('=', type1, type2) is None:
		# 	raise Exception(f'Error: No se puede asignar el tipo {type2} a la variable \'{name_loc}\' de tipo {type1} \n')	
		
		if type2 in typenames and type2 == type1:
			return True

		raise Exception(f'AssigmentError: Linea {n.lineno}: No se puede asignar el tipo \'{type2}\' a la variable de tipo \'{type1}\' \n')	


	def visit(self, n:PrintStmt, env:Symtab):
		'''
		1. visitar n.expr
		'''
		n.expression.accept(self, env)


	def visit(self, n:IfStmt, env:Symtab):
		'''
		1. Visitar n.test (validar tipos)
		2. Visitar Stament por n.then
		3. Si existe opcion n.else_, visitar
		'''
		if n.condition.accept(self, env) != 'bool':
			raise Exception(f'IfError: Linea {n.lineno}: La condición debe ser de tipo \'bool\' \n')

		if_env = Symtab("ifSymbol", env)

		for cons in n.consequence:
			cons.accept(self, if_env)
		
		else_env = Symtab('elseSymbol', env)

		for alt in n.alternative:
			alt.accept(self, else_env)

			
	def visit(self, n:WhileStmt, env:Symtab):
		'''
		1. Visitar n.test (validar tipos)
		2. visitar n.body
		'''
		if n.condition.accept(self, env) != 'bool':
			raise Exception(f'WhileError: Linea {n.lineno}: La condición debe ser de tipo \'bool\' \n')
		
		while_env = Symtab('loopSymbol', env)

		for body in n.body:
			body.accept(self, while_env)

		
	def visit(self, n:Union[BreakStmt, ContinueStmt], env:Symtab):
		'''
		1. Verificar que esta dentro de un ciclo while
		'''
		while env.name != 'global':
			if env.name == 'loopSymbol':
				return True
			
			env = env.parent

		raise Exception(f'Error: Linea {n.lineno}: Solo se puede usar en un ciclo') 
	
	def visit(self, n:ReturnStmt, env:Symtab):
		'''
		1. Si se ha definido n.expr, validar que sea del mismo tipo de la función
		'''
		env_apo = env
		while env_apo.name != 'global':
			if env_apo.name == 'funcSymbol':
				type1 = n.expression.accept(self, env)
				if type1 == env.get('func').type:
					return True
				else:
					raise Exception(f'ReturnError: Linea {n.lineno}: El retorno debe coincidir con el tipo de retorno declarado en la función')
			
			env_apo = env_apo.parent
		
		raise Exception(f'ReturnError: Linea {n.lineno}: El retorno solo se puede usar dentro de una función')
		
	
	# Declarations

	def visit(self, n:Vardecl, env:Symtab):
		'''
		1. Agregar n.name a la TS actual
		'''
		# # Si el tipo de variable no fue definido, 
		# # se asigna el tipo de la expresion
		# if n.type is None:
		# 	if not (n.value is None):
		# 		n.type = n.value.type

		if n.value is None:

			if n.kind == 'const':
				raise Exception('VarDeclError: Linea {n.lineno}: Se debe inicializar la variable constante')
			
		else:
			type2 = n.value.accept(self, env)
			if n.type != type2 and n.type != None:
				raise Exception(f'VarDeclError: Linea {n.lineno}: No se puede asignar el tipo \'{type2}\' a la variable \'{n.name}\' de tipo \'{n.type}\' \n')
		

			
		env.add(n.name, n)
		

	def visit(self, n:Funcdecl, env:Symtab):
		'''
		1. Guardar la función en la TS actual
		2. Crear una nueva TS para la función
		3. Agregar todos los n.params dentro de la TS
		4. Visitar n.stmts
		'''
		env.add(n.name, n)
		func_env = Symtab('funcSymbol',env)
		func_env.add('func', n)

		for p in n.parameters:
			func_env.add(p.name, p)
		
		for stmt in n.statements:
			stmt.accept(self, func_env)

	def visit(self, n:Parameter, env:Symtab):
		'''
		1. Guardar el parametro (name, type) en TS
		'''
		return n.type
		
	# Expressions

	def visit(self, n:Literal, env:Symtab):
		'''
		1. Retornar el tipo de la literal
		'''
		return n.type

	def visit(self, n:Binary, env:Symtab):
		'''
		1. visitar n.left y luego n.right
		2. Verificar compatibilidad de tipos
		'''
		type1 = n.left.accept(self, env)
		type2 = n.right.accept(self, env)

		if type1 != type2:
			raise Exception(f'BinaryError: Linea {n.lineno}: No se puede hacer una operacion \'{n.op}\' entre \'{type1}\' y \'{type2}\' \n')
		
		return check_binop(n.op, type1, type2)
		
	def visit(self, n:Unary, env:Symtab):
		'''
		1. visitar n.expr
		2. validar si es un operador unario valido
		'''
		type1 = n.expression.accept(self, env)
		return check_unaryop(n.oper, type1)

	def visit(self, n:TypeConversion, env:Symtab):
		'''
		1. Visitar n.expr para validar
		2. retornar el tipo del cast n.type
		'''
		type_expr = n.exp.accept(self, env)
		type_conv = n.type

		if type_conv == 'char':
			return type_conv
		
		if type_expr == 'char':
			raise Exception(f'TypeConvertionError: Linea {n.lineno}: No se puede convertir un tipo \'char\' a tipo \'{type_conv}\' \n')
		
		#Preguntar para booleanos

		return type_conv



	def visit(self, n:FuncCall, env:Symtab):
		'''
		1. Validar si n.name existe
		2. visitar n.args (si estan definidos)
		3. verificar que len(n.args) == len(func.params)
		4. verificar que cada arg sea compatible con cada param de la función
		'''


		func = env.get(n.name)

		if func is None:
			raise Exception(f'FunCallError: Linea {n.lineno}: La funcion \'{n.name}\' no esta definida')

		for arg in n.arg:
			arg.accept(self, env)

		num_arg = len(n.arg)
		num_param = len(func.parameters)
		if num_arg != num_param:
			raise Exception(f'FunCallError: Linea {n.lineno}: Numero de argumentos \'{num_arg}\' no concuerdan con el numero de parametros \'{num_param}\' de la funcion \'{func.name}\'')
		
		params = func.parameters
		args = n.arg
		for i in range(num_arg):
			if params[i].accept(self, env) != args[i].accept(self, env):
				raise Exception(f'FunCallError: Linea {n.lineno}: Tipo de dato no coinciden')
		
		return func.type


	def visit(self, n:LocationPrimi, env:Symtab):
		'''
		1. Verificar si n.name existe en TS y obtener el tipo
		2. Retornar el tipo
		'''
		name_loc = n.name
		type1 = env.get(name_loc) # Nombre de la variable a la que se le asigna

		if type1 is None:
			raise NameError(f'Linea {n.lineno}: La variable \'{name_loc}\' no existe \n')
		
		if type1.type is None:
			type1.type = type1.value.accept(self, env)
		

		return type1.type

	def visit(self, n:LocationMem, env:Symtab):
		'''
		1. Visitar n.address (expression) para validar
		2. Retornar el tipo de datos
		'''
		type = n.expr.accept(self, env)

		return type

nodes = Parser('prueba.gox')

ast = nodes.parse()
print(ast)

check = Checker()
_, env = check.check(ast)

env.print()