
class StackMachine:
    def __init__(self):
        self.stack = []                       # Pila principal
        self.memory = [0] * 1024              # Memoria lineal
        self.globals = {}                     # Variables globales
        # self.locals_stack = []                # Stack de variables locales por función
        self.locals_stack = {}                # Stack de variables locales por función
        self.call_stack = []                  # Stack de retorno
        self.functions = {}                   # Diccionario de funciones
        self.pc = 0                           # Contador de programa
        self.program = []                     # Programa IR cargado
        self.running = False

        self.else_pc = 0
        self.endif_pc = 0
        self.start_loop_pc = 0
        self.end_loop_pc = 0
        self.pc_if = 0
        self.pc_loop = 0

        # self.break_loop = False
        # self.continue_loop = False
        # self.return_func = False

    def load_ir(self, module):
        self.program = module.functions['main'].code
        self.functions = module.functions 
        self.functions.pop('main')
        # print(self.functions)
        # self.globals = module.globals
        for name, value in module.globals.items():
            type = value.type
            self.globals[name] = (type, None)

    def load_program(self, program):
        self.program = program

    def run(self):
        self.pc = 0
        self.running = True
        while self.running and self.pc < len(self.program):
            instr = self.program[self.pc]
            opname = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            method = getattr(self, f"op_{opname}", None)

            if opname == 'LOOP' or opname == 'IF':
                args.append(self.pc)
            
            # if self.break_loop:
            #     self.running = False
            #     continue

            # if self.continue_loop:
            #     self.running = False
            #     self.pc = -1
            #     continue
            # print(f'Esto es globals {self.globals}')
            # print(f'Operacion a reslizar op_{opname}')
            # print(f'para el pc {self.pc}')
            # print(f'este es el program {self.program}')
            
            # print(f'para locals {self.locals_stack}')
            
            
            if method:
                method(*args)
            else:
                raise RuntimeError(f"Error en StackMachine: Instrucción desconocida: {opname}")
            
            # print(f'Esto es pila: {self.stack}')
            # print(f'Para runing {self.running}')
            self.pc += 1

    def op_CONSTI(self, value):
        self.stack.append(('I', value))
    

    def op_ADDI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', a + b))
        else:
            raise TypeError("Error en StackMachine: ADDI requiere dos enteros")

    def op_SUBI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', a - b))
        else:
            raise TypeError("Error en StackMachine: SUBI requiere dos enteros")
    
    def op_MULI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', a * b))
        else:
            raise TypeError("Error en StackMachine: MULI requiere dos enteros")

    def op_DIVI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            # value = round(a / b)
            # self.stack.append(('I', int(value)))
            self.stack.append(('I', a // b))
        else:
            raise TypeError("Error en StackMachine: DIVI requiere dos enteros")
        
    def op_LTI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', int(a < b)))
        else:
            raise TypeError("Error en StackMachine: LTI requiere dos enteros")
    
    def op_LEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', int(a <= b)))
        else:
            raise TypeError("Error en StackMachine: LEI requiere dos enteros")

    def op_GTI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', int(a > b)))
        else:
            raise TypeError("Error en StackMachine: GTI requiere dos enteros")
        
    def op_GEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', int(a >= b)))
        else:
            raise TypeError("Error en StackMachine: GEI requiere dos enteros")

    def op_EQI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', int(a == b)))
        else:
            raise TypeError("Error en StackMachine: EQI requiere dos enteros")
        
    def op_NEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'I':
            self.stack.append(('I', int(a != b)))
        else:
            raise TypeError("Error en StackMachine: NEI requiere dos enteros")
        
    def op_PEEKI(self):
        address_type, address = self.stack.pop()

        if address_type == 'I':
            if address < len(self.memory):
                self.stack.append(('I', int(self.memory[address])))
            else:
                raise TypeError(f"Error en StackMachine: Direccion {address} fuera de rango")    
        else:
            raise TypeError("Error en StackMachine: PEEKI requiere una direccion de entero")

    def op_POKEI(self):
        value_type, value = self.stack.pop()
        address_type, address = self.stack.pop()

        if value_type == address_type == 'I':
            if address < len(self.memory):
                self.memory[address] = int(value)
            else:
                raise TypeError(f"Error en StackMachine: Direccion {address} fuera de rango")    
        else:
            raise TypeError("Error en StackMachine: POKEI requiere una direccion de entero")
        
    def op_ITOF(self):
        value_type, value = self.stack.pop()

        if value_type == 'I':
            self.stack.append(('F', float(value)))
        else:
            raise TypeError("Error en StackMachine: ITOF requiere un numero entero")

    def op_CONSTF(self, value):
        self.stack.append(('F', value))
        
    def op_ADDF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('F', a + b))
        else:
            raise TypeError("Error en StackMachine: ADDF requiere dos flotantes")
        
    def op_SUBF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('F', a - b))
        else:
            raise TypeError("Error en StackMachine: SUBF requiere dos flotantes")
    
    def op_MULF(self):
        # print(f'esto es stack {self.stack}')
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('F', a * b))
        else:
            raise TypeError("Error en StackMachine: MULF requiere dos flotantes")

    def op_DIVF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('F', a / b))
        else:
            raise TypeError("Error en StackMachine: DIVF requiere dos flotantes")
        
    def op_LTF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('I', int(a < b)))
        else:
            raise TypeError("Error en StackMachine: LTF requiere dos flotantes")
    
    def op_LEF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('I', int(a <= b)))
        else:
            raise TypeError("Error en StackMachine: LEF requiere dos flotantes")

    def op_GTF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('I', int(a > b)))
        else:
            raise TypeError("Error en StackMachine: GTF requiere dos flotantes")
        
    def op_GEF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('I', int(a >= b)))
        else:
            raise TypeError("Error en StackMachine: GEF requiere dos flotantes")

    def op_EQF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('I', int(a == b)))
        else:
            raise TypeError("Error en StackMachine: EQF requiere dos flotantes")
        
    def op_NEF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'F':
            self.stack.append(('I', int(a != b)))
        else:
            raise TypeError("Error en StackMachine: NEF requiere dos flotantes")
        
    def op_PEEKF(self):
        address_type, address = self.stack.pop()

        if address_type == 'I':
            if address < len(self.memory):
                self.stack.append(('F', float(self.memory[address])))
            else:
                raise TypeError(f"Error en StackMachine: Direccion {address} fuera de rango")    
        else:
            raise TypeError("Error en StackMachine: PEEKF requiere una direccion de entero")

    def op_POKEF(self):
        value_type, value = self.stack.pop()
        address_type, address = self.stack.pop()

        if address_type == 'I':
            if value_type == 'F':
                if address < len(self.memory):
                    self.memory[address] = float(value)
                else:
                    raise TypeError(f"Error en StackMachine: Direccion {address} fuera de rango")    
            else:
                raise TypeError("Error en StackMachine: POKEF requiere un flotante")
        else:
            raise TypeError("Error en StackMachine: POKEF requiere una direccion de entero")
        
    def op_FTOI(self):
        value_type, value = self.stack.pop()

        if value_type == 'F':
            value = round(value)
            self.stack.append(('I', int(value)))
        else:
            raise TypeError("Error en StackMachine: FTOI requiere un numero flotante")

    def op_PRINTI(self):
        val_type, value = self.stack.pop()
        if val_type == 'I':
            print(value, end='')
        else:
            raise TypeError("Error en StackMachine: PRINTI requiere un entero")
        
    def op_PRINTF(self):
        val_type, value = self.stack.pop()
        if val_type == 'F':
            print(value, end='')
        else:
            raise TypeError("Error en StackMachine: PRINTF requiere un flotante")
        
    def op_PRINTB(self):
        val_type, value = self.stack.pop()
        if val_type == 'I':
            if value == 1 or value == 0:
                print(str(bool(value)).lower(), end='')
            else:
                print(chr(value), end='')
        else:
            raise TypeError("Error en StackMachine: PRINTF requiere un flotante")
        
    def op_PEEKB(self):
        address_type, address = self.stack.pop()

        if address_type == 'I':
            if address < len(self.memory):
                self.stack.append(('I', int(self.memory[address])))
            else:
                raise TypeError(f"Error en StackMachine: Direccion {address} fuera de rango")    
        else:
            raise TypeError("Error en StackMachine: PEEKB requiere una direccion de entero")

    def op_POKEB(self):
        value_type, value = self.stack.pop()
        address_type, address = self.stack.pop()

        if value_type == address_type == 'I':
            if address < len(self.memory):
                self.memory[address] = float(value)
            else:
                raise TypeError(f"Error en StackMachine: Direccion {address} fuera de rango")    
        else:
            raise TypeError("Error en StackMachine: POKEF requiere una direccion de entero")

    def op_RET(self):

        self.running = False

    def op_GLOBAL_SET(self, var):
        _ , a = self.stack.pop()
        type = self.globals[var][0]
        value = (type, a)
        self.globals[var] = value

    def op_GLOBAL_GET(self, var):
        value = self.globals[var]
        self.stack.append((value[0], value[1]))
    
    def findEndLoop(self, pc):
        while True:
            pc += 1
            a = self.program[pc]
            if a[0] == 'LOOP':
                pc = self.findEndLoop(pc)
            elif a[0] == 'ENDLOOP':
                return pc
    
    # NUevo para loop       
    # def op_CBREAK(self):
    #     # print(self.stack)
    #     _, condition = self.stack.pop()

    #     if condition == 1:
    #         print(f'Entro aqui con {self.end_loop_pc}')
    #         self.pc = self.pc_loop = self.end_loop_pc
    #         # self.running = False
    #         # self.break_loop = True
        
    #     # return self.end_loop_pc
        
    # def op_CONTINUE(self):
    #     self.pc_loop = self.start_loop_pc
    #     return self.start_loop_pc
    #     # self.pc = -1
    #     # self.continue_loop = True

    # def op_ENDLOOP(self):
    #     self.pc_loop = self.start_loop_pc
    #     # self.pc = -1

    # def op_LOOP(self, pc):
    #     # Guarda los valores por si esta dentro de un loop
    #     # start_loop_pc = self.start_loop_pc
    #     # end_loop_pc = self.end_loop_pc
    #     #Guarda los valores por si esta dentro de un if
    #     # else_pc = self.else_pc
    #     # endif_pc = self.endif_pc

    #     # While actual
    #     # self.start_loop_pc = pc + 1
    #     end_loop_pc = self.findEndLoop(pc)
    #     # self.pc_loop = pc

    #     # Guarda los valores anteriores si esta dentro de un ciclo
    #     # o dentro de un if, o del principal o función
    #     old_running = self.running
    #     old_program = self.program

    #     self.program = self.program[pc + 1: end_loop_pc + 1]

    #     self.pc = 0

    #     # print('En loop')
    #     self.run()

    #     self.break_loop = False
    #     self.continue_loop = False
    #     # print('Fin de loop')

    #     self.running = old_running
    #     self.program = old_program
    #     self.pc = end_loop_pc

    #     # start_loop_pc = start_loop_pc
    #     # end_loop_pc = end_loop_pc

    #     # self.else_pc = else_pc
    #     # self.endif_pc = endif_pc

    # NUevo para loop

    def op_CBREAK(self):
        # print(self.stack)
        _, condition = self.stack.pop()

        if condition == 1:
            # print(f'Entro aqui con {self.end_loop_pc}')
            self.pc = self.pc_loop = self.end_loop_pc
        
        return self.end_loop_pc
        
    def op_CONTINUE(self):
        self.pc_loop = self.start_loop_pc
        return self.start_loop_pc

    def op_ENDLOOP(self):
        self.pc_loop = self.start_loop_pc

    def op_LOOP(self, pc):
        self.start_loop_pc = pc
        self.end_loop_pc = self.findEndLoop(pc)
        self.pc_loop = pc
        
        while self.pc_loop < self.end_loop_pc and self.running:
            # print(f'Despues del break {self.pc_loop}')
            self.pc_loop += 1
            instr = self.program[self.pc_loop]
            opname = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            method = getattr(self, f"op_{opname}", None)

            # print(f'Operacion a reslizar op_{opname}')
            # print(f'para el pc {self.pc}')
            # print(f'para locals {self.locals_stack}')
            # print(f'para la pila {self.stack}')
            # print(f'Operacion a reslizar op_{opname}')
            # print(f'para el pc_loop {self.pc_loop}')

            if opname == 'LOOP' or opname == 'IF':
                args.append(self.pc_loop)
                start_loop_pc = self.start_loop_pc
                end_loop_pc = self.end_loop_pc

                else_pc = self.else_pc
                endif_pc = self.endif_pc

                self.pc_loop = method(*args)

                self.start_loop_pc = start_loop_pc
                self.end_loop_pc = end_loop_pc

                self.else_pc = else_pc
                self.endif_pc = endif_pc
                continue
            # print(self.stack)
            if method:
                # print(f'opname {opname}')
                method(*args)
            else:
                raise RuntimeError(f"Error en StackMachine: Instrucción desconocida: {opname}")

            # print(f'Esto es pila: {self.stack}')
        return self.end_loop_pc

    def findElseAndEndIf(self, pc):
        else_pc = None
        # print(pc)
        while True:
            
            pc += 1
            a = self.program[pc]

            if a[0] == 'IF':
                _, pc = self.findElseAndEndIf(pc)
            elif a[0] == 'ELSE':
                else_pc = pc
            elif a[0] == 'ENDIF':
                return (else_pc, pc)

    # NUevo para if 
    # def op_ELSE(self):
    #     self.running = False

    # def op_ENDIF(self):
    #     self.running = False

    # def op_IF(self, pc):
    #     _, condition = self.stack.pop()
    #     else_pc, endif_pc = self.findElseAndEndIf(pc)    

    #     if condition == 0:
    #         pc_if = else_pc + 1
    #     else:
    #         pc_if = pc + 1

    #     old_running = self.running
    #     old_program = self.program

    #     self.program = self.program[pc_if : endif_pc + 1]

    #     self.pc = 0

    #     print('En IF')
    #     self.run()
    #     print('Fin de IF')

    #     self.running = old_running
    #     self.program = old_program
    #     self.pc = endif_pc
    # NUevo para if 


    def op_IF(self, pc):
        _, condition = self.stack.pop()
        self.else_pc, self.endif_pc = self.findElseAndEndIf(pc)

        if condition == 0:
            self.pc_if = self.else_pc + 1
        else:
            self.pc_if = pc + 1
        
        while self.pc_if <= self.endif_pc and self.running:
            instr = self.program[self.pc_if]
            opname = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            method = getattr(self, f"op_{opname}", None)

            # print(f'Operacion a reslizar op_{opname}')
            # print(f'para el pc_if {self.pc_if}')

            if opname == 'LOOP' or opname == 'IF':
                args.append(self.pc_if)  
                else_pc = self.else_pc
                endif_pc = self.endif_pc

                start_loop_pc = self.start_loop_pc
                end_loop_pc = self.end_loop_pc

                self.pc_if = method(*args)

                self.else_pc = else_pc
                self.endif_pc = endif_pc

                self.start_loop_pc = start_loop_pc
                self.end_loop_pc = end_loop_pc

                continue

        
            if opname == 'CBREAK' or opname == 'CONTINUE':
                return method(*args)
                # self.pc = self.endif_pc

            
            if opname == 'ELSE' or opname == 'ENDIF':
                self.pc = self.endif_pc
                break

            if method:
                method(*args)
            else:
                raise RuntimeError(f"Error en StackMachine: Instrucción desconocida: {opname}")
            
            # print(f'Esto es pila: {self.stack}')
            # print(f'Esto es pila: {self.stack}')
            self.pc_if += 1
        return self.endif_pc
            
    def op_GROW(self):
        a_type, a = self.stack.pop()

        if a_type == 'I':
            new_list = [0] * a
            self.stack.append(('I', len(self.memory)))
            self.memory = self.memory + new_list
            
        else:
            raise TypeError("Error en StackMachine: GROW requiere un valor entero")


    def op_CALL(self, name_func):
        old_locals_stack = self.locals_stack

        else_pc = self.else_pc
        endif_pc = self.endif_pc
        pc_if = self.pc_if

        start_loop_pc = self.start_loop_pc
        end_loop_pc = self.end_loop_pc
        pc_loop = self.pc_loop
        

        old_pc = self.pc
        old_program = self.program
        old_runing = self.running

        self.locals_stack = {}

        func = self.functions[name_func]
        parmnames = func.parmnames
        parmtypes = func.parmtypes
        # print(parmnames)
        i = len(parmnames)-1
        while i >= 0:
            value_type, value = self.stack.pop()
            # print(f'esto es parmname {parmnames[i]}')
            # print(f'esto es parmtype {parmtypes[i]}')
            # print(f'esto es value {value}')
            if value_type == parmtypes[i]:
                self.locals_stack[parmnames[i]] = (parmtypes[i], value)
            else:
                raise TypeError("Error en StackMachine: CALL requiere que el tipo de parametro y el tipo de argumento sean iguales")

            i -= 1

        for name, value in func.locals.items():
            type = value
            self.locals_stack[name] = (type, None)
        

        self.pc = 0

        self.program = func.code

        # print(self.program)
        # print(f'Incia funcion {name_func}')
        self.run()
        # print(f'Finaliza funcion {name_func}')
        # print(f'sale de funcion {name_func}')
        self.else_pc = else_pc
        self.endif_pc = endif_pc
        self.pc_if = pc_if

        self.start_loop_pc = start_loop_pc
        self.end_loop_pc = end_loop_pc
        self.pc_loop = pc_loop

        self.locals_stack = old_locals_stack
        # print(f'con locals {self.locals_stack}')
        self.program = old_program
        self.pc = old_pc
        self.running = old_runing
       

    def op_LOCAL_SET(self, var):
        # print(self.locals_stack)
        _ , a = self.stack.pop()
        type = self.locals_stack[var][0]
        value = (type, a)
        self.locals_stack[var] = value

    def op_LOCAL_GET(self, var):
        # print(f'para pc {self.pc}')
        # print(f'esto es locals {self.locals_stack}')
        value = self.locals_stack[var]
        self.stack.append((value[0], value[1]))


# program = [
#     ('CONSTI', 10),
#     ('CONSTI', 20),
#     ('ADDI',),
#     ('PRINTI',),
#     ('RET',),
# ]

# vm = StackMachine()
# vm.load_program(program)
# vm.run()