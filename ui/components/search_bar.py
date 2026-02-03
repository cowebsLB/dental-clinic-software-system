"""Global search component."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal
from config.i18n import tr

class SearchBar(QWidget):
    """Global search bar widget."""
    
    search_triggered = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("common.search"))
        self.search_input.returnPressed.connect(self.on_search)
        
        search_button = QPushButton(tr("common.search"))
        search_button.clicked.connect(self.on_search)
        
        layout.addWidget(self.search_input)
        layout.addWidget(search_button)
    
    def on_search(self):
        """Handle search."""
        query = self.search_input.text().strip()
        if query:
            self.search_triggered.emit(query)
    
    def clear(self):
        """Clear search."""
        self.search_input.clear()

