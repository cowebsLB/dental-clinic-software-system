"""Network/sync status indicator widget."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette
from utils.network_monitor import network_monitor
from database.sync_manager import sync_manager
from typing import Optional
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import get_neumorphic_button_style, apply_neumorphic_effect

class SyncStatusWidget(QWidget):
    """Widget showing network and sync status."""
    
    sync_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_status()
        
        # Connect to network monitor
        network_monitor.status_changed.connect(self.on_network_status_changed)
    
    def setup_ui(self):
        """Setup UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Status indicator
        self.status_label = QLabel()
        self.status_label.setFixedWidth(12)
        self.status_label.setFixedHeight(12)
        self.status_label.setStyleSheet("border-radius: 6px;")
        
        # Status text
        self.status_text = QLabel("Checking...")
        self._update_text_style()
        
        # Sync button
        self.sync_button = QPushButton("Sync")
        self.sync_button.setFixedHeight(24)
        self.sync_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(self.sync_button, inset=False, intensity=0.8)
        self.sync_button.clicked.connect(self.on_sync_clicked)
        self.sync_button.setVisible(False)
        
        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_text)
        layout.addWidget(self.sync_button)
        layout.addStretch()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_text_style(self):
        """Update text style with theme."""
        palette = theme_manager.get_palette()
        self.status_text.setStyleSheet(f"font-size: 11px; color: {palette.text_secondary}; background: transparent;")
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_text_style()
        # Update button style
        self.sync_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(self.sync_button, inset=False, intensity=0.8)
    
    def update_status(self):
        """Update status display."""
        is_online = network_monitor.is_online()
        sync_status = sync_manager.get_sync_status()
        
        if is_online:
            if sync_status['is_syncing']:
                self.set_status("Syncing...", QColor(255, 193, 7))  # Yellow
                self.sync_button.setVisible(False)
            elif sync_status['pending_count'] > 0:
                self.set_status(f"{sync_status['pending_count']} pending", QColor(255, 193, 7))
                self.sync_button.setVisible(True)
            else:
                self.set_status("Synced", QColor(76, 175, 80))  # Green
                self.sync_button.setVisible(False)
        else:
            self.set_status("Offline", QColor(244, 67, 54))  # Red
            self.sync_button.setVisible(sync_status['pending_count'] > 0)
    
    def set_status(self, text: str, color: QColor):
        """Set status text and color."""
        self.status_text.setText(text)
        self.status_label.setStyleSheet(
            f"background-color: {color.name()}; border-radius: 6px;"
        )
    
    def on_network_status_changed(self, is_online: bool):
        """Handle network status change."""
        self.update_status()
    
    def on_sync_clicked(self):
        """Handle sync button click."""
        self.sync_requested.emit()

