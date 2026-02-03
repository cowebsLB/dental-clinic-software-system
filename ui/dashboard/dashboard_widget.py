"""Main dashboard widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import apply_neumorphic_effect, get_neumorphic_card_style

# #region agent log
import json
DEBUG_LOG_PATH = r"c:\Users\COWebs.lb\Desktop\my files\01-Projects\dental clinic software system\.cursor\debug.log"
def _debug_log(location, message, data=None, hypothesis_id=None):
    try:
        with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
            log_entry = {
                "location": location,
                "message": message,
                "data": data or {},
                "timestamp": __import__('time').time() * 1000,
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": hypothesis_id
            }
            f.write(json.dumps(log_entry) + '\n')
    except: pass
# #endregion

class DashboardWidget(QWidget):
    """Dashboard widget."""
    
    def __init__(self, parent=None):
        # #region agent log
        _debug_log("dashboard_widget.py:14", "DashboardWidget.__init__ entry", {}, "H3")
        # #endregion
        super().__init__(parent)
        # #region agent log
        _debug_log("dashboard_widget.py:17", "After super().__init__", {}, "H3")
        # #endregion
        self.setup_ui()
        # #region agent log
        _debug_log("dashboard_widget.py:19", "DashboardWidget.__init__ complete", {}, "H3")
        # #endregion
    
    def setup_ui(self):
        """Setup UI."""
        # #region agent log
        _debug_log("dashboard_widget.py:22", "setup_ui entry", {}, "H3")
        # #endregion
        # Set transparent background
        self.setStyleSheet("background: transparent;")
        
        # Connect to theme changes
        # #region agent log
        _debug_log("dashboard_widget.py:28", "Before theme_manager connection", {"theme_manager_exists": theme_manager is not None}, "H5")
        # #endregion
        theme_manager.theme_changed.connect(self._on_theme_changed)
        # #region agent log
        _debug_log("dashboard_widget.py:30", "After theme_manager connection", {}, "H5")
        # #endregion
        
        layout = QVBoxLayout(self)
        # #region agent log
        _debug_log("dashboard_widget.py:32", "Layout created", {}, "H3")
        # #endregion
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title - large, neumorphic style
        # #region agent log
        _debug_log("dashboard_widget.py:37", "Before title label creation", {}, "H3")
        # #endregion
        self.title_label = QLabel(tr("dashboard.title"))
        # #region agent log
        _debug_log("dashboard_widget.py:39", "Title label created", {}, "H3")
        # #endregion
        self._update_title_style()
        layout.addWidget(self.title_label)
        
        # Metrics cards
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        # #region agent log
        _debug_log("dashboard_widget.py:46", "Before revenue card creation", {}, "H3")
        # #endregion
        revenue_card = self.create_metric_card("Revenue", "$0.00", "This Month", "#4A90E2")
        # #region agent log
        _debug_log("dashboard_widget.py:48", "Revenue card created", {}, "H3")
        # #endregion
        metrics_layout.addWidget(revenue_card)
        
        appointments_card = self.create_metric_card("Appointments", "0", "Today", "#9B59B6")
        metrics_layout.addWidget(appointments_card)
        
        patients_card = self.create_metric_card("Patients", "0", "Total", "#9B59B6")
        metrics_layout.addWidget(patients_card)
        
        layout.addLayout(metrics_layout)
        
        # Recent appointments
        self.recent_label = QLabel(tr("dashboard.recent_appointments"))
        self._update_recent_label_style()
        layout.addWidget(self.recent_label)
        
        # TODO: Add recent appointments list
        
        layout.addStretch()
        # #region agent log
        _debug_log("dashboard_widget.py:66", "setup_ui complete", {}, "H3")
        # #endregion
    
    def _update_title_style(self):
        """Update title style with theme."""
        # #region agent log
        _debug_log("dashboard_widget.py:70", "_update_title_style entry", {}, "H4")
        # #endregion
        try:
            palette = theme_manager.get_palette()
            # #region agent log
            _debug_log("dashboard_widget.py:73", "Got palette for title", {"text_primary": palette.text_primary}, "H4")
            # #endregion
            stylesheet = f"""
            font-size: 48px;
            font-weight: 300;
            color: {palette.text_primary};
            background: transparent;
        """
            self.title_label.setStyleSheet(stylesheet)
            # #region agent log
            _debug_log("dashboard_widget.py:82", "Title style applied", {}, "H4")
            # #endregion
        except Exception as e:
            # #region agent log
            _debug_log("dashboard_widget.py:84", "Exception in _update_title_style", {"error": str(e), "type": type(e).__name__}, "H4")
            # #endregion
            raise
    
    def _update_recent_label_style(self):
        """Update recent label style."""
        palette = theme_manager.get_palette()
        self.recent_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {palette.text_primary};
            background: transparent;
            margin-top: 20px;
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_title_style()
        self._update_recent_label_style()
        # Update all metric cards
        if self.layout():
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, '_update_card_style'):
                        widget._update_card_style()
    
    def create_metric_card(self, title: str, value: str, subtitle: str, icon_color: str) -> QWidget:
        """Create a neumorphic metric card."""
        # #region agent log
        _debug_log("dashboard_widget.py:99", "create_metric_card entry", {"title": title}, "H3,H4")
        # #endregion
        card = QWidget()
        card.setFixedHeight(180)
        card._title = title
        card._value = value
        card._subtitle = subtitle
        card._icon_color = icon_color
        card._update_card_style = lambda: self._update_card_style(card)
        
        # Apply neumorphic outset effect
        # #region agent log
        _debug_log("dashboard_widget.py:114", "Before apply_neumorphic_effect", {}, "H4")
        # #endregion
        apply_neumorphic_effect(card, inset=False, intensity=1.0)
        # #region agent log
        _debug_log("dashboard_widget.py:116", "After apply_neumorphic_effect", {}, "H4")
        # #endregion
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(10)
        
        # Header with title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        card.title_label = QLabel(title)
        header_layout.addWidget(card.title_label)
        header_layout.addStretch()
        
        card_layout.addLayout(header_layout)
        
        # Value - large
        card.value_label = QLabel(value)
        card_layout.addWidget(card.value_label)
        
        # Subtitle
        card.subtitle_label = QLabel(subtitle)
        card_layout.addWidget(card.subtitle_label)
        
        card_layout.addStretch()
        
        # #region agent log
        _debug_log("dashboard_widget.py:109", "Before _update_card_style", {}, "H4")
        # #endregion
        # Update card style after labels are created
        self._update_card_style(card)
        # #region agent log
        _debug_log("dashboard_widget.py:111", "After _update_card_style", {}, "H4")
        # #endregion
        
        return card
    
    def _update_card_style(self, card: QWidget):
        """Update card style with theme."""
        # #region agent log
        _debug_log("dashboard_widget.py:221", "_update_card_style entry", {"has_title_label": hasattr(card, 'title_label'), "has_value_label": hasattr(card, 'value_label'), "has_subtitle_label": hasattr(card, 'subtitle_label')}, "H4")
        # #endregion
        palette = theme_manager.get_palette()
        
        # Card background
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.base};
                border-radius: 20px;
                border: 1px solid {palette.border};
            }}
        """)
        
        # Only update label styles if they exist (safety check)
        if hasattr(card, 'title_label') and card.title_label:
            # Title label
            card.title_label.setStyleSheet(f"""
                color: {palette.text_secondary};
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            """)
        
        if hasattr(card, 'value_label') and card.value_label:
            # Value label
            card.value_label.setStyleSheet(f"""
                color: {card._icon_color};
                font-size: 42px;
                font-weight: 700;
                background: transparent;
            """)
        
        if hasattr(card, 'subtitle_label') and card.subtitle_label:
            # Subtitle label
            card.subtitle_label.setStyleSheet(f"""
                color: {palette.text_secondary};
                font-size: 12px;
                background: transparent;
            """)

