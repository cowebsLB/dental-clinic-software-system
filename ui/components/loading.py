"""Loading indicators and progress bars with neumorphic styling."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QProgressBar, QFrame)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import apply_neumorphic_effect


class NeumorphicSpinner(QWidget):
    """Neumorphic circular spinner."""
    
    def __init__(self, parent=None, size: int = 40):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.setFixedSize(size, size)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_angle)
        self.timer.start(50)  # Update every 50ms
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_angle(self):
        """Update rotation angle."""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self.update()
    
    def paintEvent(self, event):
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        palette = theme_manager.get_palette()
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 5
        
        # Draw spinner arc
        pen = QPen()
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setColor(QColor(palette.accent))
        painter.setPen(pen)
        
        # Draw arc that rotates
        start_angle = self.angle * 16  # Qt uses 1/16th degree units
        span_angle = 270 * 16  # 270 degree arc
        
        painter.drawArc(center.x() - radius, center.y() - radius,
                       radius * 2, radius * 2, start_angle, span_angle)
    
    def start(self):
        """Start the spinner."""
        self.timer.start()
        self.show()
    
    def stop(self):
        """Stop the spinner."""
        self.timer.stop()
        self.hide()


class NeumorphicProgressBar(QProgressBar):
    """Neumorphic styled progress bar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._update_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update progress bar style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: {palette.base};
                border: 2px solid {palette.border};
                border-radius: 10px;
                height: 20px;
                text-align: center;
                color: {palette.text_primary};
            }}
            QProgressBar::chunk {{
                background-color: {palette.accent};
                border-radius: 8px;
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()


class LoadingOverlay(QWidget):
    """Semi-transparent loading overlay with spinner."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent:
            parent.installEventFilter(self)
        self.setup_ui()
        self.hide()
    
    def setup_ui(self):
        """Setup overlay UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spinner
        self.spinner = NeumorphicSpinner(size=50)
        layout.addWidget(self.spinner)
        
        # Label
        self.label = QLabel("Loading...")
        palette = theme_manager.get_palette()
        self.label.setStyleSheet(f"""
            color: {palette.text_primary};
            font-size: 14px;
            background: transparent;
        """)
        layout.addWidget(self.label)
    
    def eventFilter(self, obj, event):
        """Resize overlay to match parent."""
        if obj == self.parent():
            if event.type() == event.Type.Resize:
                self.setGeometry(self.parent().rect())
        return super().eventFilter(obj, event)
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading overlay."""
        self.label.setText(message)
        self.spinner.start()
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()
    
    def hide_loading(self):
        """Hide loading overlay."""
        self.spinner.stop()
        self.hide()


class SkeletonLoader(QWidget):
    """Skeleton loader placeholder (neumorphic card)."""
    
    def __init__(self, width: int = 200, height: int = 100, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self._update_style()
        apply_neumorphic_effect(self, inset=False, intensity=0.5)
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_style(self):
        """Update skeleton style."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.base};
                border: 1px solid {palette.border};
                border-radius: 12px;
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_style()

