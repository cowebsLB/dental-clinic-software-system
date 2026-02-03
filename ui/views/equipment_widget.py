"""Equipment management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QDateEdit, QTextEdit,
                               QHBoxLayout)
from PySide6.QtCore import Qt, QDate
from ui.widgets.base_list_widget import BaseListWidget
from modules.equipment import equipment_manager
from modules.rooms import room_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)


class EquipmentDialog(QDialog):
    """Dialog for creating/editing equipment."""
    
    def __init__(self, equipment_data=None, parent=None):
        super().__init__(parent)
        self.equipment_data = equipment_data
        self.setWindowTitle("Edit Equipment" if equipment_data else "Add Equipment")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if equipment_data:
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
        
        # Equipment name
        self.equipment_name_input = QLineEdit()
        self._apply_input_style(self.equipment_name_input)
        form.addRow("Equipment Name", self.equipment_name_input)
        
        # Equipment type
        self.equipment_type_input = QLineEdit()
        self._apply_input_style(self.equipment_type_input)
        form.addRow("Equipment Type", self.equipment_type_input)
        
        # Room selection
        self.room_combo = QComboBox()
        self._populate_rooms()
        self._apply_input_style(self.room_combo)
        form.addRow("Room", self.room_combo)
        
        # Serial number
        self.serial_number_input = QLineEdit()
        self._apply_input_style(self.serial_number_input)
        form.addRow("Serial Number", self.serial_number_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['operational', 'maintenance', 'out_of_order', 'retired'])
        self._apply_input_style(self.status_combo)
        form.addRow("Status", self.status_combo)
        
        # Purchase date
        self.purchase_date_input = QDateEdit()
        self.purchase_date_input.setCalendarPopup(True)
        self.purchase_date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.purchase_date_input)
        form.addRow("Purchase Date", self.purchase_date_input)
        
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
        for widget in [self.equipment_name_input, self.equipment_type_input, self.room_combo,
                      self.serial_number_input, self.status_combo, self.purchase_date_input,
                      self.notes_input]:
            self._apply_input_style(widget)
    
    def _populate_rooms(self):
        """Populate room dropdown."""
        self.room_combo.clear()
        self.room_combo.addItem("", None)
        try:
            rooms = room_manager.list_all()
            for room in rooms:
                room_num = room.get('room_number', 'Unknown')
                self.room_combo.addItem(room_num, room.get('id'))
        except Exception as e:
            print(f"Error loading rooms: {e}")
    
    def load_data(self):
        """Load equipment data into form."""
        if self.equipment_data:
            self.equipment_name_input.setText(self.equipment_data.get('equipment_name', ''))
            self.equipment_type_input.setText(self.equipment_data.get('equipment_type', ''))
            
            # Set room
            room_id = self.equipment_data.get('room_id')
            if room_id:
                for i in range(self.room_combo.count()):
                    if self.room_combo.itemData(i) == room_id:
                        self.room_combo.setCurrentIndex(i)
                        break
            
            self.serial_number_input.setText(self.equipment_data.get('serial_number', ''))
            
            # Set status
            status = self.equipment_data.get('status', 'operational')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            # Set purchase date
            purchase_date_str = self.equipment_data.get('purchase_date')
            if purchase_date_str:
                try:
                    date = QDate.fromString(purchase_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.purchase_date_input.setDate(date)
                except:
                    pass
            
            self.notes_input.setPlainText(self.equipment_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        data = {
            'equipment_name': self.equipment_name_input.text().strip(),
            'equipment_type': self.equipment_type_input.text().strip(),
            'room_id': self.room_combo.currentData(),
            'serial_number': self.serial_number_input.text().strip(),
            'status': self.status_combo.currentText(),
            'purchase_date': self.purchase_date_input.date().toString(Qt.DateFormat.ISODate),
            'notes': self.notes_input.toPlainText().strip()
        }
        
        if not data['equipment_name']:
            QMessageBox.warning(self, tr("common.error"), "Equipment name is required")
            return
        
        try:
            if self.equipment_data:
                # Update
                success, error = equipment_manager.update(self.equipment_data['id'], data)
            else:
                # Create
                success, item_id, error = equipment_manager.create(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save equipment")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class EquipmentWidget(QWidget):
    """Equipment management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('equipment_name', 'Name'),
            ('equipment_type', 'Type'),
            ('room_id', 'Room'),
            ('serial_number', 'Serial Number'),
            ('status', 'Status'),
        ]
        
        self.list_widget = BaseListWidget(
            "Equipment",
            equipment_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = EquipmentDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, equipment_data: dict):
        """Handle edit."""
        dialog = EquipmentDialog(equipment_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

