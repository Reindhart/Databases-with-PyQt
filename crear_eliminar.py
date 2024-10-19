from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QScrollArea, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QSizePolicy, QHeaderView
)
from PyQt6.QtGui import QColor, QBrush, QIcon
from PyQt6.QtCore import QSize
import re
from connection import create_database, drop_database, get_databases

class DynamicTextInput(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QFrame(self.scroll_area)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.scroll_area)

        self.add_button = QPushButton("Crear Base de Datos", self)
        self.add_button.clicked.connect(self.add_to_list)
        left_layout.addWidget(self.add_button)

        self.table_scroll_area = QScrollArea(self)
        self.table_scroll_area.setWidgetResizable(True)
        self.table_widget_container = QFrame(self.table_scroll_area)
        self.table_widget_layout = QVBoxLayout(self.table_widget_container)

        self.table_widget = QTableWidget(self.table_widget_container)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Bases de Datos", ""])

        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table_widget.setColumnWidth(1, 10)

        self.table_widget_layout.addWidget(self.table_widget)
        self.table_widget_container.setLayout(self.table_widget_layout)
        self.table_scroll_area.setWidget(self.table_widget_container)

        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.table_scroll_area)

        self.text_inputs = []
        self.load_databases()
        self.add_text_input()

    def load_databases(self):
        self.table_widget.setRowCount(0)
        databases = get_databases()
        for database in databases:
            self.add_row_to_table(database)

    def add_row_to_table(self, database_name):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        name_item = QTableWidgetItem(database_name)
        self.table_widget.setItem(row_position, 0, name_item)

        delete_button = QPushButton(self)
        delete_button.setIcon(QIcon('delete.png'))
        delete_button.setIconSize(QSize(24, 24))
        delete_button.setFixedSize(QSize(24, 24))
        delete_button.clicked.connect(lambda: self.delete_database(database_name))

        self.table_widget.setCellWidget(row_position, 1, delete_button)
        delete_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        if row_position % 2 == 0:
            name_item.setBackground(QColor(220, 220, 220))
        else:
            name_item.setBackground(QColor(255, 255, 255))

        name_item.setForeground(QBrush(QColor(0, 0, 0)))

    def delete_database(self, database_name):
        try:
            # Eliminar la base de datos en el servidor
            drop_database(database_name)

            # Buscar la fila que corresponde al nombre de la base de datos
            row_count = self.table_widget.rowCount()
            found_row = -1
            
            # Recorrer la tabla para encontrar la fila correspondiente al nombre
            for row in range(row_count):
                item = self.table_widget.item(row, 0)  # Columna de nombres (columna 0)
                if item and item.text() == database_name:
                    found_row = row
                    break  # Rompemos el bucle una vez encontramos la fila correcta
            
            # Verificar que se encontró una fila
            if found_row != -1:
                # Eliminar la fila encontrada
                self.table_widget.removeRow(found_row)
                # Asegurarse de que la tabla se actualice visualmente
                self.table_widget.repaint()
            else:
                QMessageBox.warning(self, "Advertencia", f"No se encontró la base de datos '{database_name}' en la tabla.")
        
        except Exception as err:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la base de datos: {err}")

    def add_text_input(self):
        new_input = QLineEdit(self)
        new_input.setPlaceholderText('Escribe el nombre de la base de datos...')
        new_input.textChanged.connect(self.on_text_changed)
        self.content_layout.addWidget(new_input)
        self.text_inputs.append(new_input)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_text_changed(self, text):
        if text:
            sender = self.sender()
            sender.textChanged.disconnect()
            self.add_text_input()

    def is_valid_database_name(self, name):
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None

    def add_to_list(self):
        names_to_create = []
        for input_field in self.text_inputs:
            input_value = input_field.text().strip()
            if input_value:
                if self.is_valid_database_name(input_value):
                    names_to_create.append(input_value)
                else:
                    QMessageBox.warning(self, "Advertencia", f"El nombre de la base de datos '{input_value}' es inválido.")
                    return

        if not names_to_create:
            QMessageBox.warning(self, "Advertencia", "Escriba un nombre para la base de datos.")
            return

        for name in names_to_create:
            try:
                create_database(name)
                self.add_row_to_table(name)
            except Exception as err:
                QMessageBox.critical(self, "Error", f"No se pudo crear la base de datos '{name}': {err}")

        # Limpiar las entradas de texto y restablecer a solo una
        for input_field in self.text_inputs:
            input_field.deleteLater()  # Eliminar el widget de la interfaz

        self.text_inputs.clear()  # Limpiar la lista de entradas
        self.add_text_input()  # Agregar una nueva entrada de texto
        self.text_inputs[0].setFocus()  # Enfocar la nueva entrada

    def center(self):
        # Obtener el tamaño de la pantalla y calcular el centro
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())