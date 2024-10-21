from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QWidget

class CrearTablaFormulario(QDialog):
    def __init__(self, selected_db):
        super().__init__()
        self.setWindowTitle("Crear Tabla")

        self.selected_db = selected_db  # Guardar la base de datos seleccionada

        layout_principal = QVBoxLayout(self)

        # Campo para el nombre de la tabla
        self.nombre_tabla_input = QLineEdit()
        layout_principal.addWidget(QLabel("Nombre de la tabla:"))
        layout_principal.addWidget(self.nombre_tabla_input)

        # SpinBox para el número de atributos
        self.num_atributos_spinbox = QSpinBox()
        self.num_atributos_spinbox.setMinimum(1)
        self.num_atributos_spinbox.valueChanged.connect(self.update_atributos)
        layout_principal.addWidget(QLabel("No. Atributos:"))
        layout_principal.addWidget(self.num_atributos_spinbox)

        # Tabla para atributos
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(7)  # Número de columnas (atributos)
        self.table_widget.setHorizontalHeaderLabels(["Nombre", "Tipo", "Longitud", "Predeterminado", "Nulo", "Autoincremento", "Llave"])
        layout_principal.addWidget(self.table_widget)

        # Botón para crear la tabla
        self.crear_tabla_btn = QPushButton("Crear Tabla")
        self.crear_tabla_btn.clicked.connect(self.crear_tabla)
        layout_principal.addWidget(self.crear_tabla_btn)

        self.setLayout(layout_principal)

        # Inicializar atributos
        self.update_atributos()

    def update_atributos(self):
        """Actualiza la tabla según el número seleccionado en el SpinBox."""
        num_atributos_nuevo = self.num_atributos_spinbox.value()
        self.table_widget.setRowCount(num_atributos_nuevo)  # Establece el número de filas en la tabla

        for row in range(num_atributos_nuevo):
            # Nombre
            nombre_widget = QLineEdit()
            self.table_widget.setCellWidget(row, 0, nombre_widget)

            # Tipo
            tipo_widget = QComboBox()
            tipo_widget.addItems(["INT", "VARCHAR", "TEXT", "DATE"])  # Agregar más tipos de datos si es necesario
            self.table_widget.setCellWidget(row, 1, tipo_widget)

            # Longitud
            longitud_widget = QLineEdit()
            self.table_widget.setCellWidget(row, 2, longitud_widget)

            # Predeterminado
            predeterminado_widget = QComboBox()
            predeterminado_widget.addItems(["NULL", "CURRENT_TIMESTAMP", ""])  # Valores predeterminados
            self.table_widget.setCellWidget(row, 3, predeterminado_widget)

            # Nulo
            nulo_widget = QCheckBox()
            self.table_widget.setCellWidget(row, 4, nulo_widget)

            # Autoincremento
            autoincremento_widget = QCheckBox()
            self.table_widget.setCellWidget(row, 5, autoincremento_widget)

            # Llave
            llave_widget = QComboBox()
            llave_widget.addItems(["", "PK", "FK"])
            self.table_widget.setCellWidget(row, 6, llave_widget)

    def crear_tabla(self):
        """Lógica para crear la tabla en la base de datos seleccionada."""
        table_name = self.nombre_tabla_input.text()
        if not table_name:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nombre para la tabla.")
            return

        num_attributes = self.num_atributos_spinbox.value()

        # Recolectar información de los atributos
        atributos = []
        for i in range(num_attributes):
            nombre = self.table_widget.cellWidget(i, 0).text() if self.table_widget.cellWidget(i, 0) else ""
            tipo = self.table_widget.cellWidget(i, 1).currentText() if self.table_widget.cellWidget(i, 1) else ""
            longitud = self.table_widget.cellWidget(i, 2).text() if self.table_widget.cellWidget(i, 2) else ""
            predeterminado = self.table_widget.cellWidget(i, 3).currentText() if self.table_widget.cellWidget(i, 3) else ""
            nulo = self.table_widget.cellWidget(i, 4) and self.table_widget.cellWidget(i, 4).isChecked()
            autoincremento = self.table_widget.cellWidget(i, 5) and self.table_widget.cellWidget(i, 5).isChecked()
            llave = self.table_widget.cellWidget(i, 6).currentText() if self.table_widget.cellWidget(i, 6) else ""

            # Verifica que el nombre de cada atributo no esté vacío
            if not nombre:
                QMessageBox.warning(self, "Error", f"El nombre del atributo {i + 1} está vacío.")
                return

            atributos.append({
                "nombre": nombre,
                "tipo": tipo,
                "longitud": longitud,
                "predeterminado": predeterminado,
                "nulo": nulo,
                "autoincremento": autoincremento,
                "llave": llave
            })

        # Aquí puedes agregar la lógica para crear la tabla en la base de datos utilizando self.selected_db
        print(f"Crear tabla {table_name} en la base de datos {self.selected_db} con atributos: {atributos}")
        self.accept()  # Cierra el diálogo si todo está correcto
