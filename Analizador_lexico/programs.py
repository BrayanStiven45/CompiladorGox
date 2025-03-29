# programs.py
# 
# En las entrañas de su compilador, debe representar programas
# como estructuras de datos. En este archivo, codificará manualmente
# algunos programas goxlang simples usando el modelo de datos que
# se ha desarrollado en el archivo goxlang/model.py
#
# El propósito de este ejercicio es doble:
#
# 1. Asegúrese de comprender el modelo de datos de su compilador.
# 2. Tenga algunas estructuras de programas que pueda usar para pruebas
# y experimentación posteriores.
#
# Este archivo está dividido en secciones. Siga las instrucciones para
# cada parte. Es posible que se haga referencia a partes de este archivo 
# en partes posteriores del proyecto. Planifique tener muchos debates.
#
from model import *

# ---------------------------------------------------------------------
# Expression Simple
#
# Esto se le da a usted como un ejemplo

expr_source = "2 + 3 * 4"

expr_model = BinOp('+', Integer(2),
                        BinOp('*', Integer(3),
                        Integer(4)))

# ---------------------------------------------------------------------
# Programa 1: Printing
#
# Codifique el siguiente programa el cual prueba la impresión y expresion simple
#
source1 = '''
    print 2 + 3 * -4;
    print 2.0 - 3.0 / -4.0;
    print -2 + 3;
'''

model1 = None

# ---------------------------------------------------------------------
# Programa 2: Declaración de Variables y Constantes.
#            Expresiones y Asignaciones
#
# Codifique la siguiente sentencia.

source2 = '''
    const pi = 3.14159;
    var tau float;
    tau = 2.0 * pi;
    print(tau);
'''

model2 = None

# ---------------------------------------------------------------------
# Programa 3: Condicionales. Este programa imprime el mínimo de 
#            dos valores
#
# Codifique la siguiente sentencia.

source3 = '''
    var a int = 2;
    var b int = 3;
    if a < b {
        print a;
    } else {
        print b;
    }
'''

model3 = None

# ---------------------------------------------------------------------
# Programa 4: Ciclos.  Este programa imprime los primeros 10 factoriales.
#
source4 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;

    while x < n {
        fact = fact * x;
        print fact;
        x = x + 1;
    }
'''

model4 = None

# ---------------------------------------------------------------------
# Programa 5: Funciones (simple)
#
source5 = '''
    func square(x int) int {
        return x*x;
    }

    print square(4);
    print square(10);
'''

model5 = None

# ---------------------------------------------------------------------
# Programa 6: Funciones (complejas)
#
source6 = '''
    func fact(n int) int {
        var x int = 1;
        var result int = 1;
        while x < n {
            result = result * x;
            x = x + 1;
        }
        return result;
    }

    print(fact(10));
'''

model6 = None

# ---------------------------------------------------------------------
# Programa 7: Conversión de tipos
#
source7 = '''
    var pi = 3.14159;
    var spam = 42;

    print(spam * int(pi));
    print(float(spam) * pi;)
    print(int(spam) * int(pi));
'''

model7 = None

# ---------------------------------------------------------------------
# Programa 8: Acceso a memoria
#
source8 = '''
    var x int = ^8192;      // Incrementa memoria por 8192 bytes
    var addr int = 1234;
    `addr = 5678;           // Almacena 5678 en addr
    print(`addr + 8);
'''

model8 = None