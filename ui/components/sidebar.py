"""Sidebar navigation component with categorized groups."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFrame, QScrollArea)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QIcon, QFont
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import apply_neumorphic_effect


class SidebarGroup(QWidget):
    """A collapsible group in the sidebar."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.is_expanded = True
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(0)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the group UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header button (clickable to expand/collapse)
        arrow = "▾" if self.is_expanded else "▸"
        self.header_btn = QPushButton(f"{arrow} {self.title}")
        self.header_btn.setCheckable(False)
        self._update_header_style()
        self.header_btn.clicked.connect(self.toggle)
        layout.addWidget(self.header_btn)
        
        # Container for items
        self.items_container = QWidget()
        self.items_container.setLayout(self.items_layout)
        self.items_container.setVisible(self.is_expanded)
        layout.addWidget(self.items_container)
    
    def _update_header_style(self):
        """Update header button style with neumorphic theme."""
        palette = theme_manager.get_palette()
        self.header_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 11px;
                color: {palette.text_secondary};
                background-color: transparent;
                border: none;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {palette.base};
                border-radius: 8px;
            }}
        """)
    
    def toggle(self):
        """Toggle expand/collapse."""
        self.is_expanded = not self.is_expanded
        self.items_container.setVisible(self.is_expanded)
        # Update arrow icon if needed
        arrow = "▾" if self.is_expanded else "▸"
        self.header_btn.setText(f"{arrow} {self.title}")
    
    def add_item(self, item: QWidget):
        """Add an item to this group."""
        self.items_layout.addWidget(item)
    
    def set_expanded(self, expanded: bool):
        """Set expanded state."""
        if self.is_expanded != expanded:
            self.toggle()


class SidebarItem(QWidget):
    """A navigation item in the sidebar."""
    
    clicked_item = Signal(str)  # Emits the item_id when clicked
    
    def __init__(self, item_id: str, text: str, icon: str = None, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.text = text
        self.setup_ui(icon)
    
    def setup_ui(self, icon: str):
        """Setup the item UI."""
        # Icon mapping
        icon_map = {
            "dashboard": "🏠",
            "clients": "👥",
            "appointments": "📅",
            "treatment_plans": "📋",
            "medical_records": "📄",
            "prescriptions": "💊",
            "billing": "📄",
            "payments": "💳",
            "insurance": "🛡️",
            "staff": "👥",
            "doctors": "👨‍⚕️",
            "rooms": "🚪",
            "equipment": "⚙️",
            "reports": "📊",
            "calendar": "📅",
        }
        
        icon_text = icon_map.get(self.item_id, "•")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(12)
        
        # Icon label
        self.icon_label = QLabel(icon_text)
        self.icon_label.setStyleSheet("""
            background: transparent;
            font-size: 18px;
        """)
        layout.addWidget(self.icon_label)
        
        # Text label
        self.text_label = QLabel(self.text)
        self._update_style()
        layout.addWidget(self.text_label)
        layout.addStretch()
    
    def _update_style(self):
        """Update style with neumorphic theme."""
        palette = theme_manager.get_palette()
        self.text_label.setStyleSheet(f"""
            background: transparent;
            font-size: 14px;
            color: {palette.text_secondary};
        """)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border-radius: 10px;
            }}
            QWidget:hover {{
                background-color: {palette.base};
            }}
        """)
    
    def setChecked(self, checked: bool):
        """Set checked state."""
        palette = theme_manager.get_palette()
        if checked:
            # Apply inset effect for selected item
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {palette.base};
                    border-radius: 10px;
                }}
            """)
            apply_neumorphic_effect(self, inset=True, intensity=0.8)
            self.text_label.setStyleSheet(f"""
                background: transparent;
                font-size: 14px;
                color: {palette.text_primary};
                font-weight: 600;
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                    border-radius: 10px;
                }}
            """)
            # Remove effect
            self.setGraphicsEffect(None)
            self.text_label.setStyleSheet(f"""
                background: transparent;
                font-size: 14px;
                color: {palette.text_secondary};
            """)
    
    def mousePressEvent(self, event):
        """Handle click."""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_item.emit(self.item_id)


class Sidebar(QWidget):
    """Main sidebar navigation component."""
    
    item_selected = Signal(str)  # Emits item_id when an item is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_item = None
        self.setup_ui()
        self.setup_navigation()
    
    def setup_ui(self):
        """Setup sidebar UI."""
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
        _debug_log("sidebar.py:204", "Sidebar.setup_ui entry", {}, "H3")
        # #endregion
        self.setFixedWidth(280)
        # #region agent log
        _debug_log("sidebar.py:207", "Before _apply_theme", {}, "H3")
        # #endregion
        self._apply_theme()
        # #region agent log
        _debug_log("sidebar.py:210", "After _apply_theme", {}, "H3")
        # #endregion
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
        # #region agent log
        _debug_log("sidebar.py:214", "Before layout creation", {}, "H3")
        # #endregion
        layout = QVBoxLayout(self)
        # #region agent log
        _debug_log("sidebar.py:216", "Layout created", {"layout_exists": layout is not None}, "H3")
        # #endregion
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for navigation items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Container widget for scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        # #region agent log
        _debug_log("sidebar.py:231", "Before layout.addWidget(scroll)", {"layout_exists": 'layout' in locals()}, "H3")
        # #endregion
        layout.addWidget(scroll)
        # #region agent log
        _debug_log("sidebar.py:233", "Sidebar.setup_ui complete", {}, "H3")
        # #endregion
    
    def _apply_theme(self):
        """Apply neumorphic theme to sidebar."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.surface};
                border-right: 1px solid {palette.border};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {palette.base};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {palette.border};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {palette.text_secondary};
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._apply_theme()
        # Update all items
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if isinstance(widget, SidebarGroup):
                widget._update_header_style()
                for j in range(widget.items_layout.count()):
                    item_widget = widget.items_layout.itemAt(j).widget()
                    if isinstance(item_widget, SidebarItem):
                        item_widget._update_style()
                        # Reapply checked state if needed
                        if item_widget == self.current_item:
                            item_widget.setChecked(True)
    
    def setup_navigation(self):
        """Setup navigation groups and items."""
        # Dashboard group
        dashboard_group = SidebarGroup("Main")
        dashboard_item = SidebarItem("dashboard", tr("dashboard.title"))
        dashboard_item.clicked_item.connect(self.on_item_clicked)
        dashboard_group.add_item(dashboard_item)
        self.content_layout.insertWidget(0, dashboard_group)
        
        # Patients & Clients group
        patients_group = SidebarGroup("Patients & Clients")
        patients_items = [
            ("clients", tr("clients.title")),
            ("appointments", tr("appointments.title")),
        ]
        for item_id, item_text in patients_items:
            item = SidebarItem(item_id, item_text)
            item.clicked_item.connect(self.on_item_clicked)
            patients_group.add_item(item)
        self.content_layout.insertWidget(1, patients_group)
        
        # Medical Records group
        medical_group = SidebarGroup("Medical")
        medical_items = [
            ("treatment_plans", "Treatment Plans"),
            ("medical_records", "Medical Records"),
            ("prescriptions", "Prescriptions"),
        ]
        for item_id, item_text in medical_items:
            item = SidebarItem(item_id, item_text)
            item.clicked_item.connect(self.on_item_clicked)
            medical_group.add_item(item)
        self.content_layout.insertWidget(2, medical_group)
        
        # Billing & Payments group
        billing_group = SidebarGroup("Billing")
        billing_items = [
            ("billing", "Billing & Invoicing"),
            ("payments", "Payments"),
            ("insurance", "Insurance"),
        ]
        for item_id, item_text in billing_items:
            item = SidebarItem(item_id, item_text)
            item.clicked_item.connect(self.on_item_clicked)
            billing_group.add_item(item)
        self.content_layout.insertWidget(3, billing_group)
        
        # Administration group
        admin_group = SidebarGroup("Administration")
        admin_items = [
            ("staff", "Staff"),
            ("doctors", "Doctors"),
            ("rooms", "Rooms"),
            ("equipment", "Equipment"),
        ]
        for item_id, item_text in admin_items:
            item = SidebarItem(item_id, item_text)
            item.clicked_item.connect(self.on_item_clicked)
            admin_group.add_item(item)
        self.content_layout.insertWidget(4, admin_group)
        
        # Reports & Analytics group
        reports_group = SidebarGroup("Reports")
        reports_items = [
            ("reports", "Reports & Analytics"),
            ("calendar", "Calendar"),
        ]
        for item_id, item_text in reports_items:
            item = SidebarItem(item_id, item_text)
            item.clicked_item.connect(self.on_item_clicked)
            reports_group.add_item(item)
        self.content_layout.insertWidget(5, reports_group)
        
        # Set dashboard as default selected
        dashboard_item.setChecked(True)
        self.current_item = dashboard_item
        
        # Add user info at bottom
        self.user_info = QLabel("Logged in as admin")
        self._update_user_info_style()
        self.content_layout.addWidget(self.user_info)
    
    def _update_user_info_style(self):
        """Update user info label style."""
        palette = theme_manager.get_palette()
        self.user_info.setStyleSheet(f"""
            color: {palette.text_secondary};
            font-size: 12px;
            padding: 15px 20px;
            background: transparent;
        """)
    
    def on_item_clicked(self, item_id: str):
        """Handle item click."""
        # Uncheck previous item
        if self.current_item:
            self.current_item.setChecked(False)
        
        # Find and check new item
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if isinstance(widget, SidebarGroup):
                for j in range(widget.items_layout.count()):
                    item_widget = widget.items_layout.itemAt(j).widget()
                    if isinstance(item_widget, SidebarItem) and item_widget.item_id == item_id:
                        item_widget.setChecked(True)
                        self.current_item = item_widget
                        break
        
        # Emit signal
        self.item_selected.emit(item_id)
    
    def select_item(self, item_id: str, emit_signal: bool = False):
        """Programmatically select an item."""
        # Uncheck previous item
        if self.current_item:
            self.current_item.setChecked(False)
        
        # Find and check new item
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if isinstance(widget, SidebarGroup):
                for j in range(widget.items_layout.count()):
                    item_widget = widget.items_layout.itemAt(j).widget()
                    if isinstance(item_widget, SidebarItem) and item_widget.item_id == item_id:
                        item_widget.setChecked(True)
                        self.current_item = item_widget
                        if emit_signal:
                            self.item_selected.emit(item_id)
                        return

