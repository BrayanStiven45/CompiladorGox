from sly import Parser
from goxlex import Lexer
from goxats import *
import json
import os

class Token:
    def __init__(self, type, value, lineno, index=0):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.index = index
        self.end = index

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.lineno})"

class Program(Node):
    def __init__(self, statements):
        super().__init__("Program")
        self.statements = statements
        for stmt in statements:
            self.add_child(stmt)
    
    def __repr__(self):
        return f'Program(statements={len(self.statements)})'

class GoxParser(Parser):
    tokens = Lexer.tokens
    
    precedence = (
        ('left', 'LOR'),
        ('left', 'LAND'),
        ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MODULO'),
        ('right', 'UMINUS'),
    )

    @_('statements')
    def program(self, p):
        return Program(p.statements)

    @_('statement statements',
       '')
    def statements(self, p):
        if len(p) == 0:
            return []
        return [p.statement] + (p.statements if p.statements else [])

    @_('assignment',
       'vardecl',
       'funcdecl',
       'if_stmt',
       'while_stmt',
       'break_stmt',
       'continue_stmt',
       'return_stmt',
       'print_stmt',
       'compound_stmt')
    def statement(self, p):
        return p[0]

    @_('LBRACE statements RBRACE')
    def compound_stmt(self, p):
        return p.statements

    @_('location ASSIGN expression SEMI')
    def assignment(self, p):
        return Assignment(p.location, p.expression)

    @_('VAR ID type_spec ASSIGN expression SEMI')
    def vardecl(self, p):
        return VariableDeclaration(p.ID, p.type_spec, p.expression, False)

    @_('VAR ID type_spec SEMI')
    def vardecl(self, p):
        return VariableDeclaration(p.ID, p.type_spec, None, False)

    @_('CONST ID type_spec ASSIGN expression SEMI')
    def vardecl(self, p):
        return VariableDeclaration(p.ID, p.type_spec, p.expression, True)

    @_('FUNC ID LPAREN parameters RPAREN type LBRACE statements RBRACE',
       'FUNC ID LPAREN parameters RPAREN LBRACE statements RBRACE')
    def funcdecl(self, p):
        return_type = p.type if hasattr(p, 'type') else 'void'
        return FunctionDefinition(p.ID, p.parameters, return_type, p.statements)

    @_('IF expression compound_stmt')
    def if_stmt(self, p):
        return Conditional(p.expression, p.compound_stmt)

    @_('IF expression compound_stmt ELSE compound_stmt')
    def if_stmt(self, p):
        return Conditional(p.expression, p.compound_stmt0, p.compound_stmt1)

    @_('WHILE expression compound_stmt')
    def while_stmt(self, p):
        return WhileLoop(p.expression, p.compound_stmt)

    @_('BREAK SEMI')
    def break_stmt(self, p):
        return Break()
    
    @_('ID LPAREN args RPAREN SEMI')  # Nueva regla para llamadas a funciones como statements
    def statement(self, p):
        return FunctionCall(p.ID, p.args)

    @_('CONTINUE SEMI')
    def continue_stmt(self, p):
        return Continue()

    @_('RETURN expression SEMI')
    def return_stmt(self, p):
        return Return(p.expression)

    @_('PRINT expression SEMI')
    def print_stmt(self, p):
        return Print(p.expression)

    @_('expression LOR expression')
    def expression(self, p):
        return BinaryOperation(p.expression0, p.LOR, p.expression1)

    @_('expression LAND expression')
    def expression(self, p):
        return BinaryOperation(p.expression0, p.LAND, p.expression1)

    @_('expression EQ expression', 'expression NE expression')
    def expression(self, p):
        return BinaryOperation(p.expression0, p[1], p.expression1)

    @_('expression LT expression', 'expression LE expression',
       'expression GT expression', 'expression GE expression')
    def expression(self, p):
        return BinaryOperation(p.expression0, p[1], p.expression1)

    @_('expression PLUS expression', 'expression MINUS expression')
    def expression(self, p):
        return BinaryOperation(p.expression0, p[1], p.expression1)

    @_('expression TIMES expression', 'expression DIVIDE expression', 
       'expression MODULO expression')
    def expression(self, p):
        return BinaryOperation(p.expression0, p[1], p.expression1)

    @_('MINUS expression %prec UMINUS')
    def expression(self, p):
        return UnaryOperation('-', p.expression)

    @_('LPAREN expression RPAREN')
    def expression(self, p):
        return p.expression

    @_('location')
    def expression(self, p):
        return p.location

    @_('literal')
    def expression(self, p):
        return p.literal

    @_('ID LPAREN args RPAREN')
    def expression(self, p):
        return FunctionCall(p.ID, p.args)

    @_('ID')
    def location(self, p):
        return PrimitiveReadLocation(p.ID)

    @_('INTEGER')
    def literal(self, p):
        return Literal('int', p.INTEGER)

    @_('FLOAT_LITERAL')
    def literal(self, p):
        return Literal('float', p.FLOAT_LITERAL)

    @_('STRING_LITERAL')
    def literal(self, p):
        return Literal('string', p.STRING_LITERAL)

    @_('TRUE', 'FALSE')
    def literal(self, p):
        return Literal('bool', p[0])

    @_('INT', 'FLOAT', 'CHAR', 'BOOL')
    def type_spec(self, p):
        return p[0]

    @_('ID type_spec')
    def parameter(self, p):
        return Parameter(p.ID, p.type_spec)

    @_('parameter COMMA parameters',
       'parameter')
    def parameters(self, p):
        if len(p) == 1:
            return [p.parameter]
        return [p.parameter] + p.parameters

    @_('')
    def parameters(self, p):
        return []

    @_('INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID')
    def type(self, p):
        return p[0]

    @_('expression COMMA args',
       'expression')
    def args(self, p):
        if len(p) == 1:
            return [p.expression]
        return [p.expression] + p.args

    @_('')
    def args(self, p):
        return []

    def error(self, p):
        if p:
            raise SyntaxError(f"Error de sintaxis en línea {p.lineno}, token inesperado '{p.value}'")
        else:
            raise SyntaxError("Error de sintaxis al final del archivo")

