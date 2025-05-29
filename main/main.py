import sys
import os

from rich import print

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Parser.parser import Parser
from Checker.check import Checker
from Codigo_Intermedio.IR import *
from Maquina_de_pila.StackMachine import StackMachine

try:

    nodes = Parser('prueba.gox')

    ast = nodes.parse()
    print('Analisis Lexico Correcto')
    print('Analisis Sintactico Correcto')

    # print(ast)
    # check = Checker()

    _, env = Checker.check(ast)

    # env.print()
    # print(ast)
    print('Analisis Semantico Correcto')

    module = IRCode.gencode(ast)
    print('Generador de Codigo Intermedio Correcto')
    # module.dump()


    

except Exception as e:
    print("Ocurrió un error:", e)


vm = StackMachine()
vm.load_ir(module)
vm.run()