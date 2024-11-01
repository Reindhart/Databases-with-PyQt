from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QAbstractItemView, QTableView, 
                             QProxyStyle, QPushButton, QHeaderView, QCheckBox, QComboBox, 
                             QHBoxLayout, QWidget)
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, QSize
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon
import re

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

        attribute = self._data[index.row()]
        # Extrae información de las columnas principales
        name = attribute.get("name", "")
        col_type = attribute.get("col_type", "")
        key_type = attribute.get("key_type", "")
        extras = attribute.get("extras", "")
        
        # Valores predeterminados para columnas adicionales
        default_value = ""
        is_nullable = False
        auto_increment = False
        length = ""
        
        # Dividir y verificar los componentes de extras
        if "Nulo: sí" in extras:
            is_nullable = True
        if "Length:" in extras:
            length = extras.split("Length: ")[-1].split(",")[0]  # Extraer longitud
        if "Default:" in extras:
            default_value = extras.split("Default: ")[-1].split(",")[0]  # Extraer valor por defecto
        if "Auto Increment" in extras:
            auto_increment = True

        # Mapea las columnas visibles en tu tabla con la información extraída
        column_map = {
            0: name,
            1: col_type,
            2: length,          # Longitud
            3: default_value,   # Valor predeterminado
            4: is_nullable,     # Nulo
            5: auto_increment,  # Auto incremento
            6: key_type         # Tipo de llave
        }

        # Retorna el valor correspondiente a la columna actual o un string vacío
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

    
        view = ReorderTableView(self)
        view.setModel(ReorderTableModel(attributes))
        
        # Configura el modelo con los atributos
        model = ReorderTableModel(attributes)
        view.setModel(model)

        for row, attribute in enumerate(attributes):

            # Crear combobox de llaves
            combo = self.create_categorized_combobox()
            tipo = attribute.get("col_type", "")
            index = combo.findText(tipo.upper())  # Selecciona el tipo de dato actual
            if index >= 0:
                combo.setCurrentIndex(index)
            view.setIndexWidget(model.index(row, 1), combo)  # Asigna el combo box a la celda
            
            # Crear combobox de predeterminados
            combo_default = QComboBox()
            combo_default.addItems(["Ninguno", "NULL", "CURRENT_TIMESTAMP"])
            default = ""
            extras = attribute.get("extras", "")
            match = re.search(r"Default:\s*([^\s,]+)", extras)  # Busca el valor después de "Default:"
            if match:
                default = match.group(1).rstrip("()")  # Obtiene el valor predeterminado
            index_default = combo_default.findText(default.upper())
            if index_default >= 0:
                combo_default.setCurrentIndex(index_default)
            view.setIndexWidget(model.index(row, 3), combo_default)

            # Crear y asignar los widgets de checkbox
            nulo_checkbox = QCheckBox()
            nulo_checkbox.setChecked(attribute.get("is_nullable", False))
            view.setIndexWidget(model.index(row, 4), nulo_checkbox)
            
            ai_checkbox = QCheckBox()
            ai_checkbox.setChecked(attribute.get("auto_increment", False))
            view.setIndexWidget(model.index(row, 5), ai_checkbox)

            # Crear combobox de llaves
            combo_key = QComboBox()
            combo_key.addItems(["", "PRIMARY", "UNIQUE", "INDEX", "FULLTEXT", "SPATIAL"])
            llave = attribute.get("key_type", "")
            index_key = combo_key.findText(llave.upper())  # Selecciona la llave actual
            if index_key >= 0:
                combo_key.setCurrentIndex(index_key)
            view.setIndexWidget(model.index(row, 6), combo_key)  # Asigna el combo box a la celda

        layout_principal.addWidget(view)
        
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
        
        self.aplicar_cambios_btn.clicked.connect(self.aplicar_cambios)
        self.agregar_fila_btn.clicked.connect(self.agregar_fila)
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

    def create_categorized_combobox(self):
        combo = QComboBox()

        # Crear un modelo para manejar las categorías y subcategorías
        model = QStandardItemModel()

        for data_type in ["INT", "VARCHAR", "TEXT", "DATE"]:
            item = QStandardItem(data_type)
            model.appendRow(item)
            
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