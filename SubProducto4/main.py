import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)
        self.setWindowTitle("Analizador Léxico, Sintáctico y Semántico con Calculadora")

        # Conectar los botones con los métodos respectivos
        self.pushButton.clicked.connect(self.iniciar_analisis_lexico)
        self.pushButton_2.clicked.connect(self.iniciar_analisis_sintactico)
        self.pushButton_3.clicked.connect(self.iniciar_analisis_semantico)
        self.pushButtonfile.clicked.connect(self.obtener_archivo)
        self.pushButton_4.clicked.connect(self.compilacion)

        # Configurar la tabla para el análisis léxico
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Lexema", "Token", "#"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)

        # Diccionario para almacenar las variables y sus valores
        self.variables = {}

    def obtener_archivo(self):
        options = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir archivo de texto", "", "Text Files (*.txt)", options=options)
        if archivo:
            with open(archivo, 'r') as file:
                content = file.read()
                self.plainTextEdit_2.appendPlainText(content)

    def iniciar_analisis_lexico(self):
        texto = self.plainTextEdit_2.toPlainText()
        palabras_reservadas = ["int", "float", "void", "if", "while", "return", "else"]
        operadores = ['+', '-', '*', '=', '/', '<', '<=', '>', '>=', '==', '!=', '&&', '||']
        delimitadores = ['(', ')', '{', '}', ';', ',']
        
        resultados = []
        i = 0
        while i < len(texto):
            c = texto[i]
            if c.isspace():
                i += 1
                continue
            if c.isalpha():
                inicio = i
                while i < len(texto) and (texto[i].isalnum() or texto[i] == '_'):
                    i += 1
                token = texto[inicio:i]
                if token in palabras_reservadas:
                    resultados.append([token, "Palabra reservada", 4])
                else:
                    resultados.append([token, "Identificador", 0])
                continue
            elif c.isdigit():
                inicio = i
                tiene_punto = False
                while i < len(texto) and (texto[i].isdigit() or (texto[i] == '.' and not tiene_punto)):
                    if texto[i] == '.':
                        tiene_punto = True
                    i += 1
                token = texto[inicio:i]
                if tiene_punto:
                    resultados.append([token, "Número real", 2])
                else:
                    resultados.append([token, "Número entero", 1])
                continue
            elif c in operadores:
                if i + 1 < len(texto) and texto[i:i+2] in operadores:
                    resultados.append([texto[i:i+2], "Operador", 7])
                    i += 2
                else:
                    resultados.append([c, "Operador", 7])
                    i += 1
                continue
            elif c in delimitadores:
                resultados.append([c, "Delimitador", 12])
                i += 1
                continue
            else:
                resultados.append([c, "Error léxico", 6])
                i += 1

        self.tableWidget.setRowCount(0)
        for fila in resultados:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            for columna, item in enumerate(fila):
                self.tableWidget.setItem(row_position, columna, QTableWidgetItem(str(item)))

    def iniciar_analisis_sintactico(self):
        texto = self.plainTextEdit_2.toPlainText().splitlines()
        errores = []
        function_declaration = False

        for num_linea, linea in enumerate(texto, start=1):
            linea = linea.strip()
            if linea.startswith("int main()"):
                function_declaration = True
                continue
            if function_declaration:
                if linea.startswith("{"):
                    function_declaration = False
                    continue
                errores.append(f"Error en la línea {num_linea}: falta '{{' después de 'int main()'.")
                function_declaration = False
            if not linea:
                continue
            if linea.startswith(("int", "float", "void")):
                if not linea.endswith(";"):
                    errores.append(f"Error en la línea {num_linea}: falta ';' al final de la declaración.")
                else:
                    tokens = linea.split()
                    if len(tokens) >= 2:
                        tipo = tokens[0]
                        variable = tokens[1].replace(";", "")
                        self.variables[variable] = 0  # Inicializamos la variable con valor 0

            elif "=" in linea:
                if not linea.endswith(";"):
                    errores.append(f"Error en la línea {num_linea}: falta ';' al final de la asignación.")
                tokens = linea.replace(";", "").split()
                for token in tokens:
                    if token.isidentifier() and token not in self.variables:
                        errores.append(f"Error en la línea {num_linea}: variable '{token}' no está declarada.")

        self.plainTextEdit_3.clear()
        if errores:
            for error in errores:
                self.plainTextEdit_3.appendPlainText(error)
        else:
            self.plainTextEdit_3.appendPlainText("Análisis sintáctico completado: no se encontraron errores.")

    def iniciar_analisis_semantico(self):
        texto = self.plainTextEdit_2.toPlainText().splitlines()
        errores = []

        # Limpia el texto de errores previos
        self.plainTextEdit_4.clear()

        for num_linea, linea in enumerate(texto, start=1):
            tokens = linea.replace(";", "").replace("(", "").replace(")", "").split()
            if "=" in linea:
                partes = linea.split("=")
                variable = partes[0].strip().lower()
                valor = partes[1].strip().replace(";", "")

                # Verifica si la variable fue declarada
                if variable not in self.variables:
                    errores.append(f"Error en la línea {num_linea}: variable '{variable}' no está declarada.")
                else:
                    tipo_variable = self.variables[variable]
                    # Verifica compatibilidad de tipos
                    if tipo_variable == "int" and any(c in valor for c in ".eE"):
                        errores.append(f"Error en la línea {num_linea}: tipo incompatible, asignación de flotante a 'int'.")
                    else:
                        # Calcula el resultado y actualiza la variable
                        resultado = self.calculadora(valor)
                        if resultado is not None:
                            self.variables[variable] = resultado
                            self.plainTextEdit_4.appendPlainText(f"Resultado de '{variable} = {valor}': {resultado}")

        if errores:
            for error in errores:
                self.plainTextEdit_4.appendPlainText(error)
        else:
            self.plainTextEdit_4.appendPlainText("Análisis semántico completado: no se encontraron errores.")

    def calculadora(self, expresion):
        try:
            # Reemplaza las variables en la expresión por sus valores
            for var, val in self.variables.items():
                expresion = expresion.replace(var, str(val))
            
            # Evalúa la expresión matemática
            resultado = eval(expresion)

            # Muestra el resultado en el plainTextEdit_6
            self.plainTextEdit_6.appendPlainText(f"Resultado de '{expresion}': {resultado}")
            return resultado
        except ZeroDivisionError:
            self.plainTextEdit_6.appendPlainText("Error: División por cero.")
            return None
        except Exception as e:
            self.plainTextEdit_6.appendPlainText(f"Error en la expresión '{expresion}': {e}")
            return None


    def compilacion(self):
        texto = self.plainTextEdit_2.toPlainText().splitlines()
        codigo_ensamblador = [
            "; Programa generado en ensamblador EMU8086",
            ".MODEL SMALL",
            ".STACK 100h",
            ".DATA",
        ]
        
        variables = {}
        direccion_actual = 0x400  # Dirección inicial en 400h

        # Declarar las variables en la sección .DATA
        for num_linea, linea in enumerate(texto, start=1):
            linea = linea.strip()
            if linea.startswith("int "):  # Declaración de variables
                var = linea.split()[1].replace(";", "")
                if var not in variables:
                    variables[var] = f"[{hex(direccion_actual).upper()}]"
                    codigo_ensamblador.append(f"{var} DW ? ; {hex(direccion_actual).upper()}")
                    direccion_actual += 2  # Cada variable ocupa 2 bytes

        codigo_ensamblador.append("\n.CODE")
        codigo_ensamblador.append("START:")
        codigo_ensamblador.append("MOV AX, @DATA")
        codigo_ensamblador.append("MOV DS, AX\n")

        # Generar instrucciones ensamblador para las operaciones
        for num_linea, linea in enumerate(texto, start=1):
            linea = linea.strip()
            if "=" in linea:  # Operaciones de asignación
                var, expresion = linea.split("=")
                var = var.strip()
                expresion = expresion.strip().replace(";", "")

                try:
                    # Asumimos que la expresión es una operación aritmética simple
                    tokens = expresion.split()
                    if len(tokens) == 1:  # Asignación directa, ej. x = 5
                        if tokens[0].isdigit():  # Es un número
                            codigo_ensamblador.append(f"MOV AX, {tokens[0]}")
                            codigo_ensamblador.append(f"MOV {variables[var]}, AX")
                        elif tokens[0] in variables:  # Es una variable
                            codigo_ensamblador.append(f"MOV AX, {variables[tokens[0]]}")
                            codigo_ensamblador.append(f"MOV {variables[var]}, AX")
                    elif len(tokens) == 3:  # Operación binaria, ej. x = a + b
                        op1, oper, op2 = tokens
                        if op1.isdigit():
                            codigo_ensamblador.append(f"MOV AX, {op1}")
                        else:
                            codigo_ensamblador.append(f"MOV AX, {variables[op1]}")
                        
                        if op2.isdigit():
                            codigo_ensamblador.append(f"MOV BX, {op2}")
                        else:
                            codigo_ensamblador.append(f"MOV BX, {variables[op2]}")

                        if oper == "+":
                            codigo_ensamblador.append("ADD AX, BX")
                        elif oper == "-":
                            codigo_ensamblador.append("SUB AX, BX")
                        elif oper == "*":
                            codigo_ensamblador.append("MUL BX")
                        elif oper == "/":
                            codigo_ensamblador.append("MOV DX, 0")  # Limpiar DX para la división
                            codigo_ensamblador.append("DIV BX")
                        
                        codigo_ensamblador.append(f"MOV {variables[var]}, AX")
                    else:
                        codigo_ensamblador.append(f"; ERROR: No se reconoce la expresión '{expresion}'")
                except KeyError as e:
                    codigo_ensamblador.append(f"; ERROR: Variable no definida {e}")
                except Exception as e:
                    codigo_ensamblador.append(f"; ERROR: {str(e)}")

        # Finalización del programa
        codigo_ensamblador.append("\nMOV AH, 4Ch")
        codigo_ensamblador.append("INT 21h")
        codigo_ensamblador.append("END START")

        # Mostrar el código ensamblador generado
        self.plainTextEdit_5.clear()
        self.plainTextEdit_5.appendPlainText("\n".join(codigo_ensamblador))

# Ejecutar la aplicación
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())