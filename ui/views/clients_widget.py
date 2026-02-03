"""Clients management widget."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDialog, QFormLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from ui.widgets.base_list_widget import BaseListWidget
from modules.clients import client_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)


class ClientDialog(QDialog):
    """Dialog for creating/editing clients."""
    
    def __init__(self, client_data=None, parent=None):
        super().__init__(parent)
        self.client_data = client_data
        self.setWindowTitle(tr("clients.edit_client") if client_data else tr("clients.add_client"))
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if client_data:
            self.load_data()
    
    def setup_ui(self):
        """Setup UI."""
        # Apply neumorphic theme
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
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.first_name_input = QLineEdit()
        self._apply_input_style(self.first_name_input)
        form.addRow(tr("clients.first_name"), self.first_name_input)
        
        self.last_name_input = QLineEdit()
        self._apply_input_style(self.last_name_input)
        form.addRow(tr("clients.last_name"), self.last_name_input)
        
        self.phone_input = QLineEdit()
        self._apply_input_style(self.phone_input)
        form.addRow(tr("clients.phone"), self.phone_input)
        
        self.email_input = QLineEdit()
        self._apply_input_style(self.email_input)
        form.addRow(tr("clients.email"), self.email_input)
        
        self.dob_input = QLineEdit()
        self.dob_input.setPlaceholderText("YYYY-MM-DD")
        self._apply_input_style(self.dob_input)
        form.addRow(tr("clients.date_of_birth"), self.dob_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self._apply_input_style(self.address_input)
        form.addRow(tr("clients.address"), self.address_input)
        
        self.medical_history_input = QTextEdit()
        self.medical_history_input.setMaximumHeight(100)
        self._apply_input_style(self.medical_history_input)
        form.addRow(tr("clients.medical_history"), self.medical_history_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self._apply_input_style(self.notes_input)
        form.addRow(tr("clients.notes"), self.notes_input)
        
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
        # Reapply input styles
        for widget in [self.first_name_input, self.last_name_input, self.phone_input,
                      self.email_input, self.dob_input, self.address_input,
                      self.medical_history_input, self.notes_input]:
            self._apply_input_style(widget)
    
    def load_data(self):
        """Load client data into form."""
        if self.client_data:
            self.first_name_input.setText(self.client_data.get('first_name', ''))
            self.last_name_input.setText(self.client_data.get('last_name', ''))
            self.phone_input.setText(self.client_data.get('phone', ''))
            self.email_input.setText(self.client_data.get('email', ''))
            self.dob_input.setText(self.client_data.get('date_of_birth', ''))
            self.address_input.setPlainText(self.client_data.get('address', ''))
            self.medical_history_input.setPlainText(self.client_data.get('medical_history', ''))
            self.notes_input.setPlainText(self.client_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        data = {
            'first_name': self.first_name_input.text().strip(),
            'last_name': self.last_name_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'date_of_birth': self.dob_input.text().strip(),
            'address': self.address_input.toPlainText().strip(),
            'medical_history': self.medical_history_input.toPlainText().strip(),
            'notes': self.notes_input.toPlainText().strip(),
            'created_by': user_id
        }
        
        if not data['first_name'] or not data['last_name']:
            QMessageBox.warning(self, tr("common.error"), "First name and last name are required")
            return
        
        try:
            if self.client_data:
                # Update
                success, error = client_manager.update(self.client_data['id'], data)
            else:
                # Create
                success, item_id, error = client_manager.create(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save client")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class ClientsWidget(QWidget):
    """Clients management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('first_name', 'First Name'),
            ('last_name', 'Last Name'),
            ('phone', 'Phone'),
            ('email', 'Email'),
            ('date_of_birth', 'Date of Birth'),
        ]
        
        self.list_widget = BaseListWidget(
            tr("clients.title"),
            client_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = ClientDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, client_data: dict):
        """Handle edit."""
        dialog = ClientDialog(client_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

