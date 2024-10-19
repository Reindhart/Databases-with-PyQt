from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QScrollArea, QTreeWidget, QTreeWidgetItem
from connection import get_databases, get_tables  # Asegúrate de que tienes esta función para obtener tablas

class Tablas(QWidget):
    def __init__(self):
        super().__init__()

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
        self.tables_tree = QTreeWidget()
        self.tables_tree.setHeaderLabels(["Tablas"])

        right_layout = QVBoxLayout()
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.tables_tree)

        # Añadir ambos scrolls al layout principal
        main_layout.addWidget(left_scroll)  # Scroll izquierdo con lista de bases de datos
        main_layout.addWidget(right_scroll, 1)  # Scroll derecho

        # Establecer el layout en el widget principal
        self.setLayout(main_layout)

    def load_databases(self):
        databases = get_databases()  # Obtener bases de datos
        self.database_list.clear()  # Limpiar la lista existente

        # Agregar bases de datos a la lista
        for db in databases:
            self.database_list.addItem(db)

    def on_database_selected(self, item):
        """Manejador para cuando se selecciona una base de datos."""
        selected_db = item.text()
        self.load_tables(selected_db)  # Cargar tablas de la base de datos seleccionada

    def load_tables(self, db_name):
        """Cargar las tablas de la base de datos seleccionada."""
        self.tables_tree.clear()  # Limpiar la lista existente de tablas
        tables = get_tables(db_name)  # Obtener tablas de la base de datos

        # Agregar tablas al QTreeWidget
        for table in tables:
            QTreeWidgetItem(self.tables_tree, [table])  # Agregar tabla al árbol

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
