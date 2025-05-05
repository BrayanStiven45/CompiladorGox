# ircode.py
'''
Una Máquina Intermedia "Virtual"
================================

Una CPU real generalmente consta de registros y un pequeño conjunto de
códigos de operación básicos para realizar cálculos matemáticos,
cargar/almacenar valores desde memoria y controlar el flujo básico
(ramas, saltos, etc.). Aunque puedes hacer que un compilador genere
instrucciones directamente para una CPU, a menudo es más sencillo
dirigirse a un nivel de abstracción más alto. Una de esas abstracciones
es la de una máquina de pila (stack machine).

Por ejemplo, supongamos que deseas evaluar una operación como esta:

    a = 2 + 3 * 4 - 5

Para evaluar la expresión anterior, podrías generar pseudo-instrucciones
como esta:

    CONSTI 2      ; stack = [2]
    CONSTI 3      ; stack = [2, 3]
    CONSTI 4      ; stack = [2, 3, 4]
    MULI          ; stack = [2, 12]
    ADDI          ; stack = [14]
    CONSTI 5      ; stack = [14, 5]
    SUBI          ; stack = [9]
    LOCAL_SET "a" ; stack = []

Observa que no hay detalles sobre registros de CPU ni nada por el estilo
aquí. Es mucho más simple (un módulo de nivel inferior puede encargarse
del mapeo al hardware más adelante si es necesario).

Las CPUs usualmente tienen un pequeño conjunto de tipos de datos como
enteros y flotantes. Existen instrucciones dedicadas para cada tipo. El
código IR seguirá el mismo principio, admitiendo operaciones con enteros
y flotantes. Por ejemplo:

    ADDI   ; Suma entera
    ADDF   ; Suma flotante

Aunque el lenguaje de entrada podría tener otros tipos como `bool` y
`char`, esos tipos deben ser mapeados a enteros o flotantes. Por ejemplo,
un bool puede representarse como un entero con valores {0, 1}. Un char
puede representarse como un entero cuyo valor sea el mismo que el código
del carácter (es decir, un código ASCII o código Unicode).

Con eso en mente, aquí hay un conjunto básico de instrucciones para
nuestro Código IR:

    ; Operaciones enteras
    CONSTI value             ; Apilar un literal entero
    ADDI                     ; Sumar los dos elementos superiores de la pila
    SUBI                     ; Restar los dos elementos superiores de la pila
    MULI                     ; Multiplicar los dos elementos superiores de la pila
    DIVI                     ; Dividir los dos elementos superiores de la pila
    ANDI                     ; AND bit a bit
    ORI                      ; OR bit a bit
    LTI                      : <
    LEI                      : <=
    GTI                      : >
    GEI                      : >=
    EQI                      : ==
    NEI                      : !=
    PRINTI                   ; Imprimir el elemento superior de la pila
    PEEKI                    ; Leer entero desde memoria (dirección en la pila)
    POKEI                    ; Escribir entero en memoria (valor, dirección en la pila)
    ITOF                     ; Convertir entero a flotante

    ; Operaciones en punto flotante
    CONSTF value             ; Apilar un literal flotante
    ADDF                     ; Sumar los dos elementos superiores de la pila
    SUBF                     ; Restar los dos elementos superiores de la pila
    MULF                     ; Multiplicar los dos elementos superiores de la pila
    DIVF                     ; Dividir los dos elementos superiores de la pila
    LTF                      : <
    LEF                      : <=
    GTF                      : >
    GEF                      : >=
    EQF                      : ==
    NEF                      : !=
    PRINTF                   ; Imprimir el elemento superior de la pila
    PEEKF                    ; Leer flotante desde memoria (dirección en la pila)
    POKEF                    ; Escribir flotante en memoria (valor, dirección en la pila)
    FTOI                     ; Convertir flotante a entero

    ; Operaciones orientadas a bytes (los valores se presentan como enteros)
    PRINTB                   ; Imprimir el elemento superior de la pila
    PEEKB                    ; Leer byte desde memoria (dirección en la pila)
    POKEB                    ; Escribir byte en memoria (valor, dirección en la pila)

    ; Carga/almacenamiento de variables.
    ; Estas instrucciones leen/escriben variables locales y globales. Las variables
    ; son referenciadas por algún tipo de nombre que las identifica. La gestión
    ; y declaración de estos nombres también debe ser manejada por tu generador de código.
    ; Sin embargo, las declaraciones de variables no son una instrucción normal. En cambio,
    ; es un tipo de dato que debe asociarse con un módulo o función.
    LOCAL_GET name           ; Leer una variable local a la pila
    LOCAL_SET name           ; Guardar una variable local desde la pila
    GLOBAL_GET name          ; Leer una variable global a la pila
    GLOBAL_SET name          ; Guardar una variable global desde la pila

    ; Llamadas y retorno de funciones.
    ; Las funciones se referencian por nombre. Tu generador de código deberá
    ; encontrar alguna manera de gestionar esos nombres.
    CALL name                ; Llamar función. Todos los argumentos deben estar en la pila
    RET                      ; Retornar de una función. El valor debe estar en la pila

    ; Control estructurado de flujo
    IF                       ; Comienza la parte "consecuencia" de un "if". Prueba en la pila
    ELSE                     ; Comienza la parte "alternativa" de un "if"
    ENDIF                    ; Fin de una instrucción "if"

    LOOP                     ; Inicio de un ciclo
    CBREAK                   ; Ruptura condicional. Prueba en la pila
    CONTINUE                 ; Regresa al inicio del ciclo
    ENDLOOP                  ; Fin del ciclo

    ; Memoria
    GROW                     ; Incrementar memoria (tamaño en la pila) (retorna nuevo tamaño)

Una palabra sobre el acceso a memoria... las instrucciones PEEK y POKE
se usan para acceder a direcciones de memoria cruda. Ambas instrucciones
requieren que una dirección de memoria esté en la pila *primero*. Para
la instrucción POKE, el valor a almacenar se apila después de la dirección.
El orden es importante y es fácil equivocarse. Así que presta mucha
atención a eso.

Su tarea
=========
Su tarea es la siguiente: Escribe código que recorra la estructura del
programa y la aplane a una secuencia de instrucciones representadas como
tuplas de la forma:

       (operation, operands, ...)

Por ejemplo, el código del principio podría terminar viéndose así:

    code = [
       ('CONSTI', 2),
       ('CONSTI', 3),
       ('CONSTI', 4),
       ('MULI',),
       ('ADDI',),
       ('CONSTI', 5),
       ('SUBI',),
       ('LOCAL_SET', 'a'),
    ]

Funciones
=========
Todo el código generado está asociado con algún tipo de función. Por
ejemplo, con una función definida por el usuario como esta:

    func fact(n int) int {
        var result int = 1;
        var x int = 1;
        while x <= n {
            result = result * x;
            x = x + 1;
        }
     }

Debes crear un objeto `Function` que contenga el nombre de la función,
los argumentos, el tipo de retorno, las variables locales y un cuerpo
que contenga todas las instrucciones de bajo nivel. Nota: en este nivel,
los tipos representarán tipos IR de bajo nivel como Integer (I) y Float (F).
No son los mismos tipos usados en el código GoxLang de alto nivel.

Además, todo el código que se define *fuera* de una función debe ir
igualmente en una función llamada `_init()`. Por ejemplo, si tienes
declaraciones globales como esta:

     const pi = 3.14159;
     const r = 2.0;
     print pi*r*r;

Tu generador de código debería en realidad tratarlas así:

     func _init() int {
         const pi = 3.14159;
         const r = 2.0;
         print pi*r*r;
         return 0;
     }

En resumen: todo el código debe ir dentro de una función.

Módulos
=======
La salida final de la generación de código debe ser algún tipo de
objeto `Module` que contenga todo. El módulo incluye objetos de función,
variables globales y cualquier otra cosa que puedas necesitar para
generar código posteriormente.
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
		n.expression.accept(self, func)

		func.append(('PRINTI',))
	
	def visit(self, n:Assignment, func:IRFunction):
		pass

	def visit(self, n:IfStmt, func:IRFunction):
		pass

	def visit(self, n:WhileStmt, func:IRFunction):
		pass

	def visit(self, n:BreakStmt, func:IRFunction):
		pass

	def visit(self, n:ContinueStmt, func:IRFunction):
		pass

	def visit(self, n:ReturnStmt, func:IRFunction):
		pass

	# --- Declaration
		
	def visit(self, n:Vardecl, func:IRFunction):

		var_type = None

		if n.kind == 'const':
			var_type = n.value.accept(self, func)
		else:
			var_type = n.type
			

		if func.name == 'main':
			var_global = IRGlobal(n.name, var_type)
			func.module.globals[n.name] = var_global

			if n.value != None:
				func.append(('GLOBAL_SET', n.name))
		else:
			func.new_local(n.name, var_type)

			if n.value != None:
				func.append(('LOCAL_SET', n.name))

		
	def visit(self, n:Funcdecl, func:IRFunction):
		pass
		
	# --- Expressions

	def visit(self, n:Literal, func: IRFunction):
		value = None
		if n.type == 'int':
			func.append(('CONSTI', n.value))
		elif n.type == 'float':
			func.append(('CONSTF', n.value))
		elif n.type == 'char':
			func.append(('CONSTI', ord(n.value[1])))
		elif n.type == 'bool':
			value = eval(n.value.capitalize()) #Para que python lo detecte como False o True y lo conviarta a 1 o 0
			func.append(('CONSTI', int(value)))
		else:
			raise Exception(f'Error en la linea {n.lineno} en Literal de codigo intermedio')

		return n.type
			

	
	# def visit(self, n:Integer, func:IRFunction):
	# 	pass

	# def visit(self, n:Float, func:IRFunction):
	# 	pass

	# def visit(self, n:Char, func:IRFunction):
	# 	pass
		
	# def visit(self, n:Bool, func:IRFunction):
	# 	pass

	def visit(self, n:Binary, func:IRFunction):
		print(n)
		
		if n.op == '&&':
			...
		elif n.op == '||':
			...
		else:
			left = n.left.accept(self, func)
			right = n.right.accept(self, func)
			func.append((self._binop_code[left, n.op, right],))
			return right
		
	def visit(self, n:Unary, func:IRFunction):
		value_type = n.expression.accept(self, func)
		instructions = self._unaryop_code[n.oper, value_type]
		func.extend(instructions)

		return value_type
		
	def visit(self, n:TypeConversion, func:IRFunction):
		pass
		
	def visit(self, n:FuncCall, func:IRFunction):
		pass
	
	def visit(self, n:LocationPrimi, func:IRFunction):
		pass
		
	def visit(self, n:LocationMem, func:IRFunction):
		pass


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