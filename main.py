from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar
from PyQt6.QtGui import QAction, QIcon
import sys
from crear_eliminar import DynamicTextInput
from respaldar_restaurar import Respaldar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bases de Datos")
        self.setGeometry(100, 100, 800, 600)

        # Establecer el icono de la ventana
        self.setWindowIcon(QIcon("favicon.ico"))  # Asegúrate de que el archivo esté en el mismo directorio

        # Crear el menú
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Crear acciones para el menú
        self.create_delete_action = QAction("Crear/Eliminar", self)
        self.create_delete_action.triggered.connect(self.show_create_delete_tab)

        self.backup_restore_action = QAction("Respaldar/Restaurar", self)
        self.backup_restore_action.triggered.connect(self.show_backup_restore_tab)

        self.reload_action = QAction("Recargar", self)
        self.reload_action.triggered.connect(self.reload_databases)

        # Agregar acciones al menú
        self.menu_bar.addAction(self.create_delete_action)
        self.menu_bar.addAction(self.backup_restore_action)
        self.menu_bar.addAction(self.reload_action)

        # Inicializar las pestañas
        self.current_widget = None
        self.show_create_delete_tab()  # Mostrar la pestaña de Crear/Eliminar al inicio

        self.center()  # Llamar a la función para centrar la ventana

    def show_create_delete_tab(self):
        if self.current_widget is not None:
            self.current_widget.deleteLater()  # Eliminar el widget actual

        self.current_widget = DynamicTextInput()  # Crear nueva instancia
        self.setCentralWidget(self.current_widget)  # Establecer como widget central

    def show_backup_restore_tab(self):
        if self.current_widget is not None:
            self.current_widget.deleteLater()  # Eliminar el widget actual

        self.current_widget = Respaldar()  # Crear nueva instancia
        self.setCentralWidget(self.current_widget)  # Establecer como widget central
        self.reload_databases()  # Cargar bases de datos al mostrar la pestaña

    def reload_databases(self):
        if self.current_widget is not None:
            self.current_widget.load_databases()  # Recargar las bases de datos en el widget actual
            if isinstance(self.current_widget, Respaldar):
                self.current_widget.load_backup_files()  # Cargar archivos de respaldo si estamos en la pestaña de Respaldar

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
