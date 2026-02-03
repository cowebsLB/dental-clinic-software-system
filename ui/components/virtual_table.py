"""Virtualized table component for performance."""

from PySide6.QtWidgets import QTableView, QAbstractItemView
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class VirtualTableModel(QAbstractTableModel):
    """Model for virtualized table."""
    
    def __init__(self, data: List[Dict], columns: List[Dict], parent=None):
        super().__init__(parent)
        self._data = data
        self._columns = columns
        self._column_names = [col['key'] for col in columns]
        self._column_headers = [col.get('header', col['key']) for col in columns]
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of rows."""
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return number of columns."""
        return len(self._columns)
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Return data for index."""
        if not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._data[index.row()]
            col_key = self._column_names[index.column()]
            value = row.get(col_key, '')
            
            # Format value based on column type
            col_type = self._columns[index.column()].get('type', 'text')
            if col_type == 'number' and value is not None:
                return f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
            elif col_type == 'date' and value:
                return str(value)[:10]  # Just the date part
            
            return str(value) if value is not None else ''
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._column_headers[section]
        return None
    
    def update_data(self, data: List[Dict]):
        """Update table data."""
        self.beginResetModel()
        self._data = data
        self.endResetModel()
    
    def get_row_data(self, row: int) -> Optional[Dict]:
        """Get data for a specific row."""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None


class VirtualTableView(QTableView):
    """Virtualized table view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(True)
    
    def set_data(self, data: List[Dict], columns: List[Dict]):
        """Set table data and columns."""
        model = VirtualTableModel(data, columns, self)
        self.setModel(model)
        
        # Resize columns
        self.resizeColumnsToContents()
    
    def get_selected_row_data(self) -> Optional[Dict]:
        """Get data for selected row."""
        selection = self.selectedIndexes()
        if selection:
            model = self.model()
            if model:
                row = selection[0].row()
                return model.get_row_data(row)
        return None
    
    def clear_selection(self):
        """Clear selection."""
        self.selectionModel().clearSelection()

