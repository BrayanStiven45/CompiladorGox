import unittest
from analizador_lexico import tokenize, Token

class TestTokenizer(unittest.TestCase):
	def test_simple_tokens(self): # Test the simple tokens
		text = "var x = 42; print(x);"
		print(text)
		tokens = [tok for tok in tokenize(text)]
		
		expected_tokens = [
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='PRINT', value='print', lineno=1),
			Token(type='LPAREN', value='(', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='RPAREN', value=')', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
		]
		
		self.assertEqual(tokens, expected_tokens)
	
	def test_float_tokens(self): # Test the float tokens 
		text = "var x = 42.5;\n var y = .5;\n\n var z = 42.;\n var w = 0.;\t var v = 0.5; var m = 42.2e-2; var n = 42.2e2; var o = 42.2e+2; var p = 42.2E2; var q = 42.e2;"

		tokens = [tok for tok in tokenize(text)]

		expected_tokens = [
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='FLOAT', value='42.5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=2),
			Token(type='ID', value='y', lineno=2),
			Token(type='ASSIGN', value='=', lineno=2),
			Token(type='FLOAT', value='.5', lineno=2),
			Token(type='SEMI', value=';', lineno=2),
			Token(type='VAR', value='var', lineno=4),
			Token(type='ID', value='z', lineno=4),
			Token(type='ASSIGN', value='=', lineno=4),
			Token(type='FLOAT', value='42.', lineno=4),
			Token(type='SEMI', value=';', lineno=4),
			Token(type='VAR', value='var', lineno=5),
			Token(type='ID', value='w', lineno=5),
			Token(type='ASSIGN', value='=', lineno=5),
			Token(type='FLOAT', value='0.', lineno=5),
			Token(type='SEMI', value=';', lineno=5),
			Token(type='VAR', value='var', lineno=5),
			Token(type='ID', value='v', lineno=5),
			Token(type='ASSIGN', value='=', lineno=5),
			Token(type='FLOAT', value='0.5', lineno=5),
			Token(type='SEMI', value=';', lineno=5),
			Token(type='VAR', value='var', lineno=5),
			Token(type='ID', value='m', lineno=5),
			Token(type='ASSIGN', value='=', lineno=5),
			Token(type='FLOAT', value='42.2e-2', lineno=5),
			Token(type='SEMI', value=';', lineno=5),
			Token(type='VAR', value='var', lineno=5),
			Token(type='ID', value='n', lineno=5),
			Token(type='ASSIGN', value='=', lineno=5),
			Token(type='FLOAT', value='42.2e2', lineno=5),
			Token(type='SEMI', value=';', lineno=5),
			Token(type='VAR', value='var', lineno=5),
			Token(type='ID', value='o', lineno=5),
			Token(type='ASSIGN', value='=', lineno=5),
			Token(type='FLOAT', value='42.2e+2', lineno=5),
			Token(type='SEMI', value=';', lineno=5),
			Token(type='VAR', value='var', lineno=5),
			Token(type='ID', value='p', lineno=5),
			Token(type='ASSIGN', value='=', lineno=5),
			Token(type='FLOAT', value='42.2E2', lineno=5),
			Token(type='SEMI', value=';', lineno=5),
			Token(type='VAR', value='var', lineno=5),
			Token(type='ID', value='q', lineno=5),
			Token(type='ASSIGN', value='=', lineno=5),
			Token(type='FLOAT', value='42.e2', lineno=5),
			Token(type='SEMI', value=';', lineno=5),
		]

		self.assertEqual(tokens, expected_tokens)

	def test_char_tokens(self): # Test the char tokens
		text = "var x = 'a'; var y = '\\n'; var z = '\\x41'; var w = '\\'';"

		tokens = [tok for tok in tokenize(text)]

		expected_tokens = [
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='CHAR', value="'a'", lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='y', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='CHAR', value="'\\n'", lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='z', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='CHAR', value="'\\x41'", lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='w', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='CHAR', value="'\\''", lineno=1),
			Token(type='SEMI', value=';', lineno=1),
		]

		self.assertEqual(tokens, expected_tokens)

	def test_operators(self): # Test the operators
		text = "var int x = 42 + 5; var y = 42 - 5; var z = 42 * 5; var w = 42 / 5; var v = 42 < 5; var m = 42 <= 5; var n = 42 > 5; var o = 42 >= 5; var p = 42 == 5; var q = 42 != 5; var r = 42 && 5; var s = 42 || 5; var t = 42 ^ 5;"

		tokens = [tok for tok in tokenize(text)]

		expected_tokens = [
			Token(type='VAR', value='var', lineno=1),
			Token(type='INT', value='int', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='PLUS', value='+', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='y', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='MINUS', value='-', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='z', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='TIMES', value='*', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='w', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='DIVIDE', value='/', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='v', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='LT', value='<', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='m', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='LE', value='<=', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='n', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='GT', value='>', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='o', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='GE', value='>=', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='p', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='EQ', value='==', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='q', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='NE', value='!=', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='r', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='LAND', value='&&', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='s', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='LOR', value='||', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='t', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='GROW', value='^', lineno=1),
			Token(type='INTEGER', value='5', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
		]

		self.assertEqual(tokens, expected_tokens)

	def test_keywords(self): # Test the keywords
		text = "const x = 42; var y = 42; print(x); return y; break; continue; if x < 42; else y; while x < 42; func x; import y; true; false;"

		tokens = [tok for tok in tokenize(text)]

		expected_tokens = [
			Token(type='CONST', value='const', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='VAR', value='var', lineno=1),
			Token(type='ID', value='y', lineno=1),
			Token(type='ASSIGN', value='=', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='PRINT', value='print', lineno=1),
			Token(type='LPAREN', value='(', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='RPAREN', value=')', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='RETURN', value='return', lineno=1),
			Token(type='ID', value='y', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='BREAK', value='break', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='CONTINUE', value='continue', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='IF', value='if', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='LT', value='<', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='ELSE', value='else', lineno=1),
			Token(type='ID', value='y', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='WHILE', value='while', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='LT', value='<', lineno=1),
			Token(type='INTEGER', value='42', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='FUNC', value='func', lineno=1),
			Token(type='ID', value='x', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='IMPORT', value='import', lineno=1),
			Token(type='ID', value='y', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='TRUE', value='true', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
			Token(type='FALSE', value='false', lineno=1),
			Token(type='SEMI', value=';', lineno=1),
		]

		self.assertEqual(tokens, expected_tokens)

		
if __name__ == '__main__':
	unittest.main()

