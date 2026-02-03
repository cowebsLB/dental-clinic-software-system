"""Conflict resolution dialog."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QSplitter, QWidget)
from PySide6.QtCore import Qt
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import get_neumorphic_button_style, get_neumorphic_input_style, apply_neumorphic_effect
from typing import Optional

class ConflictDialog(QDialog):
    """Dialog for resolving conflicts."""
    
    def __init__(self, conflict_data: dict, parent=None):
        super().__init__(parent)
        self.conflict_data = conflict_data
        self.resolution = None
        self.setWindowTitle("Resolve Conflict")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {palette.background};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Data Conflict Detected")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {palette.text_primary};
            background: transparent;
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("The local and remote versions of this record differ. Choose how to resolve:")
        desc.setStyleSheet(f"""
            color: {palette.text_secondary};
            background: transparent;
        """)
        layout.addWidget(desc)
        
        # Split view showing local vs remote
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Local data
        local_label = QLabel("Local Data:")
        local_label.setStyleSheet(f"color: {palette.text_primary}; font-weight: 600; background: transparent;")
        local_text = QTextEdit()
        local_text.setReadOnly(True)
        local_text.setPlainText(self._format_data(self.conflict_data.get('local_data', {})))
        local_text.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(local_text, inset=True, intensity=0.8)
        
        local_layout = QVBoxLayout()
        local_layout.addWidget(local_label)
        local_layout.addWidget(local_text)
        local_widget = QWidget()
        local_widget.setLayout(local_layout)
        splitter.addWidget(local_widget)
        
        # Remote data
        remote_label = QLabel("Remote Data:")
        remote_label.setStyleSheet(f"color: {palette.text_primary}; font-weight: 600; background: transparent;")
        remote_text = QTextEdit()
        remote_text.setReadOnly(True)
        remote_text.setPlainText(self._format_data(self.conflict_data.get('remote_data', {})))
        remote_text.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(remote_text, inset=True, intensity=0.8)
        
        remote_layout = QVBoxLayout()
        remote_layout.addWidget(remote_label)
        remote_layout.addWidget(remote_text)
        remote_widget = QWidget()
        remote_widget.setLayout(remote_layout)
        splitter.addWidget(remote_widget)
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        accept_local = QPushButton("Accept Local")
        accept_local.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(accept_local, inset=False, intensity=1.0)
        accept_local.clicked.connect(lambda: self.accept_resolution('local'))
        button_layout.addWidget(accept_local)
        
        accept_remote = QPushButton("Accept Remote")
        accept_remote.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(accept_remote, inset=False, intensity=1.0)
        accept_remote.clicked.connect(lambda: self.accept_resolution('remote'))
        button_layout.addWidget(accept_remote)
        
        merge_button = QPushButton("Merge Manually")
        merge_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(merge_button, inset=False, intensity=1.0)
        merge_button.clicked.connect(lambda: self.accept_resolution('merge'))
        button_layout.addWidget(merge_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(cancel_button, inset=False, intensity=1.0)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _format_data(self, data: dict) -> str:
        """Format data for display."""
        import json
        return json.dumps(data, indent=2)
    
    def accept_resolution(self, resolution: str):
        """Accept a resolution."""
        self.resolution = resolution
        self.accept()
    
    def get_resolution(self) -> Optional[str]:
        """Get selected resolution."""
        return self.resolution