# Función para convertir AST a JSON
def ast_to_dict(node):
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif hasattr(node, "__dict__"):
        return {
            "__type__": node.__class__.__name__,
            **{key: ast_to_dict(value) 
               for key, value in node.__dict__.items() 
               if not key.startswith('_')}
        }
    elif isinstance(node, Token):
        return {
            "__type__": "Token",
            "type": node.type,
            "value": node.value,
            "lineno": node.lineno
        }
    else:
        return node

# Prueba del parser
def test_parser(source_code=None):
    if source_code is None:
        source_code = """
        func main() {
            if true {
                print "hola";
            }
        }
        """
    
    lexer = Lexer()
    tokens = list(lexer.tokenize(source_code))
    
    filtered_tokens = [
        (tok_type, tok_value, lineno) 
        for tok_type, tok_value, lineno in tokens
        if tok_type not in {'WHITESPACE', 'NEWLINE', 'COMMENT_LINE'}
    ]
    
    structured_tokens = [
        Token(type=t[0], value=t[1], lineno=t[2], index=i)
        for i, t in enumerate(filtered_tokens)
    ]
    
    parser = GoxParser()
    
    try:
        ast = parser.parse(iter(structured_tokens))
        ast_json = json.dumps(ast_to_dict(ast), indent=4, ensure_ascii=False)
        
        ast_file_path = "ast_output.json"
        with open(ast_file_path, "w", encoding="utf-8") as f:
            f.write(ast_json)
            
        print("\n✅ Análisis sintáctico exitoso")
        print(f"📄 AST guardado en: {os.path.abspath(ast_file_path)}")
        
        return ast_file_path
        
    except SyntaxError as e:
        print("\n❌ Error de sintaxis detectado:")
        print(str(e))
        print("\nTokens alrededor del error:")
        
        error_index = e.token.index if hasattr(e, 'token') else len(filtered_tokens)-1
        start = max(0, error_index-2)
        end = min(len(filtered_tokens), error_index+3)
        
        for i in range(start, end):
            t = filtered_tokens[i]
            marker = ">>>" if i == error_index else "   "
            print(f"{marker} Línea {t[2]}: {t[0]}({t[1]})")
        
    except Exception as e:
        print("\n❌ Error inesperado durante el análisis:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        
        if hasattr(e, 'token'):
            print(f"Token problemático: {e.token.type}({e.token.value})")
            print(f"Línea: {e.token.lineno}")
        
    return None

if __name__ == "__main__":
    print("🔍 Iniciando análisis sintáctico...")
    
    with open("factorize.gox", encoding="utf-8") as f:
        source = f.read()
        result = test_parser(source)
    
    if result:
        print("\n📍 Análisis completado exitosamente")
    else:
        print("\n✖️ El análisis encontró errores. Revisa la salida anterior.")