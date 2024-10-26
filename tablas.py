from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QScrollArea, QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox, QAbstractItemView
from PyQt6.QtGui import QColor
from connection import get_tables, connect_to_database, get_databases, get_attributes, delete_table
from tablas_crear import CrearTablaFormulario
from tablas_modificar import ModificarAtributosDialog

class Tablas(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_db = None
        self.selected_table = None

        # Crear el layout principal horizontal
        main_layout = QHBoxLayout(self)

        # Crear la lista de bases de datos
        self.database_list = QListWidget()
        self.database_list.itemClicked.connect(self.on_database_selected)  # Conectar la señal de clic
        self.load_databases()  # Cargar bases de datos al inicio

        # Ajuste de tamaño del QListWidget según el contenido
        self.database_list.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)

        # Scrollbar para la lista
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(False)  # No queremos que el scroll area se redimensione
        left_scroll.setWidget(self.database_list)  # Poner la lista en el scroll area

        # Ajustar el tamaño máximo al de la lista
        self.adjust_scroll_size()

        # Layout derecho para mostrar las tablas
        right_layout = QVBoxLayout()

        # Layout derecho para las tablas
        self.tables_tree = QTreeWidget()
                
        self.tables_tree.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        
        # Ajuste de los encabezados para múltiples columnas
        self.tables_tree.setHeaderLabels(["Tabla", "Llave", "Tipo", "Extras"])
        
         # Conectar el evento de selección de tabla
        self.tables_tree.itemClicked.connect(self.on_table_selected)

        # Cambiar el color de fondo a blanco
        self.tables_tree.setStyleSheet("QTreeWidget { background-color: #f3f3f3; } QHeaderView { background-color: #f3f3f3; color: #000 }")

        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.tables_tree)

        # Añadir el scroll de tablas al layout derecho
        right_layout.addWidget(right_scroll)

        # Añadir los botones de Agregar, Eliminar y Modificar debajo de la tabla
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Agregar")
        self.delete_button = QPushButton("Eliminar")
        self.modify_button = QPushButton("Modificar")

        # Agregar los botones al layout
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.modify_button)

        # Conectar los botones a sus métodos correspondientes (placeholders)
        self.add_button.clicked.connect(self.add_table)
        self.delete_button.clicked.connect(self.delete_table)
        self.modify_button.clicked.connect(self.modify_table)

        # Añadir el layout de los botones debajo de las tablas
        right_layout.addLayout(buttons_layout)

        # Añadir ambos scrolls al layout principal
        main_layout.addWidget(left_scroll)  # Scroll izquierdo con lista de bases de datos
        main_layout.addLayout(right_layout, 1)  # Layout derecho con tablas y botones

        # Establecer el layout en el widget principal
        self.setLayout(main_layout)

    def on_database_selected(self, item):
        """Manejador para cuando se selecciona una base de datos."""
        self.selected_db = item.text()  # Guarda la base de datos seleccionada
        self.load_tables(self.selected_db)  # Cargar tablas de la base de datos seleccionada
        
    def on_table_selected(self, item):
        """Manejador para cuando se selecciona una tabla."""
        self.selected_table = item.text(0)
    
    def load_databases(self):
        databases = get_databases()  # Obtener bases de datos
        self.database_list.clear()  # Limpiar la lista existente

        # Agregar bases de datos a la lista
        for db in databases:
            self.database_list.addItem(db)

    def load_tables_2(self):
        return self.selected_db

    def load_tables(self, db_name):
        """Cargar las tablas de la base de datos seleccionada."""
                
        connection = connect_to_database(db_name)  # Conectar a la base de datos seleccionada
        if connection:
            self.tables_tree.clear()  # Limpiar la lista existente de tablas
            tables = get_tables(connection)  # Obtener las tablas usando la conexión

            for table in tables:
                table_item = QTreeWidgetItem(self.tables_tree)  # Crear item para la tabla
                table_item.setText(0, table)  # Nombre de la tabla en la primera columna
                table_item.setForeground(0, QColor("blue"))  # Azul para el nombre de la tabla

                # Obtener los atributos de la tabla
                attributes = get_attributes(connection, table)
                
                for attr in attributes:
                    attr_item = QTreeWidgetItem(table_item)

                    # Columna 0: Nombre del atributo
                    attr_item.setText(0, attr['name'])
                    attr_item.setForeground(0, QColor("green"))

                    # Columna 1: Llave (PK, FK o Regular)
                    attr_item.setText(1, attr['key_type'])  # Aquí debe mostrarse PK, FK o Regular
                    if attr['key_type'] == "PK":
                        attr_item.setForeground(1, QColor("gold"))
                    elif attr['key_type'] == "FK":
                        attr_item.setForeground(1, QColor("silver"))
                    else:
                        attr_item.setForeground(1, QColor("black"))

                    # Columna 2: Tipo de dato (VARCHAR, INT, etc.)
                    attr_item.setText(2, attr['col_type'])
                    attr_item.setForeground(2, QColor("orange"))

                    # Columna 3: Extras (Auto Increment, Length, Default)
                    attr_item.setText(3, attr['extras'])
                    attr_item.setForeground(3, QColor("darkGray"))

            # Ajustar el ancho de todas las columnas al contenido
            for i in range(self.tables_tree.columnCount()):
                self.tables_tree.resizeColumnToContents(i)

            # Ajustar un ancho mínimo para cada columna (en caso de que no haya contenido)
            self.tables_tree.setColumnWidth(0, 150)  # Nombre de la tabla
            self.tables_tree.setColumnWidth(1, 100)  # Llave (PK, FK)
            self.tables_tree.setColumnWidth(2, 120)  # Tipo de dato
            self.tables_tree.setColumnWidth(3, 180)  # Extras
            

    def adjust_scroll_size(self):
        """Ajusta el tamaño del scroll para la lista de bases de datos al tamaño de la lista."""
        self.database_list.setMaximumHeight(self.calculate_list_height())  # Ajustar el alto al contenido
        self.database_list.setMinimumHeight(self.calculate_list_height())  # Evitar que sea demasiado pequeño
        self.database_list.setMaximumWidth(self.calculate_list_width())  # Ajustar el ancho al contenido

    def calculate_list_height(self):
        """Calcula el alto necesario para contener todos los elementos de la lista."""
        total_height = 0
        for i in range(self.database_list.count()):
            total_height += self.database_list.sizeHintForRow(i)
        return total_height + 2 * self.database_list.frameWidth()  # Añadir margen

    def calculate_list_width(self):
        """Calcula el ancho de la lista basado en el tamaño del texto."""
        max_text_width = 0
        for i in range(self.database_list.count()):
            item = self.database_list.item(i)
            item_width = self.database_list.fontMetrics().boundingRect(item.text()).width()
            max_text_width = max(max_text_width, item_width)

        return min(int(self.width() * 0.5), max_text_width + 20)  # Limita al 50% del ancho de la ventana, añade margen

    def resizeEvent(self, event):
        """Ajusta el tamaño máximo del QListWidget cuando la ventana se redimensiona."""
        super().resizeEvent(event)
        self.adjust_scroll_size()  # Ajustar tamaño de la lista y scroll cuando la ventana cambia de tamaño
                
    # Placeholder para los métodos de los botones
    def add_table(self):
        if not self.selected_db:  # Verifica si hay una base de datos seleccionada
            QMessageBox.warning(self, "Error", "Debe seleccionar una base de datos.")
            return
        
        dialog = CrearTablaFormulario(self.selected_db)  # Pasa la instancia del padre (Tablas)
        if dialog.exec():
            # Recargar las tablas después de crear una nueva
            self.load_tables(self.selected_db)

    def delete_table(self):
        if not self.selected_db:  # Verifica si hay una base de datos seleccionada
            QMessageBox.warning(self, "Error", "Debe seleccionar una base de datos.")
            return
        
        selected_items = [item for item in self.tables_tree.selectedItems() if item.parent() is None]  # Solo tablas
        
        if not selected_items:
            QMessageBox.warning(self, "Error", "Debe seleccionar al menos una tabla.")
            return
        
        text = "¿Esta seguro de eliminar las tablas:\n\n" if len(selected_items) > 1 else "¿Esta seguro de eliminar la tabla: "
        text2 = "Se han eliminado las tablas exitosamente" if len(selected_items) > 1 else "Se ha eliminado la tabla exitosamente"
        
        tables_to_delete = [f'"{item.text(0)}"' for item in selected_items]
        print(tables_to_delete)
        reply = QMessageBox.question(
            self, 'Confirmación',
            f"{text}{', '.join(tables_to_delete)}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            for table_name in selected_items:
                delete_table(self.selected_db, table_name.text(0))  # Eliminar cada tabla seleccionada
                QMessageBox.information("Éxito", f"{text2}")
            self.load_tables(self.selected_db)

    def modify_table(self):
        if not self.selected_db:  # Verifica si hay una base de datos seleccionada
            QMessageBox.warning(self, "Error", "Debe seleccionar una base de datos.")
            return
        
        selected_items = [item for item in self.tables_tree.selectedItems() if item.parent() is None]  # Solo tablas
        
        if not selected_items:
            QMessageBox.warning(self, "Error", "Debe seleccionar una tabla.")
            return
        
        attributes = get_attributes(connect_to_database(self.selected_db), self.selected_table)
        
        print(attributes)
        
        dialog = ModificarAtributosDialog(attributes)  # Pasa la instancia del padre (Tablas)
        if dialog.exec():
            # Recargar las tablas después de crear una nueva
            self.load_tables(self.selected_db)

        