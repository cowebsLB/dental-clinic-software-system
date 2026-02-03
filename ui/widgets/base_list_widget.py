"""Base list widget for displaying and managing data."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QLineEdit)
from PySide6.QtCore import Qt, Signal
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   get_neumorphic_table_style, apply_neumorphic_effect)


class BaseListWidget(QWidget):
    """Base widget for displaying lists of data with CRUD operations."""
    
    item_selected = Signal(dict)  # Emits selected item data
    add_requested = Signal()
    edit_requested = Signal(dict)
    delete_requested = Signal(str)
    
    def __init__(self, title: str, manager, columns: list, parent=None):
        super().__init__(parent)
        self.title = title
        self.manager = manager
        self.columns = columns  # List of (key, display_name) tuples
        self.data = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the UI."""
        self.setStyleSheet("background: transparent;")
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.title)
        self._update_title_style()
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Search - inset neumorphic effect
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("common.search"))
        self.search_input.setMaximumWidth(300)
        self._update_search_style()
        apply_neumorphic_effect(self.search_input, inset=True, intensity=0.8)
        self.search_input.textChanged.connect(self.on_search)
        header_layout.addWidget(self.search_input)
        
        # Add button - outset neumorphic effect
        self.add_button = QPushButton(tr("common.add"))
        self._update_button_style(self.add_button)
        apply_neumorphic_effect(self.add_button, inset=False, intensity=1.0)
        self.add_button.clicked.connect(self.on_add)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        
        # Table - neumorphic styling
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([col[1] for col in self.columns])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.table.setAlternatingRowColors(True)
        self._update_table_style()
        apply_neumorphic_effect(self.table, inset=False, intensity=0.9)
        layout.addWidget(self.table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.edit_button = QPushButton(tr("common.edit"))
        self._update_button_style(self.edit_button)
        apply_neumorphic_effect(self.edit_button, inset=False, intensity=1.0)
        self.edit_button.clicked.connect(self.on_edit)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton(tr("common.delete"))
        self._update_button_style(self.delete_button)
        apply_neumorphic_effect(self.delete_button, inset=False, intensity=1.0)
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
    
    def _update_title_style(self):
        """Update title style with theme."""
        palette = theme_manager.get_palette()
        self.title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 300;
            color: {palette.text_primary};
            background: transparent;
        """)
    
    def _update_search_style(self):
        """Update search input style."""
        self.search_input.setStyleSheet(get_neumorphic_input_style())
    
    def _update_button_style(self, button: QPushButton):
        """Update button style."""
        button.setStyleSheet(get_neumorphic_button_style())
    
    def _update_table_style(self):
        """Update table style."""
        self.table.setStyleSheet(get_neumorphic_table_style())
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_title_style()
        self._update_search_style()
        self._update_button_style(self.add_button)
        self._update_button_style(self.edit_button)
        self._update_button_style(self.delete_button)
        self._update_table_style()
        
        # Connect selection
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
    
    def load_data(self):
        """Load data from manager."""
        try:
            if hasattr(self.manager, 'list_all'):
                # Try calling with default parameters
                try:
                    self.data = self.manager.list_all()
                except TypeError:
                    # Some managers have required parameters
                    self.data = self.manager.list_all(limit=100)
            elif hasattr(self.manager, 'get_all'):
                self.data = self.manager.get_all()
            elif hasattr(self.manager, 'query'):
                # Use query method if available
                self.data = self.manager.query({})
            else:
                # Fallback: try to query local cache directly
                from database.local_cache import local_cache
                table_name = getattr(self.manager, 'table_name', '')
                if table_name:
                    self.data = local_cache.query(table_name, limit=100)
                else:
                    self.data = []
            
            self.populate_table()
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error loading data: {e}")
            self.data = []
            self.populate_table()
    
    def populate_table(self):
        """Populate table with data."""
        self.table.setRowCount(len(self.data))
        
        for row, item in enumerate(self.data):
            for col, (key, _) in enumerate(self.columns):
                value = item.get(key, '')
                # Format value for display
                if value is None:
                    display_value = ''
                elif isinstance(value, bool):
                    display_value = 'Yes' if value else 'No'
                else:
                    display_value = str(value)
                
                table_item = QTableWidgetItem(display_value)
                table_item.setData(Qt.ItemDataRole.UserRole, item)  # Store full item data
                self.table.setItem(row, col, table_item)
        
        # Resize columns
        self.table.resizeColumnsToContents()
    
    def on_search(self, text: str):
        """Handle search."""
        if not text.strip():
            self.populate_table()
            return
        
        try:
            if hasattr(self.manager, 'search'):
                self.data = self.manager.search(text)
            else:
                # Simple client-side filtering
                query_lower = text.lower()
                self.data = [
                    item for item in self.data
                    if any(query_lower in str(item.get(key, '')).lower() 
                          for key, _ in self.columns)
                ]
            self.populate_table()
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error searching: {e}")
    
    def on_add(self):
        """Handle add button."""
        self.add_requested.emit()
    
    def on_edit(self):
        """Handle edit button."""
        selected_items = self.table.selectedItems()
        if selected_items:
            item_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if item_data:
                self.edit_requested.emit(item_data)
    
    def on_delete(self):
        """Handle delete button."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        item_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not item_data:
            return
        
        item_id = item_data.get('id')
        if not item_id:
            return
        
        # Confirm deletion with styled message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(tr("common.confirm"))
        msg_box.setText("Are you sure you want to delete this item?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4C1D95, stop:1 #1E1B4B);
                color: rgba(255, 255, 255, 0.9);
            }
            QMessageBox QLabel {
                color: rgba(255, 255, 255, 0.9);
            }
            QMessageBox QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if hasattr(self.manager, 'delete'):
                    success, error = self.manager.delete(item_id)
                    if success:
                        QMessageBox.information(self, tr("common.success"), "Item deleted successfully")
                        self.load_data()
                    else:
                        QMessageBox.warning(self, tr("common.error"), error or "Failed to delete item")
            except Exception as e:
                QMessageBox.warning(self, tr("common.error"), f"Error deleting: {e}")
    
    def on_item_double_clicked(self, item: QTableWidgetItem):
        """Handle double click on item."""
        item_data = item.data(Qt.ItemDataRole.UserRole)
        if item_data:
            self.edit_requested.emit(item_data)
    
    def on_selection_changed(self):
        """Handle selection change."""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def refresh(self):
        """Refresh the data."""
        self.load_data()

