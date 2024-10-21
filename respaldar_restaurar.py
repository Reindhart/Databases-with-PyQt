from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QScrollArea, QFrame, QPushButton,
    QMessageBox, QHeaderView, QComboBox, QListWidget
)
from connection import get_databases_with_tables
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
import os, subprocess
from datetime import datetime

fecha = datetime.today().strftime('%d_%m_%Y-%H.%M')
mysqldumpPath = "C:\\_App\\xampp\\mysql\\bin\\mysqldump.exe"
mysqlPath = "C:\\_App\\xampp\\mysql\\bin\\mysql.exe"
user="root"
password=""

import os
import subprocess

def backup_database(database_name, backup_path):
    try:
        # Crear la carpeta de respaldo si no existe
        os.makedirs(backup_path, exist_ok=True)

        # Crear la ruta completa para el archivo de respaldo
        backup_file = os.path.join(backup_path, f"{database_name}-{fecha}.sql")

        # Comando mysqldump con usuario, contraseña y archivo de salida
        backup_command = [
            mysqldumpPath,                   # Ruta al ejecutable mysqldump
            "--user=" + user,          # Usuario
            "--password=" + password,  # Contraseña
            "--databases",             # Indicar que se van a respaldar bases de datos
            database_name,             # Nombre de la base de datos
            "--result-file=" + backup_file  # Archivo de salida
        ]

        # Ejecutar el comando mysqldump
        process = subprocess.run(backup_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Verificar si hubo algún error
        if process.returncode != 0:
            # Mensaje amigable para el usuario
            error_message = f"No se pudo respaldar la base de datos '{database_name}'. Verifica si está disponible o si tiene tablas válidas."
            print(f"Error técnico: {process.stderr}")  # Mostrar error técnico en consola
            raise Exception(error_message)  # Lanzar el mensaje de error amigable

        print(f"Respaldo de '{database_name}' creado exitosamente en {backup_file}")

    except Exception as err:
        print(f"Error: {err}")
        raise  # Propaga el error para que sea manejado en el método principal



class Respaldar(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Respaldar Bases de Datos")

        # Layout principal (horizontal) que contendrá el ComboBox y la tabla
        main_layout = QHBoxLayout(self)

        # Crear layout vertical para la tabla y el botón
        left_layout = QVBoxLayout()

        # Crear scroll y tabla
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QFrame(self.scroll_area)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)

        self.table_widget = QTableWidget(self.content_widget)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Bases de Datos", ""])  # Nombre de la columna vacío

        self.load_databases()

        self.backup_button = QPushButton("Respaldar Bases de Datos", self)
        self.backup_button.clicked.connect(self.backup_selected_databases)

        self.table_widget.itemClicked.connect(self.toggle_checkbox)  # Conectar clic en las celdas

        # Agregar la tabla y el botón al layout vertical (izquierda)
        left_layout.addWidget(self.scroll_area)
        left_layout.addWidget(self.backup_button)

        # Crear layout vertical para ComboBox y lista
        right_layout = QVBoxLayout()

        # Crear ComboBox
        self.database_combobox = QComboBox(self)
        self.database_combobox.addItem("Escoja una base de datos...")  # Placeholder
        self.load_combobox_databases()  # Llenar el ComboBox con las bases de datos

        # Crear una línea vertical para la separación
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.VLine)  # Línea vertical
        separator.setFrameShadow(QFrame.Shadow.Sunken)  # Sombra de la línea

        # Crear QListWidget para mostrar los archivos de respaldo
        self.backup_list_widget = QListWidget(self)

        # Agregar el ComboBox y la lista al layout vertical (derecha)
        right_layout.addWidget(self.database_combobox)
        right_layout.addWidget(self.backup_list_widget)

        # Crear botón "Restaurar"
        self.restore_button = QPushButton("Restaurar", self)
        self.restore_button.clicked.connect(self.restore_database)  # Conectar señal del botón a la función de restaurar
        right_layout.addWidget(self.restore_button)

        # Añadir layouts al main_layout con igual tamaño
        main_layout.addLayout(left_layout)
        main_layout.addWidget(separator)
        main_layout.addLayout(right_layout)  # Agregar el layout derecho que contiene ComboBox y lista

        # Configurar el tamaño del layout principal para que ocupe la mitad
        main_layout.setStretchFactor(left_layout, 1)  # La sección de la izquierda ocupará 1 parte
        main_layout.setStretchFactor(right_layout, 1)  # La sección de la derecha (ComboBox y lista) ocupará 1 parte

        self.setLayout(main_layout)

        self.load_backup_files()  # Cargar archivos de respaldo al iniciar

    def load_databases(self):
        databases = get_databases_with_tables()
        self.table_widget.setRowCount(len(databases))

        for row, database_name in enumerate(databases):
            name_item = QTableWidgetItem(database_name)
            self.table_widget.setItem(row, 0, name_item)

            if row % 2 == 0:
                name_item.setBackground(QColor(220, 220, 220))
            else:
                name_item.setBackground(QColor(255, 255, 255))

            name_item.setForeground(QBrush(QColor(0, 0, 0)))

            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, 1, checkbox_item)

        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table_widget.setColumnWidth(1, 30)

        self.content_layout.addWidget(self.table_widget)

    def load_combobox_databases(self):
        databases = get_databases_with_tables()
        for database in databases:
            self.database_combobox.addItem(database)

    def load_backup_files(self):
        self.backup_list_widget.clear()  # Limpiar la lista existente
        backup_path = "Respaldos"
        try:
            # Listar los archivos de la carpeta "Respaldos"
            for filename in os.listdir(backup_path):
                if filename.endswith(".sql"):  # Asegurarse de que solo se agreguen archivos .sql
                    self.backup_list_widget.addItem(filename)
        except FileNotFoundError:
            print("La carpeta de respaldos no existe.")
        
    def backup_selected_databases(self):
        backup_path = "Respaldos"
        databases_to_backup = []

        for row in range(self.table_widget.rowCount()):
            checkbox_item = self.table_widget.item(row, 1)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                database_name = self.table_widget.item(row, 0).text()
                databases_to_backup.append(database_name)

        if not databases_to_backup:
            QMessageBox.warning(self, "Advertencia", "No se ha seleccionado ninguna base de datos para respaldar.")
            return

        any_errors = False
        for db_name in databases_to_backup:
            try:
                backup_database(db_name, backup_path)
            except Exception as err:
                QMessageBox.critical(self, "Error", str(err))  # Muestra el mensaje de error amigable
                any_errors = True

        if any_errors:
            QMessageBox.critical(self, "Error", "Ocurrieron errores durante el respaldo. Revisa los detalles.")
        else:
            QMessageBox.information(self, "Éxito", "Respaldo completado exitosamente.")

        # Restablecer todos los checkboxes a 'Unchecked' después del respaldo
        for row in range(self.table_widget.rowCount()):
            checkbox_item = self.table_widget.item(row, 1)
            if checkbox_item:
                checkbox_item.setCheckState(Qt.CheckState.Unchecked)

        self.load_backup_files()  # Recargar archivos de respaldo


    def restore_database(self):
        # Obtener el nombre de la base de datos seleccionada en el ComboBox
        selected_database = self.database_combobox.currentText()
        selected_file = self.backup_list_widget.currentItem()

        if selected_database == "Escoja una base de datos...":
            QMessageBox.warning(self, "Advertencia", "Por favor, escoja una de las bases de datos disponibles.")
            return

        if selected_file is None:
            QMessageBox.warning(self, "Advertencia", "Seleccione un archivo de respaldo para restaurar.")
            return

        # Obtener la ruta completa del archivo de respaldo
        backup_file_path = os.path.join("Respaldos", selected_file.text())
        print(f"Restaurando base de datos '{selected_database}' desde '{backup_file_path}'")

        try:
            # Abrir el archivo de respaldo
            with open(backup_file_path, 'r') as backup_file:
                # Comando para la restauración
                restore_command = [
                    mysqlPath,  # Ruta a mysql.exe o mysqlimport.exe
                    f"--user={user}",
                    f"--password={password}",
                    selected_database
                ]

                # Ejecutar el comando con el contenido del archivo como entrada
                process = subprocess.run(
                    restore_command,
                    stdin=backup_file,  # Pasar el archivo como entrada estándar
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            # Verificar si hubo algún error
            if process.returncode != 0:
                QMessageBox.critical(self, "Error", f"No se pudo restaurar la base de datos '{selected_database}': {process.stderr}")
            else:
                QMessageBox.information(self, "Éxito", f"Base de datos '{selected_database}' restaurada exitosamente.")
            
                # Restablecer el ComboBox a la opción predeterminada
                self.database_combobox.setCurrentIndex(0)

                # Deseleccionar el elemento de la lista
                self.backup_list_widget.clearSelection()

        except Exception as err:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {err}")


    def toggle_checkbox(self, item):
        if item.column() == 0:
            row = item.row()
            checkbox_item = self.table_widget.item(row, 1)
            if checkbox_item.checkState() == Qt.CheckState.Checked:
                checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            else:
                checkbox_item.setCheckState(Qt.CheckState.Checked)
