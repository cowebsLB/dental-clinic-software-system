"""Prescriptions management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QDateTimeEdit,
                               QTextEdit, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView)
from PySide6.QtCore import Qt, QDateTime, QDate, QTime
from ui.widgets.base_list_widget import BaseListWidget
from modules.prescriptions import prescription_manager
from modules.clients import client_manager
from modules.doctors import doctor_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)
from datetime import datetime


class PrescriptionDialog(QDialog):
    """Dialog for creating/editing prescriptions."""
    
    def __init__(self, prescription_data=None, parent=None):
        super().__init__(parent)
        self.prescription_data = prescription_data
        self.setWindowTitle("Edit Prescription" if prescription_data else "Add Prescription")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setup_ui()
        
        if prescription_data:
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
        
        # Client selection
        self.client_combo = QComboBox()
        self._populate_clients()
        self._apply_input_style(self.client_combo)
        form.addRow("Client", self.client_combo)
        
        # Doctor selection
        self.doctor_combo = QComboBox()
        self._populate_doctors()
        self._apply_input_style(self.doctor_combo)
        form.addRow("Doctor", self.doctor_combo)
        
        # Prescription date
        self.prescription_date_input = QDateTimeEdit()
        self.prescription_date_input.setCalendarPopup(True)
        self.prescription_date_input.setDateTime(QDateTime.currentDateTime())
        self._apply_input_style(self.prescription_date_input)
        form.addRow("Prescription Date", self.prescription_date_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['active', 'completed', 'cancelled'])
        self._apply_input_style(self.status_combo)
        form.addRow("Status", self.status_combo)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self._apply_input_style(self.notes_input)
        form.addRow("Notes", self.notes_input)
        
        layout.addLayout(form)
        
        # Prescription items table (simplified - can be enhanced later)
        items_label = QLineEdit()
        items_label.setPlaceholderText("Medication items (format: Name, Dosage, Frequency, Duration)")
        items_label.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(items_label, inset=True, intensity=0.8)
        layout.addWidget(items_label)
        self.items_input = items_label
        
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
        for widget in [self.client_combo, self.doctor_combo, self.prescription_date_input,
                      self.status_combo, self.notes_input]:
            self._apply_input_style(widget)
    
    def _populate_clients(self):
        """Populate client dropdown."""
        self.client_combo.clear()
        self.client_combo.addItem("", None)
        try:
            clients = client_manager.list_all()
            for client in clients:
                name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
                if name:
                    self.client_combo.addItem(name, client.get('id'))
        except Exception as e:
            print(f"Error loading clients: {e}")
    
    def _populate_doctors(self):
        """Populate doctor dropdown."""
        self.doctor_combo.clear()
        self.doctor_combo.addItem("", None)
        try:
            doctors = doctor_manager.list_all()
            for doctor in doctors:
                user_id = doctor.get('user_id')
                if user_id:
                    from database.local_cache import local_cache
                    user = local_cache.get('users', user_id)
                    if user:
                        name = user.get('username') or user.get('email', 'Unknown')
                        self.doctor_combo.addItem(name, doctor.get('id'))
                    else:
                        self.doctor_combo.addItem(f"Doctor {user_id}", doctor.get('id'))
        except Exception as e:
            print(f"Error loading doctors: {e}")
    
    def load_data(self):
        """Load prescription data into form."""
        if self.prescription_data:
            # Set client
            client_id = self.prescription_data.get('client_id')
            if client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == client_id:
                        self.client_combo.setCurrentIndex(i)
                        break
            
            # Set doctor
            doctor_id = self.prescription_data.get('doctor_id')
            if doctor_id:
                for i in range(self.doctor_combo.count()):
                    if self.doctor_combo.itemData(i) == doctor_id:
                        self.doctor_combo.setCurrentIndex(i)
                        break
            
            # Set prescription date
            date_str = self.prescription_data.get('prescription_date_utc')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    qdt = QDateTime(QDate(dt.year, dt.month, dt.day), QTime(dt.hour, dt.minute))
                    self.prescription_date_input.setDateTime(qdt)
                except:
                    pass
            
            # Set status
            status = self.prescription_data.get('status', 'active')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            # Set notes
            self.notes_input.setPlainText(self.prescription_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        client_id = self.client_combo.currentData()
        if not client_id:
            QMessageBox.warning(self, tr("common.error"), "Client is required")
            return
        
        doctor_id = self.doctor_combo.currentData()
        if not doctor_id:
            QMessageBox.warning(self, tr("common.error"), "Doctor is required")
            return
        
        # Build UTC datetime string
        qdt = self.prescription_date_input.dateTime()
        dt = datetime.combine(
            qdt.date().toPython(),
            qdt.time().toPython()
        )
        prescription_date_utc = dt.isoformat() + 'Z'
        
        # Parse items (simplified)
        items_text = self.items_input.text().strip()
        items = []
        if items_text:
            # Simple parsing - can be enhanced
            for line in items_text.split('\n'):
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        items.append({
                            'medication_name': parts[0].strip(),
                            'dosage': parts[1].strip() if len(parts) > 1 else '',
                            'frequency': parts[2].strip() if len(parts) > 2 else '',
                            'duration': parts[3].strip() if len(parts) > 3 else '',
                            'instructions': parts[4].strip() if len(parts) > 4 else ''
                        })
        
        data = {
            'client_id': client_id,
            'doctor_id': doctor_id,
            'prescription_date_utc': prescription_date_utc,
            'status': self.status_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip(),
            'items': items
        }
        
        try:
            if self.prescription_data:
                # Update
                success, error = prescription_manager.update(self.prescription_data['id'], data)
            else:
                # Create
                success, item_id, error = prescription_manager.create_prescription(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save prescription")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class PrescriptionsWidget(QWidget):
    """Prescriptions management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('client_id', 'Client'),
            ('doctor_id', 'Doctor'),
            ('prescription_date_utc', 'Date'),
            ('status', 'Status'),
        ]
        
        self.list_widget = BaseListWidget(
            "Prescriptions",
            prescription_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = PrescriptionDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, prescription_data: dict):
        """Handle edit."""
        dialog = PrescriptionDialog(prescription_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()
