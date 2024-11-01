from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox, 
                             QPushButton, QVBoxLayout, QTableWidget, QMessageBox, 
                             QHBoxLayout, QHeaderView, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from connection import create_table

class CrearTablaFormulario(QDialog):
    def __init__(self, selected_db):
        super().__init__()
        self.setWindowTitle("Crear Tabla")

        self.selected_db = selected_db  # Guardar la base de datos seleccionada
        self.setGeometry(100, 100, 850, 300)

        layout_principal = QVBoxLayout(self)

        # Layout horizontal para nombre de la tabla y número de atributos
        top_layout = QHBoxLayout()

        # Campo para el nombre de la tabla
        self.nombre_tabla_input = QLineEdit()
        top_layout.addWidget(QLabel("Nombre de la tabla:"))
        top_layout.addWidget(self.nombre_tabla_input)

        # SpinBox para el número de atributos
        self.num_atributos_spinbox = QSpinBox()
        self.num_atributos_spinbox.setMinimum(1)
        self.num_atributos_spinbox.valueChanged.connect(self.update_atributos)
        top_layout.addWidget(QLabel("No. Atributos:"))
        top_layout.addWidget(self.num_atributos_spinbox)

        # Añadir el layout horizontal al layout principal
        layout_principal.addLayout(top_layout)

        # Tabla para atributos
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(7)  # Número de columnas (atributos)
        self.table_widget.setHorizontalHeaderLabels(["Nombre", "Tipo", "Longitud", "Predeterminado", "Nulo", "A.I", "Llave"])
        self.table_widget.setColumnWidth(4, 10)
        self.table_widget.setColumnWidth(5, 10)
        layout_principal.addWidget(self.table_widget)

        # Botón para crear la tabla
        self.crear_tabla_btn = QPushButton("Crear Tabla")
        self.crear_tabla_btn.clicked.connect(self.crear_tabla)
        layout_principal.addWidget(self.crear_tabla_btn)

        self.setLayout(layout_principal)

        # Centrar ventana
        self.center()

        # Inicializar atributos
        self.update_atributos()

    def update_atributos(self):
        """Actualiza la tabla según el número seleccionado en el SpinBox."""
        num_atributos_nuevo = self.num_atributos_spinbox.value()
        self.table_widget.setRowCount(num_atributos_nuevo)

        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        for row in range(num_atributos_nuevo):
            if not self.table_widget.cellWidget(row, 0):
                # Nombre
                nombre_widget = QLineEdit()
                self.table_widget.setCellWidget(row, 0, nombre_widget)

                # Tipo con categorías
                tipo_widget = self.create_categorized_combobox()
                self.table_widget.setCellWidget(row, 1, tipo_widget)

                # Longitud
                longitud_widget = QLineEdit()
                self.table_widget.setCellWidget(row, 2, longitud_widget)

                # Predeterminado
                predeterminado_widget = QComboBox()
                predeterminado_widget.addItems(["Ninguno", "NULL", "CURRENT_TIMESTAMP"])
                self.table_widget.setCellWidget(row, 3, predeterminado_widget)

                # Nulo
                nulo_widget = QCheckBox()
                predeterminado_widget.currentIndexChanged.connect(lambda idx, pw=predeterminado_widget, nw=nulo_widget: self.sync_null_with_predeterminado(pw, nw))
                nulo_widget.stateChanged.connect(lambda state, pw=predeterminado_widget, nw=nulo_widget: self.sync_predeterminado_with_null(pw, nw))
                nulo_container = QWidget()
                nulo_layout = QHBoxLayout(nulo_container)
                nulo_layout.addWidget(nulo_widget)
                nulo_layout.setAlignment(nulo_widget, Qt.AlignmentFlag.AlignCenter)
                nulo_layout.setContentsMargins(0, 0, 0, 0)
                self.table_widget.setCellWidget(row, 4, nulo_container)

                # Autoincremento
                autoincremento_widget = QCheckBox()
                autoincremento_container = QWidget()
                autoincremento_layout = QHBoxLayout(autoincremento_container)
                autoincremento_layout.addWidget(autoincremento_widget)
                autoincremento_layout.setAlignment(autoincremento_widget, Qt.AlignmentFlag.AlignCenter)
                autoincremento_layout.setContentsMargins(0, 0, 0, 0)
                self.table_widget.setCellWidget(row, 5, autoincremento_container)

                # Llave
                llave_widget = QComboBox()
                llave_widget.addItems(["", "PRIMARY", "UNIQUE", "INDEX", "FULLTEXT", "SPATIAL"])
                self.table_widget.setCellWidget(row, 6, llave_widget)

    def sync_null_with_predeterminado(self, predeterminado_widget, nulo_widget):
        """Sincroniza el checkbox de 'Nulo' con la opción 'NULL' en el campo 'Predeterminado'."""
        if predeterminado_widget.currentText() == "NULL":
            nulo_widget.setChecked(True)

    def sync_predeterminado_with_null(self, predeterminado_widget, nulo_widget):
        """Sincroniza el valor del campo 'Predeterminado' cuando se desactiva 'Nulo'."""
        if not nulo_widget.isChecked() and predeterminado_widget.currentText() == "NULL":
            predeterminado_widget.setCurrentText("Ninguno")
              
    def save_current_data(self):
        """Guarda temporalmente los datos ingresados en la tabla."""
        atributos = []
        num_filas = self.table_widget.rowCount()

        for i in range(num_filas):
            nombre = self.table_widget.cellWidget(i, 0).text() if self.table_widget.cellWidget(i, 0) else ""
            tipo = self.table_widget.cellWidget(i, 1).currentText() if self.table_widget.cellWidget(i, 1) else ""
            longitud = self.table_widget.cellWidget(i, 2).text() if self.table_widget.cellWidget(i, 2) else ""
            predeterminado = self.table_widget.cellWidget(i, 3).currentText() if self.table_widget.cellWidget(i, 3) else ""
            
            nulo_widget = self.table_widget.cellWidget(i, 4).layout().itemAt(0).widget() if self.table_widget.cellWidget(i, 4) else None
            nulo = nulo_widget.isChecked() if nulo_widget else False

            autoincremento_widget = self.table_widget.cellWidget(i, 5).layout().itemAt(0).widget() if self.table_widget.cellWidget(i, 5) else None
            autoincremento = autoincremento_widget.isChecked() if autoincremento_widget else False
            
            llave = self.table_widget.cellWidget(i, 6).currentText() if self.table_widget.cellWidget(i, 6) else ""

            atributos.append({
                "nombre": nombre,
                "tipo": tipo,
                "longitud": longitud,
                "predeterminado": predeterminado,
                "nulo": nulo,
                "autoincremento": autoincremento,
                "llave": llave
            })
        return atributos

    def restore_data(self, atributos):
        """Restaura los datos previamente guardados en la tabla."""
        for i, atributo in enumerate(atributos):
            if i < self.table_widget.rowCount():
                self.table_widget.cellWidget(i, 0).setText(atributo["nombre"])
                self.table_widget.cellWidget(i, 1).setCurrentText(atributo["tipo"])
                self.table_widget.cellWidget(i, 2).setText(atributo["longitud"])
                self.table_widget.cellWidget(i, 3).setCurrentText(atributo["predeterminado"])
                nulo_widget = self.table_widget.cellWidget(i, 4).layout().itemAt(0).widget()
                
                if isinstance(nulo_widget, QCheckBox):
                    nulo_widget.setChecked(atributo["nulo"])

                autoincremento_widget = self.table_widget.cellWidget(i, 5).layout().itemAt(0).widget()
                if isinstance(autoincremento_widget, QCheckBox):
                    autoincremento_widget.setChecked(atributo["autoincremento"])

                self.table_widget.cellWidget(i, 6).setCurrentText(atributo["llave"])

    def create_categorized_combobox(self):
        combo = QComboBox()

        # Crear un modelo para manejar las categorías y subcategorías
        model = QStandardItemModel()

        for data_type in ["INT", "VARCHAR", "TEXT", "DATE"]:
            item = QStandardItem(data_type)
            model.appendRow(item)

        # Categoría numérica
        categories = {
            "--Numeric--": ["TINYINT", "SMALLINT", "MEDIUMINT", "INT", "BIGINT", "DECIMAL", "FLOAT", "DOUBLE", "REAL", "BIT", "BOOLEAN", "SERIAL"],
            "--String--": ["CHAR", "VARCHAR", "TINYTEXT", "TEXT", "MEDIUMTEXT", "LONGTEXT", "BINARY" , "VARBINARY", "TINYBLOB", "BLOB", "MEDIUMBLOB", "LONGBLOB", "ENUM", "SET"],
            "--Date--": ["DATE", "DATETIME", "TIMESTAMP", "TIME", "YEAR"],
            "--Spatial--": ["GEOMETRY", "POINT", "LINESTRING", "POLYGON", "MULTIPOINT", "MULTILINESTRING", "MULTIPOLYGON", "GEOMETRYCOLLECTION"],
            "--JSON--": ["JSON"]
        }

        for category, types in categories.items():
            item = QStandardItem(category)
            item.setFlags(Qt.ItemFlag.NoItemFlags & ~Qt.ItemFlag.ItemIsEnabled)
            model.appendRow(item)
            for data_type in types:
                model.appendRow(QStandardItem(data_type))

        combo.setModel(model)

        # Estilo para evitar el resaltado de fondo al pasar el mouse
        combo.setStyleSheet("""
            QComboBox QAbstractItemView::item:disabled {
                background: transparent; /* Sin color de fondo para las categorías */
            }
        """)

        return combo

    def crear_tabla(self):
        """Lógica para crear la tabla en la base de datos seleccionada."""
        table_name = self.nombre_tabla_input.text().strip()
        if not table_name:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nombre para la tabla.")
            return

        num_attributes = self.num_atributos_spinbox.value()
        
        # Recolectar información de los atributos
        lista_atributos = []
        
        for i in range(num_attributes):
            nombre = self.table_widget.cellWidget(i, 0).text().strip()
            tipo = self.table_widget.cellWidget(i, 1).currentText()
            longitud = self.table_widget.cellWidget(i, 2).text().strip()
            predeterminado = self.table_widget.cellWidget(i, 3).currentText()
            nulo_widget = self.table_widget.cellWidget(i, 4).layout().itemAt(0).widget()
            nulo = "NULL" if nulo_widget.isChecked() else "NOT NULL"
            autoincremento_widget = self.table_widget.cellWidget(i, 5).layout().itemAt(0).widget()
            autoincremento = "AUTO_INCREMENT" if autoincremento_widget.isChecked() else ""
            llave = self.table_widget.cellWidget(i, 6).currentText()

            # Sí no tiene nombre no se toma en cuenta
            if not nombre:
                continue
            
            atributo = [nombre, tipo, longitud, predeterminado, nulo, autoincremento, llave]
            lista_atributos.append(atributo)

        if(create_table(self.selected_db ,self.generar_sql(table_name, lista_atributos)) == ""):
            QMessageBox.information(self, "Creación de tabla", f"Se ha creado la tabla \"{table_name}\" exitosamente.")
        else:
            QMessageBox.warning(self, "Error:", f"No se ha podido crear la tabla \"{table_name}\".\n\n {create_table(self.selected_db ,self.generar_sql(table_name, lista_atributos))}")

        self.accept()  # Cierra el diálogo si todo está correcto

    def generar_sql(self, nombre_tabla, lista_atributos):
        """Genera una sentencia SQL para crear una tabla, con validaciones."""
        # Validar el nombre de la tabla
        if not nombre_tabla.isidentifier():
            QMessageBox.warning(self, "Error", f"El nombre de la tabla '{nombre_tabla}' no es válido.")
            return 
        
        # Lista para almacenar las partes del SQL
        columnas_sql = []
        key_column_sql = []

        # Diccionario para manejar tipos que soportan CURRENT_TIMESTAMP
        tipos_timestamp = {"TIMESTAMP", "DATETIME"}
        sql_reserved_keywords = {"SELECT", "INSERT", "UPDATE", "DELETE", "TABLE", "FROM", "WHERE", "JOIN"}


        # Recorrer los atributos y generar las columnas
        for atributo in lista_atributos:
            nombre = atributo[0]
            tipo = atributo[1]
            longitud = atributo[2]
            predeterminado = atributo[3]
            nulo = atributo[4]
            autoincremento = atributo[5]
            llave = atributo[6]

