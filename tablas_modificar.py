from PyQt6.QtWidgets import QDialog, QVBoxLayout, QAbstractItemView, QTableView, QProxyStyle
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex

class ReorderTableModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data

    def columnCount(self, parent=None) -> int:
        return 7

    def rowCount(self, parent=None) -> int:
        return len(self._data)

    def headerData(self, column: int, orientation, role: Qt.ItemDataRole):
        headers = ["Nombre", "Tipo", "Longitud", "Predeterminado", "Nulo", "A.I", "Llave"]
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

        layout = QVBoxLayout(self)
    
        view = ReorderTableView(self)
        
        #crashea aquí
        view.setModel(ReorderTableModel(attributes))
        layout.addWidget(view)
        
        self.setLayout(layout)