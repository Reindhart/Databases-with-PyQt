from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QMimeData

class ModificarAtributosDialog(QDialog):
    def __init__(self, attributes):
        super().__init__()

        self.setWindowTitle("Modificar Atributos")
        self.setMinimumSize(400, 300)

        # Crear el layout principal
        layout = QVBoxLayout(self)

        # Crear el QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(attributes))  # Número de filas
        self.table_widget.setColumnCount(3)  # Supongamos que hay 3 columnas (Nombre, Tipo, Llave)

        # Establecer encabezados de la tabla
        self.table_widget.setHorizontalHeaderLabels(["Nombre", "Tipo", "Longitud", "Predeterminado", "Nulo", "A.I", "Llave"])

        # Cargar los atributos en la tabla
        for row, attr in enumerate(attributes):
            self.table_widget.setItem(row, 0, QTableWidgetItem(attr['name']))
            self.table_widget.setItem(row, 1, QTableWidgetItem(attr['col_type']))
            self.table_widget.setItem(row, 2, QTableWidgetItem(attr['key_type']))
            self.table_widget.setItem(row, 2, QTableWidgetItem(attr['extras']))
            self.table_widget.setItem(row, 2, QTableWidgetItem(attr['Lenght']))

        # Habilitar drag and drop
        self.table_widget.setDragEnabled(True)
        self.table_widget.setDropIndicatorShown(True)
        self.table_widget.setAcceptDrops(True)

        layout.addWidget(self.table_widget)

        # Botón para guardar cambios
        save_button = QPushButton("Guardar Cambios")
        layout.addWidget(save_button)

        # Conectar el botón a su función
        save_button.clicked.connect(self.save_changes)

        self.setLayout(layout)

    def save_changes(self):
        # Aquí puedes implementar la lógica para guardar los cambios en los atributos
        QMessageBox.information(self, "Información", "Los cambios han sido guardados.")
        self.accept()  # Cerrar el diálogo

    def dropEvent(self, event):
        """Gestiona el evento de soltar una fila."""
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            data = event.mimeData()
            row = data.data('application/x-qabstractitemmodeldatalist')
            self.move_row(row, event.pos())

    def move_row(self, row, pos):
        """Mueve la fila a la posición dada."""
        target_row = self.table_widget.rowAt(pos.y())
        if target_row == -1:
            return  # Si no se ha soltado en una fila válida, salir.

        # Obtener los datos de la fila que se mueve
        row_data = [self.table_widget.takeItem(row, col) for col in range(self.table_widget.columnCount())]

        # Insertar la fila en la nueva posición
        if row < target_row:
            # Si movemos hacia arriba
            for i in range(row, target_row):
                for col in range(self.table_widget.columnCount()):
                    self.table_widget.setItem(i, col, self.table_widget.takeItem(i + 1, col))
            self.table_widget.setItem(target_row, 0, row_data[0])
            self.table_widget.setItem(target_row, 1, row_data[1])
            self.table_widget.setItem(target_row, 2, row_data[2])
        elif row > target_row:
            # Si movemos hacia abajo
            for i in range(row, target_row, -1):
                for col in range(self.table_widget.columnCount()):
                    self.table_widget.setItem(i, col, self.table_widget.takeItem(i - 1, col))
            self.table_widget.setItem(target_row, 0, row_data[0])
            self.table_widget.setItem(target_row, 1, row_data[1])
            self.table_widget.setItem(target_row, 2, row_data[2])