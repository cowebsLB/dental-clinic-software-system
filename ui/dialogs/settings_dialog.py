"""Settings and preferences dialog with neumorphic styling."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QRadioButton, QButtonGroup, QCheckBox)
from PySide6.QtCore import Qt, Signal
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_button_style, get_neumorphic_input_style,
                                  apply_neumorphic_effect)
from ui.widgets.form_controls import NeumorphicRadioButton, NeumorphicCheckBox


class SettingsDialog(QDialog):
    """Settings dialog for theme and preferences."""
    
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.setup_ui()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
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
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {palette.text_primary};
            background: transparent;
        """)
        layout.addWidget(title)
        
        # Theme section
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {palette.text_primary};
            background: transparent;
            margin-top: 10px;
        """)
        layout.addWidget(theme_label)
        
        # Theme radio buttons
        self.theme_group = QButtonGroup(self)
        self.light_radio = NeumorphicRadioButton("Light")
        self.dark_radio = NeumorphicRadioButton("Dark")
        self.auto_radio = NeumorphicRadioButton("Auto (System)")
        
        self.theme_group.addButton(self.light_radio, 0)
        self.theme_group.addButton(self.dark_radio, 1)
        self.theme_group.addButton(self.auto_radio, 2)
        
        theme_layout = QVBoxLayout()
        theme_layout.setSpacing(10)
        theme_layout.addWidget(self.light_radio)
        theme_layout.addWidget(self.dark_radio)
        theme_layout.addWidget(self.auto_radio)
        layout.addLayout(theme_layout)
        
        # Set current theme
        mode = theme_manager.get_mode()
        if mode == 'light':
            self.light_radio.setChecked(True)
        elif mode == 'dark':
            self.dark_radio.setChecked(True)
        else:
            self.auto_radio.setChecked(True)
        
        # Accessibility section
        accessibility_label = QLabel("Accessibility")
        accessibility_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {palette.text_primary};
            background: transparent;
            margin-top: 10px;
        """)
        layout.addWidget(accessibility_label)
        
        self.high_contrast_checkbox = NeumorphicCheckBox("High Contrast Mode")
        self.high_contrast_checkbox.setChecked(theme_manager.is_high_contrast())
        layout.addWidget(self.high_contrast_checkbox)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(self.save_button, inset=False, intensity=1.0)
        self.save_button.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(self.cancel_button, inset=False, intensity=1.0)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def on_save(self):
        """Save settings."""
        # Update theme mode
        checked_button = self.theme_group.checkedButton()
        if checked_button == self.light_radio:
            theme_manager.set_mode('light')
        elif checked_button == self.dark_radio:
            theme_manager.set_mode('dark')
        else:
            theme_manager.set_mode('auto')
        
        # Update high contrast
        theme_manager.set_high_contrast(self.high_contrast_checkbox.isChecked())
        
        self.settings_changed.emit()
        self.accept()
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {palette.background};
            }}
        """)

