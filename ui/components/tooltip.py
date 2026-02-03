"""Custom neumorphic tooltips."""

from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPainter, QPen, QBrush
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import apply_neumorphic_effect


class NeumorphicTooltip(QLabel):
    """Neumorphic styled tooltip."""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._update_style()
        apply_neumorphic_effect(self, inset=False, intensity=0.8)
        
        # Fade-in animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update tooltip style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()
    
    def showEvent(self, event):
        """Show tooltip with fade-in."""
        super().showEvent(event)
        self.setWindowOpacity(0.0)
        self.fade_animation.start()
    
    def hideEvent(self, event):
        """Hide tooltip."""
        self.fade_animation.stop()
        super().hideEvent(event)


def show_tooltip(widget: QWidget, text: str, duration: int = 3000):
    """Show a tooltip for a widget.
    
    Args:
        widget: Widget to show tooltip for
        text: Tooltip text
        duration: Duration in milliseconds
    """
    if not widget.isVisible():
        return
    
    # Get widget position
    pos = widget.mapToGlobal(widget.rect().bottomLeft())
    
    # Create tooltip
    tooltip = NeumorphicTooltip(text)
    tooltip.move(pos.x(), pos.y() + 5)
    tooltip.show()
    
    # Auto-hide after duration
    QTimer.singleShot(duration, tooltip.close)

