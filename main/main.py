import sys
import os

from rich import print

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Parser.parser import Parser
from Checker.check import Checker
from Codigo_Intermedio.IR import *

try:

    nodes = Parser('prueba.gox')
    
    ast = nodes.parse()

    print(ast)
    # check = Checker()
    
    _, env = Checker.check(ast)
    
    env.print()

    module = IRCode.gencode(ast)
        
    module.dump()

except Exception as e:
    print("Ocurrió un error:", e)


