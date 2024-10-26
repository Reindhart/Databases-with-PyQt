from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QFrame, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction, QIcon
import sys
from crear_eliminar import DynamicTextInput
from respaldar_restaurar import Respaldar
from tablas import Tablas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bases de Datos")
        self.setGeometry(100, 100, 800, 600)

        # Establecer el icono de la ventana
        self.setWindowIcon(QIcon("favicon.ico"))

        # Crear el menú
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Crear acciones para el menú
        self.create_delete_action = QAction("Crear/Eliminar", self)
        self.create_delete_action.triggered.connect(self.show_create_delete_tab)

        self.backup_restore_action = QAction("Respaldar/Restaurar", self)
        self.backup_restore_action.triggered.connect(self.show_backup_restore_tab)

        self.tablas_action = QAction("Tablas", self)
        self.tablas_action.triggered.connect(self.show_tablas_tab)  # Conectar a la nueva función

        # Crear la acción de Recargar con un ícono en lugar de texto
        self.reload_action = QAction(self)
        self.reload_action.triggered.connect(self.reload_databases)
        self.set_reload_icon()  # Establecer el ícono dinámico

        # Agregar acciones al menú
        self.menu_bar.addAction(self.create_delete_action)
        self.menu_bar.addAction(self.backup_restore_action)
        self.menu_bar.addAction(self.tablas_action)
        self.menu_bar.addAction(self.reload_action)  # Acción solo con el ícono

        # Crear un widget contenedor para el layout
        self.container_widget = QWidget()
        self.setCentralWidget(self.container_widget)

        # Crear un layout vertical para contener la línea y el contenido
        self.layout = QVBoxLayout()

        # Crear una línea horizontal
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        # Agregar la línea al layout
        self.layout.addWidget(self.line)

        # Inicializar las pestañas
        self.current_widget = None
        self.show_create_delete_tab()  # Mostrar la pestaña de Crear/Eliminar al inicio

        # Establecer el layout en el widget contenedor
        self.container_widget.setLayout(self.layout)

        # Centrar ventana
        self.center()

    def set_reload_icon(self):
        # Detectar si el fondo es oscuro o claro
        palette = self.palette()
        background_color = palette.color(palette.ColorRole.Window)
        is_dark_theme = background_color.value() < 128  # Valor bajo = oscuro

        # Cargar el archivo SVG
        icon_path = "reload.svg"

        # Crear el ícono dependiendo del tema
        if is_dark_theme:
            icon = QIcon("reload-dark.svg")  # Cambiar color a blanco si es tema oscuro
            self.reload_action.setIcon(icon)
        else:
            icon = QIcon("reload-light.svg")  # Cambiar color a negro si es tema claro
            self.reload_action.setIcon(icon)

    def show_create_delete_tab(self):
        if self.current_widget is not None:
            self.current_widget.deleteLater()  # Eliminar el widget actual

        self.current_widget = DynamicTextInput()  # Crear nueva instancia
        self.layout.addWidget(self.current_widget)  # Agregar al layout debajo de la línea

    def show_backup_restore_tab(self):
        if self.current_widget is not None:
            self.current_widget.deleteLater()  # Eliminar el widget actual

        self.current_widget = Respaldar()  # Crear nueva instancia
        self.layout.addWidget(self.current_widget)  # Agregar al layout debajo de la línea

    def show_tablas_tab(self):
        if self.current_widget is not None:
            self.current_widget.deleteLater()  # Eliminar el widget actual

        self.current_widget = Tablas()  # Crear nueva instancia desde tablas.py
        self.layout.addWidget(self.current_widget)  # Agregar al layout debajo de la línea

    def reload_databases(self):
        if self.current_widget is not None:
            self.current_widget.load_databases()  # Recargar las bases de datos en el widget actual
        if isinstance(self.current_widget, Tablas):
            if(self.current_widget.load_tables_2()):
                self.current_widget.load_tables(self.current_widget.load_tables_2())
                        
    def center(self):
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
