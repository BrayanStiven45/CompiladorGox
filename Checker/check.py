from rich    import print
from typing  import Union

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Parser.model   import *
from Parser.parser  import Parser
from Checker.symtab  import Symtab
from Checker.typesys import typenames, check_binop, check_unaryop


class Checker(Visitor):
	@classmethod
	def check(cls, n:Node):
		'''
		1. Crear una nueva tabla de simbolos
		2. Visitar todas las declaraciones
		'''
		check = cls()
		env = Symtab('global')
		try:
			n.accept(check, env)
		except Exception as e:
			print("Ocurrió un error en el Checker:", e)
			sys.exit(1)
			
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

		if not (n.alternative is None):
		
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
				type2 = env.get('func').type
				if type1 == type2:
					return True
				else:
					raise Exception(f'ReturnError: Linea {n.lineno}: El retorno debe coincidir con el tipo de retorno declarado en la función: {type1} != {type2}\n')
			
			env_apo = env_apo.parent
		
		raise Exception(f'ReturnError: Linea {n.lineno}: El retorno solo se puede usar dentro de una función \n')
		
	
	# Declarations

	def visit(self, n:Vardecl, env:Symtab):
		'''
		1. Agregar n.name a la TS actual
		'''

		if n.value is None:

			if n.kind == 'const':
				raise Exception('VarDeclError: Linea {n.lineno}: Se debe inicializar la variable constante')
			
		else:
			type2 = n.value.accept(self, env)
			if n.type != type2 and n.type != None:
				raise Exception(f'VarDeclError: Linea {n.lineno}: No se puede asignar el tipo \'{type2}\' a la variable \'{n.name}\' de tipo \'{n.type}\' \n')
		

			
		env.add(n.name, n)
	
	def function_has_return(self, stmts):
		"""
		Recorre una lista de sentencias y determina si se garantiza 
		la ejecución de un ReturnStmt en todos los caminos.
		"""
		guaranteed_return = False

		for stmt in stmts:
			# Si la sentencia es un retorno, ese camino asegura un return.
			if isinstance(stmt, ReturnStmt):
				return True

			# Si la sentencia es un IfStmt, revisamos ambos caminos.
			elif isinstance(stmt, IfStmt):
				# Verificar que en la parte "then" haya return.
				then_has_return = self.function_has_return(stmt.consequence)
				# Verificar que la rama "else" exista y tenga return.
				else_has_return = self.function_has_return(stmt.alternative) if stmt.alternative else False

				# Solo si ambos caminos retornan, ese if garantiza return.
				if then_has_return and else_has_return:
					guaranteed_return = True


		return guaranteed_return


	def visit(self, n:Funcdecl, env:Symtab):
		'''
		1. Guardar la función en la TS actual
		2. Crear una nueva TS para la función
		3. Agregar todos los n.params dentro de la TS
		4. Visitar n.stmts
		'''
		if env.name != 'global':
			raise Exception(f'FuncDeclError: Linea {n.lineno}: La función solo se puede declarar en el ámbito global \n')

		env.add(n.name, n)
		func_env = Symtab('funcSymbol',env)
		func_env.add('func', n)

		for p in n.parameters:
			func_env.add(p.name, p)
		
		for stmt in n.statements:
			stmt.accept(self, func_env)

		if not self.function_has_return(n.statements):
			raise Exception(f'FunctionError: Linea {n.lineno}: La función \'{n.name}\' no garantiza siempre retorno \n')


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

		check = check_unaryop(n.oper, type1) 

		if check is None:
			raise Exception(f'UnaryError: Linea {n.lineno}: Operación Unary incorrecto con tipo de dato \'{type1}\' \n')
		
		return check

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

if __name__ == '__main__':
	nodes = Parser('prueba.gox')

	ast = nodes.parse()

	check = Checker()
	_, env = check.check(ast)

	env.print()