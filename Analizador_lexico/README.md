# Estudiantes
Brayan Stiven Valencia Ospina  1112298468
Luis Daniel Rosas Miranda      1089932057

# analizador lexico
El codigo analiza y guarda tokens de un archivo del lenguaje .gox

El codigo se divide en 7 partes:

    1. Se crean los tokens para simbolos presentes en el lenguaje, los tokens se dividen en 2 variables tipo dict y una variable tipo set :

        TWO_CHAR: Este diccionario guarda los tokens de los simbolos que son de dos caracteres como por ejemplo el simbolo "<=".

        ONE_CHAR: Este diccionario guarda los tokens de los simbolos que son de un solo caracter como por ejemplo el simbolo "+".

        KEYWORDS: Este conjunto guarda las palabras reservadas del lenguaje gox.
    
    2. Se crean expresiones regulares (regex) con la libreria "re" de python para reconocer diferentes tipos de tokens, como:
        NAME_PAT: Expresion regular que reconoce tokens de tipo ID, para nombres de variables y nombres de funciones

        FLOAT_PAT: Expresion regular que reconoce tokens de tipo FLOAT, para numeros constantes de tipo punto flotante

        INT_PAR: Expresion regular que reconoce tokens de tipo INTEGER, para numeros constantes de tipo entero

        CHAR_PAR: Expresion regular que reconoce tokens de tipo CHAR, para reconocer caracteres de un byte, y caracteres especiales como saltos de lineas "\n" y valores hexadecimales.

    3. Se crea la clase Token con el decorador @dataClass de la libreria dataclass de python, que permite crear automaticamente las clases "__init__", "__repr__" y "__eq__". Esta clase permite crear los tokens, donde recive los atributos "type:str, value:str, lineno:int".

    4. Se declara el arreglo errors, que permite almacenar globalmente los errores que devuelve la funcion tokenize al momento de crear los tokens.

    5. Se crea la funcion tokenize que recibe el archivo .gox, donde por medio de un while se recorre el archivo caracter por caracter comparando cada caracter.

    5.1. Si se encuentra un caracter de espacio, estos se ignoran, como saltos de linea, tab, y espacios.

        5.2. Se ignoran los comentarios de bloque, y se guarda el error en la variable errors si se encuentra que no se cierra el comentario

        5.3. Se ignoran los comentarios de lina.

        5.4. Se identifican los nombres de variable y nombres de funciones,donde si el caracter actual del texto es igual a una letra o a un guion bajo "_" entra a realizar la identificacion.

        5.5. Se identifican los numeros tipo flotantes o tipo entero donde si el caracter actual del texto es igual a un digito o a un punto "." entra a realizar la identificacion del numero.

        5.6. Se identifica los valores de tipo caracter, donde si el caracter actual del texto es igual a "'" se valida si termina tambien con el mismo simbolo "'" y es un caracter de un byte. 

        5.7.  Se realizan las respectivas validaciones, donde se compara si el caracter actual del texto es un simbolo de dos caracter.

        5.8 Se realizan las respectivas validaciones, donde se compara si el caracter actual del texto es un simbolo de un caracter

    6. Funcion que imprime los errores que se encontraron en la funcion tokenize

    7. Funcion main que valida si se obtuvo el texto .gox y llama la funcion tokenize.

Estructura para llamar el analizador lexico desde la terminal:
    python analizador_lexico.py filename.gox

Estructura para llamar la conjunto de pruebas unitarias:
    python -m unittest test_tokenizer.py

# Desarrollo de la extencion de visual estudio code para resaltar la sintaxis del lenguaje gox

1. Para instalar la extensión, hay que ir a la ruta “C:\Users\USUARIO\.vscode\extensions” dentro de la carpeta “extensions” se crea una nueva carpeta para almacenar los archivos y subcarpetas de la extensión. En este caso se puede llamar “extensión-gox”. Lo único que queda por hacer es descomprimir el archivo zip con la extensión y reiniciar vscode para poder aplicar los cambios a las extensiones instaladas.
2. Durante el desarrollo de la extensión de resaltado de sintaxis para nuestro lenguaje, nos enfrentamos a varios desafíos técnicos que requirieron soluciones específicas para garantizar una correcta integración en Visual Studio Code.
Uno de los principales problemas fue el correcto reconocimiento y coloreado de los comentarios multilínea (/* ... */). Inicialmente, los operadores y palabras clave dentro de los comentarios seguían resaltándose con sus colores originales en lugar de mostrarse como texto neutro. Para solucionar esto, ajustamos la configuración de la gramática en el archivo gox.tmLanguage.json,ya que el problema estaba arraigado en el orden de declaración de la expresión de los comentarios dentro del archivo.
3. Otro aspecto que requirió ajustes fue la configuración de funciones adicionales en el editor, como el cierre automático de paréntesis y la capacidad de plegar y desplegar secciones de código. Dado que estas características no se pueden definir en el archivo de resaltado de sintaxis (gox.tmLanguage.json), fue necesario crear un archivo adicional de configuración (gox.configuration.json). Este archivo permite definir reglas específicas para el auto-cierre de símbolos como (), {}.



