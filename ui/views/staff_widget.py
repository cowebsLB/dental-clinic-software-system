"""Staff management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QCheckBox, QDateEdit,
                               QHBoxLayout)
from PySide6.QtCore import Qt, QDate
from ui.widgets.base_list_widget import BaseListWidget
from modules.staff import staff_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)
from database.local_cache import local_cache


class StaffDialog(QDialog):
    """Dialog for creating/editing staff."""
    
    def __init__(self, staff_data=None, parent=None):
        super().__init__(parent)
        self.staff_data = staff_data
        self.setWindowTitle("Edit Staff" if staff_data else "Add Staff")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if staff_data:
            self.load_data()
    
    def setup_ui(self):
        """Setup UI."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {palette.background};
            }}
            QLabel {{
                color: {palette.text_primary};
                font-size: 14px;
                background: transparent;
            }}
        """)
        
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # User selection
        self.user_combo = QComboBox()
        self._populate_users()
        self._apply_input_style(self.user_combo)
        form.addRow("User", self.user_combo)
        
        # Position
        self.position_input = QLineEdit()
        self._apply_input_style(self.position_input)
        form.addRow("Position", self.position_input)
        
        # Hire date
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.hire_date_input)
        form.addRow("Hire Date", self.hire_date_input)
        
        # Active checkbox
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        form.addRow("Active", self.is_active_checkbox)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        save_button = QPushButton(tr("common.save"))
        save_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(save_button, inset=False, intensity=1.0)
        save_button.clicked.connect(self.on_save)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton(tr("common.cancel"))
        cancel_button.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(cancel_button, inset=False, intensity=1.0)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _apply_input_style(self, input_widget):
        """Apply neumorphic input style."""
        input_widget.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(input_widget, inset=True, intensity=0.8)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {palette.background};
            }}
            QLabel {{
                color: {palette.text_primary};
                font-size: 14px;
                background: transparent;
            }}
        """)
        for widget in [self.user_combo, self.position_input, self.hire_date_input]:
            self._apply_input_style(widget)
    
    def _populate_users(self):
        """Populate user dropdown."""
        self.user_combo.clear()
        self.user_combo.addItem("", None)
        try:
            users = local_cache.query('users', limit=100)
            for user in users:
                username = user.get('username') or user.get('email', 'Unknown')
                self.user_combo.addItem(username, user.get('id'))
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def load_data(self):
        """Load staff data into form."""
        if self.staff_data:
            # Set user
            user_id = self.staff_data.get('user_id')
            if user_id:
                for i in range(self.user_combo.count()):
                    if self.user_combo.itemData(i) == user_id:
                        self.user_combo.setCurrentIndex(i)
                        break
            
            # Set position
            self.position_input.setText(self.staff_data.get('position', ''))
            
            # Set hire date
            hire_date_str = self.staff_data.get('hire_date')
            if hire_date_str:
                try:
                    date = QDate.fromString(hire_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.hire_date_input.setDate(date)
                except:
                    pass
            
            # Set active
            self.is_active_checkbox.setChecked(self.staff_data.get('is_active', True))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        selected_user_id = self.user_combo.currentData()
        if not selected_user_id:
            QMessageBox.warning(self, tr("common.error"), "User is required")
            return
        
        data = {
            'user_id': selected_user_id,
            'position': self.position_input.text().strip(),
            'hire_date': self.hire_date_input.date().toString(Qt.DateFormat.ISODate),
            'is_active': self.is_active_checkbox.isChecked(),
            'created_by': user_id,
            'last_modified_by': user_id
        }
        
        if not data['position']:
            QMessageBox.warning(self, tr("common.error"), "Position is required")
            return
        
        try:
            if self.staff_data:
                # Update
                success, error = staff_manager.update(self.staff_data['id'], data)
            else:
                # Create
                success, item_id, error = staff_manager.create(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save staff")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class StaffWidget(QWidget):
    """Staff management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('user_id', 'User ID'),
            ('position', 'Position'),
            ('hire_date', 'Hire Date'),
            ('is_active', 'Active'),
        ]
        
        self.list_widget = BaseListWidget(
            "Staff",
            staff_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = StaffDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, staff_data: dict):
        """Handle edit."""
        dialog = StaffDialog(staff_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

