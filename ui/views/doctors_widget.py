"""Doctors management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QCheckBox, QDateEdit,
                               QHBoxLayout)
from PySide6.QtCore import Qt, QDate
from ui.widgets.base_list_widget import BaseListWidget
from modules.doctors import doctor_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)
from database.local_cache import local_cache


class DoctorDialog(QDialog):
    """Dialog for creating/editing doctors."""
    
    def __init__(self, doctor_data=None, parent=None):
        super().__init__(parent)
        self.doctor_data = doctor_data
        self.setWindowTitle("Edit Doctor" if doctor_data else "Add Doctor")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if doctor_data:
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
        
        # Specialization
        self.specialization_input = QLineEdit()
        self._apply_input_style(self.specialization_input)
        form.addRow("Specialization", self.specialization_input)
        
        # License number
        self.license_number_input = QLineEdit()
        self._apply_input_style(self.license_number_input)
        form.addRow("License Number", self.license_number_input)
        
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
        for widget in [self.user_combo, self.specialization_input, self.license_number_input,
                      self.hire_date_input]:
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
        """Load doctor data into form."""
        if self.doctor_data:
            # Set user
            user_id = self.doctor_data.get('user_id')
            if user_id:
                for i in range(self.user_combo.count()):
                    if self.user_combo.itemData(i) == user_id:
                        self.user_combo.setCurrentIndex(i)
                        break
            
            # Set specialization
            self.specialization_input.setText(self.doctor_data.get('specialization', ''))
            
            # Set license number
            self.license_number_input.setText(self.doctor_data.get('license_number', ''))
            
            # Set hire date
            hire_date_str = self.doctor_data.get('hire_date')
            if hire_date_str:
                try:
                    date = QDate.fromString(hire_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.hire_date_input.setDate(date)
                except:
                    pass
            
            # Set active
            self.is_active_checkbox.setChecked(self.doctor_data.get('is_active', True))
    
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
            'specialization': self.specialization_input.text().strip(),
            'license_number': self.license_number_input.text().strip(),
            'hire_date': self.hire_date_input.date().toString(Qt.DateFormat.ISODate),
            'is_active': self.is_active_checkbox.isChecked(),
            'created_by': user_id,
            'last_modified_by': user_id
        }
        
        try:
            if self.doctor_data:
                # Update
                success, error = doctor_manager.update(self.doctor_data['id'], data)
            else:
                # Create
                success, item_id, error = doctor_manager.create(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save doctor")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class DoctorsWidget(QWidget):
    """Doctors management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('user_id', 'User ID'),
            ('specialization', 'Specialization'),
            ('license_number', 'License Number'),
            ('hire_date', 'Hire Date'),
            ('is_active', 'Active'),
        ]
        
        self.list_widget = BaseListWidget(
            "Doctors",
            doctor_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = DoctorDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, doctor_data: dict):
        """Handle edit."""
        dialog = DoctorDialog(doctor_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

