import re
from dataclasses import dataclass
from rich.table   import Table
from rich.console import Console
from rich    import print

# Define the tokens for the language 

TWO_CHAR = { # Tokens with their respective grammar for two characters
    '<=': 'LE',
    '>=': 'GE',
    '==': 'EQ',
    '!=': 'NE',
    '&&': 'AND',
    '||': 'OR',
}


ONE_CHAR = { # Tokens with their respective grammar for a character
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',
    '<': 'LT',
    '>': 'GT',
    '^': 'GROW',
    '=': 'ASSIGN',
    ';': 'SEMI',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ',': 'COMMA',
    '`': 'DEREF',
}

KEYWORDS = { # Keywords of the language
    'const', 'var', 'print', 'return', 'break', 'continue',
    'if', 'else', 'while', 'func', 'import', 'true', 'false',
    'int', 'float', 'char', 'bool', 
}

NAME_PAT = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*') # Regular expression for the identifier name
FLOAT_PAT = re.compile(r'\d*\.(?:\d+)?(?:[eE][-+]?\d+)?') # Regular expression for the floating point number
INT_PAT = re.compile(r'\d+') # Regular expression for the integer number
CHAR_PAT = re.compile(r'\'([a-zA-Z]|\\[a-z]|\\x[0-9A-Fa-f]{2}|\\\')\'') # Regular expression for the character



@dataclass
class Token: # Data class for the tokens with the type, value and line number
    type: str
    value: str
    lineno: int

errors = [] # List to store the errors in the file

class Tokenize:

    class LexerError(Exception):
        def __init__(self, errors):
            self.errors = errors
            message = self.format_errors(errors)
            super().__init__(message)

        def format_errors(self, errors):
            return "\nErrores léxicos encontrados:\n" + "\n".join(
                f"  - Línea {line}: Token inválido '{char}'" for char, line in errors
            )

    def __init__(self):
        self.errors = []


    def tokenize(self, text): # Function to tokenize the text
        lineno = 1 # Line number
        pos = 0 # Current position

        # Read the text character by character
        while pos < len(text):
            
            if text[pos].isspace(): # Skip whitespaces, tabs and newlines
                if text[pos] == '\n': # Count newlines
                    lineno += 1
                pos += 1
                continue
            elif text[pos : pos+2] == '/*': # Skip comments (/* ... */)
                end = text.find('*/', pos+2)
                if end >= 0:
                    lineno += text[pos:end].count('\n')
                    pos = end + 2
                    continue
                else:
                    raise SyntaxError(f'Invalid token: Comment not closed at line {lineno} \n') # Error if the comment is not closed
            elif text[pos : pos+2] == '//': # Skip comments (// ...)
                end = text.find('\n', pos+2)
                if end >= 0:
                    lineno += 1
                    pos = end + 1
                    continue
                else:
                    pos = len(text)
            elif text[pos].isalpha() or text[pos] == '_': # Validate the identifier name and keywords
                value = NAME_PAT.match(text, pos)
                if value:
                    identifier = value.group()
                    if identifier in KEYWORDS:
                        if identifier == 'true' or identifier == 'false':
                            yield Token('BOOL', identifier, lineno)
                        else:
                            yield Token(identifier.upper(), identifier, lineno) # Return the token with the type of the keyword
                    else:
                        yield Token('ID', identifier, lineno) # Return the token with the type ID
                    pos = value.end()
                else:
                    self.saveError(text[pos], lineno)
                    pos += 1

            elif text[pos].isdigit() or text[pos] == ".": # Validates if it is a floating point or integer
                value = FLOAT_PAT.match(text, pos)
                if value:
                    yield Token('FLOAT', value.group(), lineno) # Return the token with the type FLOAT
                    pos = value.end()
                else:
                    value = INT_PAT.match(text, pos)
                    if value:
                        yield Token('INT', value.group(), lineno) # Return the token with the type INTEGER
                        pos = value.end()
                    else:
                        self.saveError(text[pos], lineno)
                        pos += 1
            elif text[pos] == '\'':
                value = CHAR_PAT.match(text,pos)
                if value:
                    yield Token('CHAR', value.group(), lineno) # Return the token with the type CHAR
                    pos = value.end()
                else:
                    self.saveError(text[pos], lineno)
                    pos += 1
            elif text[pos:pos+2] in TWO_CHAR:
                simbol = text[pos:pos+2]
                yield Token(TWO_CHAR[simbol], simbol, lineno) # Return the token with the type of the two-character symbol
                pos += 2
            elif text[pos] in ONE_CHAR:
                simbol = text[pos]
                yield Token(ONE_CHAR[simbol], simbol, lineno) # Return the token with the type of the one-character symbol
                pos += 1
            else:
                self.saveError(text[pos], lineno)
                pos += 1

    # # Print the errors
    # def printError(self, pos, lineno):
    #     print(f'SyntaxError: Invalid token: {pos} at line {lineno}')
    #     lineno += 1

    def saveError(self, pos, lineno):
        self.errors.append((pos, lineno))


    # Print table
    def printToken(self, toks):
        table = Table(title='Análisis Léxico')
        table.add_column('type')
        table.add_column('value')
        table.add_column('lineno', justify='right')

        for tok in toks:
            value = tok.value if isinstance(tok.value, str) else str(tok.value)
            table.add_row(tok.type, value, str(tok.lineno))
            # print(tok)
        console = Console()
        console.print(table)

    # Main function
    # @classmethod
    def main (self, argv):
        tokens = []
        # if len(argv) != 1: # Check the number of arguments passed to the program
        #     raise SystemExit(f'Usage: python {argv[0]} <file>')
        with open(argv) as file: # Open the file passed as an argument
            for token in self.tokenize(file.read()): # Tokenize the file content
                tokens.append(token)
        
        self.printToken(tokens) # Print the tokens in a table format
        
        if self.errors:
            raise self.LexerError(self.errors)
        
        print('Analisis Lexico Correcto')

        return tokens

# Run the main function
if __name__ == '__main__':
    import sys
    argv = None
    if len(sys.argv) == 2:
        argv = sys.argv[1]
    else:
        argv = sys.argv[0]  

    tokenize = Tokenize() # Create an instance of the Tokenize class
    tokenize.main(argv) # Call the main function with the arguments passed to the program
