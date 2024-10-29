from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QAbstractItemView, QTableView, 
                             QProxyStyle, QPushButton, QHeaderView, QCheckBox, QComboBox, 
                             QHBoxLayout, QWidget)
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, QSize
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon

class ReorderTableModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data

    def columnCount(self, parent=None) -> int:
        return 8

    def rowCount(self, parent=None) -> int:
        return len(self._data)

    def headerData(self, column: int, orientation, role: Qt.ItemDataRole):
        headers = ["Nombre", "Tipo", "Longitud", "Predeterminado", "Nulo", "A.I", "Llave", ""]
        return headers[column] if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal else None

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if not index.isValid() or role not in {Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole}:
            return None

        # Asegúrate de que el diccionario tenga todas las claves esperadas.
        attribute = self._data[index.row()]
        column_map = {
            0: attribute.get("name", ""),
            1: attribute.get("col_type", ""),
            2: attribute.get("extras", ""),  # Asumiendo que aquí está la longitud
            3: attribute.get("default_value", ""),  # Valor predeterminado, si existe
            4: attribute.get("is_nullable", ""),  # Indicación de si permite nulos
            5: attribute.get("auto_increment", ""),  # Auto incremento si aplica
            6: attribute.get("key_type", "")  # Clave primaria, foránea o regular
        }
        
        return column_map.get(index.column(), "")

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled
        return (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction

    def relocateRow(self, row_source, row_target) -> None:
        if row_source != row_target:
            self.beginMoveRows(QModelIndex(), row_source, row_source, QModelIndex(), row_target)
            self._data.insert(row_target, self._data.pop(row_source))
            self.endMoveRows()


class ReorderTableView(QTableView):
    """QTableView with drag & drop row reordering support."""

    class DropmarkerStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            if element == self.PrimitiveElement.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
                option.rect.setLeft(0)
                if widget:
                    option.rect.setRight(widget.width())
            super().drawPrimitive(element, option, painter, widget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().hide()
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setStyle(self.DropmarkerStyle())

    def dropEvent(self, event):
        if event.source() is not self:
            super().dropEvent(event)
            return

        selection = self.selectedIndexes()
        from_index = selection[0].row() if selection else -1
        to_index = self.indexAt(event.position().toPoint()).row()
        if 0 <= from_index < self.model().rowCount() and 0 <= to_index < self.model().rowCount() and from_index != to_index:
            self.model().relocateRow(from_index, to_index)
            event.accept()
        super().dropEvent(event)


class ModificarAtributos(QDialog):
    """Ventana de modificación de atributos de la tabla con reordenamiento de filas."""
    def __init__(self, attributes):
        super().__init__()
        self.setWindowTitle("Modificar Atributos")
        self.resize(850, 300)

        layout_principal = QVBoxLayout(self)
        
        self.aplicar_cambios_btn = QPushButton("Aplicar cambios")
        self.aplicar_cambios_btn.clicked.connect(self.aplicar_cambios)
    
        view = ReorderTableView(self)
        
        view.setModel(ReorderTableModel(attributes))
        
        view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        view.setColumnWidth(4, 10)
        view.setColumnWidth(5, 10)
        view.setColumnWidth(7, 10)
        
        layout_principal.addWidget(view)
        
        self.agregar_fila_btn = QPushButton("Agregar atributo")
        self.aplicar_cambios_btn = QPushButton("Aplicar cambios")
        self.cancel_btn = QPushButton("Cancelar")

        buttons_layout = QHBoxLayout()

        # Agregar los botones al layout
        buttons_layout.addWidget(self.agregar_fila_btn)
        buttons_layout.addWidget(self.aplicar_cambios_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.agregar_fila_btn.clicked.connect(self.agregar_fila)
        self.aplicar_cambios_btn.clicked.connect(self.aplicar_cambios)
        self.cancel_btn.clicked.connect(self.cancel) 
        
        layout_principal.addLayout(buttons_layout)
        
    def agregar_fila(self):
        pass    
        
    def aplicar_cambios(self):
        pass
    
    def cancel(self):
        self.accept()
    
    def delete_table(self, table_name):
        pass
    
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
        category_numeric = QStandardItem("--Numeric--")
        category_numeric.setFlags(Qt.ItemFlag.NoItemFlags & ~Qt.ItemFlag.ItemIsEnabled)  # No seleccionable
        model.appendRow(category_numeric)

        for data_type in ["TINYINT", "SMALLINT", "MEDIUMINT", "INT", "BIGINT", 
                          "DECIMAL", "FLOAT", "DOUBLE", "REAL", "BIT", "BOOLEAN", "SERIAL"]:
            item = QStandardItem(data_type)
            model.appendRow(item)

        # Categoría de cadenas
        category_string = QStandardItem("--String--")
        category_string.setFlags(Qt.ItemFlag.NoItemFlags)  # No seleccionable
        model.appendRow(category_string)

        for data_type in ["CHAR", "VARCHAR", "TINYTEXT", "TEXT", "MEDIUMTEXT", "LONGTEXT", 
                          "BINARY" , "VARBINARY", "TINYBLOB", "BLOB", "MEDIUMBLOB", "LONGBLOB",
                          "ENUM", "SET"]:
            item = QStandardItem(data_type)
            model.appendRow(item)

        # Categoría de fecha y hora
        category_date_time = QStandardItem("--Date--")
        category_date_time.setFlags(Qt.ItemFlag.NoItemFlags)  # No seleccionable
        model.appendRow(category_date_time)

        for data_type in ["DATE", "DATETIME", "TIMESTAMP", "TIME", "YEAR"]:
            item = QStandardItem(data_type)
            model.appendRow(item)

        # Categoría de espaciales
        category_spatial = QStandardItem("--Spatial--")
        category_spatial.setFlags(Qt.ItemFlag.NoItemFlags)  # No seleccionable
        model.appendRow(category_spatial)

        for data_type in ["GEOMETRY", "POINT", "LINESTRING", "POLYGON", "MULTIPOINT", "MULTILINESTRING",
                          "MULTIPOLYGON", "GEOMETRYCOLLECTION"]:
            item = QStandardItem(data_type)
            model.appendRow(item)

        # Categoría de espaciales
        category_json = QStandardItem("--JSON--")
        category_json.setFlags(Qt.ItemFlag.NoItemFlags)  # No seleccionable
        model.appendRow(category_json)
        model.appendRow(QStandardItem("JSON"))

        combo.setModel(model)

        # Estilo para evitar el resaltado de fondo al pasar el mouse
        combo.setStyleSheet("""
            QComboBox QAbstractItemView::item:disabled {
                background: transparent; /* Sin color de fondo para las categorías */
            }
        """)

        return combo