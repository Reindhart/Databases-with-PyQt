from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QAbstractItemView, QTableView, 
                             QProxyStyle, QPushButton, QHeaderView, QCheckBox, QComboBox, 
                             QHBoxLayout, QWidget, QMessageBox)
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, QSize
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon
import re, copy

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
        if not index.isValid():
            return None

        attribute = self._data[index.row()]
        name = attribute.get("name", "")
        col_type = attribute.get("col_type", "")
        key_type = attribute.get("key_type", "")
        extras = attribute.get("extras", "")
        
        length = ""
        if "Length:" in extras:
            length = extras.split("Length: ")[-1].split(",")[0] 

        column_map = {
            0: name,
            1: col_type,
            2: length,
            3: "",
            4: "",
            5: "",
            6: key_type,
            7: ""   # Columna de botón para borrar
        }

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return column_map.get(index.column(), "")
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole and index.column() in {0, 2}:  # Solo permitir edición en columnas específicas
            # Guarda el nuevo valor en el modelo de datos
            if index.column() == 0:
                self._data[index.row()]["name"] = value
            elif index.column() == 2:
                # Aquí puedes decidir cómo manejar la longitud
                self._data[index.row()]["extras"] = f"Length: {value}, ..."
            
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled

        if index.column() in {0, 1, 2, 6}:  # Solo estas columnas serán editables
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable  # No editables

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

        self.attributes_originals = copy.deepcopy(attributes)
        super().__init__()
        self.setWindowTitle("Modificar Atributos")
        self.resize(850, 300)

        layout_principal = QVBoxLayout(self)

        # Diccionario para almacenar los widgets de cada fila
        self.widgets = {}
    
        view = ReorderTableView(self)
        view.setModel(ReorderTableModel(attributes))
        
        # Configura el modelo con los atributos
        model = ReorderTableModel(attributes)
        view.setModel(model)

        for row, attribute in enumerate(attributes):
            self.widgets[row] = {}

            # Crear combobox de tipos
            combo = self.create_categorized_combobox()
            tipo = attribute.get("col_type", "")
            index = combo.findText(tipo.upper())  # Selecciona el tipo de dato actual
            if index >= 0:
                combo.setCurrentIndex(index)
            self.widgets[row]["tipo"] = combo
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
            self.widgets[row]["default"] = combo_default
            view.setIndexWidget(model.index(row, 3), combo_default)

            # Crear y asignar los widgets de checkbox   
            nulo_checkbox = QCheckBox()
            nulo_container = QWidget()
            nulo_layout = QHBoxLayout(nulo_container)
            nulo_layout.addWidget(nulo_checkbox)
            nulo_layout.setAlignment(nulo_checkbox, Qt.AlignmentFlag.AlignCenter)
            nulo_layout.setContentsMargins(0, 0, 0, 0)
            nulo_checkbox.setChecked("Nulo: sí" in extras)
            self.widgets[row]["nulo"] = nulo_checkbox
            view.setIndexWidget(model.index(row, 4), nulo_container)
            
            ai_checkbox = QCheckBox()
            autoincremento_container = QWidget()
            autoincremento_layout = QHBoxLayout(autoincremento_container)
            autoincremento_layout.addWidget(ai_checkbox)
            autoincremento_layout.setAlignment(ai_checkbox, Qt.AlignmentFlag.AlignCenter)
            autoincremento_layout.setContentsMargins(0, 0, 0, 0)
            ai_checkbox.setChecked("Auto Increment" in extras)
            self.widgets[row]["ai"] = ai_checkbox
            view.setIndexWidget(model.index(row, 5), autoincremento_container)

            # Crear combobox de llaves
            combo_key = QComboBox()
            combo_key.addItems(["", "PRIMARY", "UNIQUE", "INDEX", "FULLTEXT", "SPATIAL"])
            llave = attribute.get("key_type", "")
            index_key = combo_key.findText(llave.upper())  # Selecciona la llave actual
            if index_key >= 0:
                combo_key.setCurrentIndex(index_key)
            self.widgets[row]["key"] = combo_key
            view.setIndexWidget(model.index(row, 6), combo_key)  # Asigna el combo box a la celda
            
            # Borrar línea
            delete_button = QPushButton(self)
            delete_button.setIcon(QIcon('delete.png'))  
            delete_button.setIconSize(QSize(24, 24))
            delete_button.setFixedSize(QSize(24, 24))
            delete_button.clicked.connect(lambda checked, r=row: self.delete_table("algo", r))
            delete_button_container = QWidget()
            delete_button_layout = QHBoxLayout(delete_button_container)
            delete_button_layout.addWidget(delete_button)
            delete_button_layout.setAlignment(delete_button, Qt.AlignmentFlag.AlignCenter)
            delete_button_layout.setContentsMargins(0, 0, 0, 0)
            view.setIndexWidget(model.index(row, 7), delete_button_container)
        
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
        
        self.aplicar_cambios_btn.clicked.connect(lambda: self.aplicar_cambios(model, self.attributes_originals))
        self.agregar_fila_btn.clicked.connect(self.agregar_fila)
        self.cancel_btn.clicked.connect(self.cancel) 
        
        layout_principal.addLayout(buttons_layout)
        
    def agregar_fila(self):
        pass    
        
    def aplicar_cambios(self, model, attributes):
        cambios = []  # Lista para almacenar los cambios

        try:
            for row in range(model.rowCount()):
                # Obtener valores de los widgets usando el diccionario de widgets
                tipo_value = self.widgets[row]["tipo"].currentText()
                default_value = self.widgets[row]["default"].currentText()
                nulo_value = "sí" if self.widgets[row]["nulo"].isChecked() else "no"
                ai_value = "sí" if self.widgets[row]["ai"].isChecked() else "no"
                key_value = self.widgets[row]["key"].currentText()

                # Agregar los valores obtenidos a cambios o actualizarlos en el modelo de datos
                cambios.append({
                    "name": model.data(model.index(row, 0), Qt.ItemDataRole.DisplayRole),
                    "key_type": key_value,
                    "col_type": tipo_value,
                    "default": default_value,
                    "Nulo": nulo_value,
                    "ai": ai_value,
                    "Lenght": model.data(model.index(row, 2), Qt.ItemDataRole.DisplayRole)
                })

            # Procesar los cambios
            self.generar_sql(cambios, attributes)
        except Exception as e:
            QMessageBox.warning("Error", f"Error en aplicar_cambios: {e}")
    
    def generar_sql(self, cambios, attributes):
        sql_statements = []
        print(id(attributes))
        print(id(cambios))
        print(f"Estos son los atributos originales:\n{attributes}\nEstos son los atributos cambiados:\n{cambios}")
        
        """
        for row, column in cambios:
            if cambios[row, column] == attributes[row, column]:
                print("hay cambio")
                if len(cambios) > len(attributes):
                    sql_statements.append(f'ALTER TABLE nombre_tabla ADD COLUMN')                
        
        for accion, atributo in cambios:
            if accion == "ADD":
                sql_statements.append(f"ALTER TABLE nombre_tabla ADD COLUMN {atributo['name']} {atributo['col_type']} ...")
            elif accion == "MODIFY":
                sql_statements.append(f"ALTER TABLE nombre_tabla MODIFY COLUMN {atributo['name']} {atributo['col_type']} ...")
            elif accion == "DELETE":
                sql_statements.append(f"ALTER TABLE nombre_tabla DROP COLUMN {atributo['name']}")
        """
        return True

    
    def cancel(self):
        self.accept()
    
    def delete_table(self, table_name, row):
        print(f"{row}: entre")
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
            QComboBox QAbstractItemmodel::item:disabled {
                background: transparent; /* Sin color de fondo para las categorías */
            }
        """)

        return combo