#---------------------------------------------------------

            # NOMBRE DE TABLA

            # Validar nombre del atributo
            if not nombre.isidentifier() or nombre.upper() in sql_reserved_keywords:
                QMessageBox.warning(self, "Error", f"Error: El nombre del atributo '{nombre}' no es válido o es una palabra reservada de SQL.")
                return

            # Generar la definición del atributo
            columna_sql = f"`{nombre}` {tipo}"

#---------------------------------------------------------

            # LONGITUD

            if tipo.upper() == "VARCHAR" and longitud == "":
                return f"Error: El atributo {nombre} requiere una longitud"

            if not longitud == "":
                if not longitud.isdigit():
                    return f"Error: El atributo '{nombre}' requiere una longitud válida. (Solo números)"
                if int(longitud) <= 0 or int(longitud) >255:
                    return f"Error: La longitud del atributo '{nombre}' debe ser mayor que 0 y menor que 255."            
                columna_sql += f"({longitud})"
            

#---------------------------------------------------------

            # PREDETERMINADO Y NULO
            
            columna_sql += f" {nulo}"

            # Validar la columna que usa CURRENT_TIMESTAMP
            if predeterminado == "CURRENT_TIMESTAMP" and tipo.upper() not in tipos_timestamp:
                return f"Error: El tipo de dato '{tipo}' no soporta CURRENT_TIMESTAMP en el atributo '{nombre}'."

            # Validar valor predeterminado si no permite NULL
            if predeterminado and not nulo:
                if tipo.upper() in ["INT", "BIGINT", "FLOAT", "DOUBLE"] and not predeterminado.isdigit():
                    return f"Error: El valor predeterminado para el atributo '{nombre}' debe ser un número válido."
                if tipo.upper() in ["VARCHAR", "CHAR"] and predeterminado and not (predeterminado.startswith("'") and predeterminado.endswith("'")):
                    return f"Error: El valor predeterminado para el atributo '{nombre}' debe estar entre comillas para los tipos de cadena."
                
                # Añadir valor predeterminado
                if predeterminado != "NULL":
                    columna_sql += f" DEFAULT {predeterminado}"
            
            elif predeterminado != "Ninguno":
                columna_sql += f" DEFAULT {predeterminado}"

            
#---------------------------------------------------------

            # AUTO INCREMENTO

            # Añadir autoincremento si corresponde
            if autoincremento:
                if tipo.upper() != "INT":
                    return f"Error: El atributo '{nombre}' tiene autoincremento, pero no es de tipo INT."
                columna_sql += " AUTO_INCREMENT"


#---------------------------------------------------------

            # LLAVES

            if llave != "":               
                key_sql = f"{llave} KEY (`{nombre}`)" if llave == "PRIMARY" else f"{llave}  (`{nombre}`)"
                key_column_sql.append(key_sql)
                

#---------------------------------------------------------

            # AGREGAR ATRIBUTO A LISTA DE ATRIBUTOS

            columnas_sql.append(columna_sql)


        # Generar la sentencia completa
        sql = (f"CREATE TABLE `{self.selected_db}`.`{nombre_tabla}` (\n    "
           + ",\n    ".join(columnas_sql))
    
        if key_column_sql:  # Solo agregar si hay llaves
            sql += ",\n    " + ",\n    ".join(key_column_sql)

        sql += "\n);"

        return sql
    
    def center(self):
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())