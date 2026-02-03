"""Rooms management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QCheckBox, QSpinBox, QTextEdit,
                               QHBoxLayout)
from PySide6.QtCore import Qt
from ui.widgets.base_list_widget import BaseListWidget
from modules.rooms import room_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)


class RoomDialog(QDialog):
    """Dialog for creating/editing rooms."""
    
    def __init__(self, room_data=None, parent=None):
        super().__init__(parent)
        self.room_data = room_data
        self.setWindowTitle("Edit Room" if room_data else "Add Room")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if room_data:
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
        
        # Room number
        self.room_number_input = QLineEdit()
        self._apply_input_style(self.room_number_input)
        form.addRow("Room Number", self.room_number_input)
        
        # Room type
        self.room_type_input = QLineEdit()
        self._apply_input_style(self.room_type_input)
        form.addRow("Room Type", self.room_type_input)
        
        # Capacity
        self.capacity_input = QSpinBox()
        self.capacity_input.setMinimum(1)
        self.capacity_input.setMaximum(100)
        self.capacity_input.setValue(1)
        self._apply_input_style(self.capacity_input)
        form.addRow("Capacity", self.capacity_input)
        
        # Available checkbox
        self.is_available_checkbox = QCheckBox()
        self.is_available_checkbox.setChecked(True)
        form.addRow("Available", self.is_available_checkbox)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self._apply_input_style(self.notes_input)
        form.addRow("Notes", self.notes_input)
        
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
        for widget in [self.room_number_input, self.room_type_input, self.capacity_input,
                      self.notes_input]:
            self._apply_input_style(widget)
    
    def load_data(self):
        """Load room data into form."""
        if self.room_data:
            self.room_number_input.setText(self.room_data.get('room_number', ''))
            self.room_type_input.setText(self.room_data.get('room_type', ''))
            self.capacity_input.setValue(self.room_data.get('capacity', 1))
            self.is_available_checkbox.setChecked(self.room_data.get('is_available', True))
            self.notes_input.setPlainText(self.room_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        data = {
            'room_number': self.room_number_input.text().strip(),
            'room_type': self.room_type_input.text().strip(),
            'capacity': self.capacity_input.value(),
            'is_available': self.is_available_checkbox.isChecked(),
            'notes': self.notes_input.toPlainText().strip(),
            'created_by': user_id,
            'last_modified_by': user_id
        }
        
        if not data['room_number']:
            QMessageBox.warning(self, tr("common.error"), "Room number is required")
            return
        
        try:
            if self.room_data:
                # Update
                success, error = room_manager.update(self.room_data['id'], data)
            else:
                # Create
                success, item_id, error = room_manager.create(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save room")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class RoomsWidget(QWidget):
    """Rooms management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('room_number', 'Room Number'),
            ('room_type', 'Type'),
            ('capacity', 'Capacity'),
            ('is_available', 'Available'),
        ]
        
        self.list_widget = BaseListWidget(
            "Rooms",
            room_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = RoomDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, room_data: dict):
        """Handle edit."""
        dialog = RoomDialog(room_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

