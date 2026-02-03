"""Neumorphic form controls."""

from PySide6.QtWidgets import (QCheckBox, QRadioButton, QComboBox, QSpinBox,
                               QDoubleSpinBox, QSlider, QWidget, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import apply_neumorphic_effect


class NeumorphicCheckBox(QCheckBox):
    """Neumorphic styled checkbox."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._update_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update checkbox style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {palette.text_primary};
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                background-color: {palette.base};
                border: 2px solid {palette.border};
            }}
            QCheckBox::indicator:hover {{
                background-color: {palette.surface};
            }}
            QCheckBox::indicator:checked {{
                background-color: {palette.accent};
                border-color: {palette.accent};
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()


class NeumorphicRadioButton(QRadioButton):
    """Neumorphic styled radio button."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._update_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update radio button style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QRadioButton {{
                color: {palette.text_primary};
                font-size: 14px;
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                background-color: {palette.base};
                border: 2px solid {palette.border};
            }}
            QRadioButton::indicator:hover {{
                background-color: {palette.surface};
            }}
            QRadioButton::indicator:checked {{
                background-color: {palette.accent};
                border-color: {palette.accent};
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()


class NeumorphicComboBox(QComboBox):
    """Neumorphic styled combobox."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._update_style()
        apply_neumorphic_effect(self, inset=True, intensity=0.8)
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update combobox style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {palette.base};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
            }}
            QComboBox:hover {{
                border-color: {palette.accent};
            }}
            QComboBox:focus {{
                border-color: {palette.accent};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {palette.text_primary};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 8px;
                selection-background-color: {palette.accent};
                selection-color: {palette.text_primary};
                padding: 4px;
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()


class NeumorphicSpinBox(QSpinBox):
    """Neumorphic styled spinbox."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._update_style()
        apply_neumorphic_effect(self, inset=True, intensity=0.8)
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update spinbox style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {palette.base};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }}
            QSpinBox:focus {{
                border-color: {palette.accent};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {palette.surface};
                border: none;
                width: 20px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {palette.accent};
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()


class NeumorphicDoubleSpinBox(QDoubleSpinBox):
    """Neumorphic styled double spinbox."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._update_style()
        apply_neumorphic_effect(self, inset=True, intensity=0.8)
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update double spinbox style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {palette.base};
                color: {palette.text_primary};
                border: 2px solid {palette.border};
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }}
            QDoubleSpinBox:focus {{
                border-color: {palette.accent};
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                background-color: {palette.surface};
                border: none;
                width: 20px;
            }}
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {palette.accent};
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()


class NeumorphicSlider(QSlider):
    """Neumorphic styled slider."""
    
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._update_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update slider style."""
        palette = theme_manager.get_palette()
        if self.orientation() == Qt.Orientation.Horizontal:
            self.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    background-color: {palette.base};
                    height: 8px;
                    border-radius: 4px;
                }}
                QSlider::handle:horizontal {{
                    background-color: {palette.accent};
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    margin: -6px 0;
                }}
                QSlider::handle:horizontal:hover {{
                    background-color: {palette.accent_hover};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QSlider::groove:vertical {{
                    background-color: {palette.base};
                    width: 8px;
                    border-radius: 4px;
                }}
                QSlider::handle:vertical {{
                    background-color: {palette.accent};
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    margin: 0 -6px;
                }}
                QSlider::handle:vertical:hover {{
                    background-color: {palette.accent_hover};
                }}
            """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()

