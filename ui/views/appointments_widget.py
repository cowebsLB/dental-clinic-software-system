"""Appointments/Reservations management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit, 
                               QTextEdit, QPushButton, QMessageBox, QComboBox, QDateTimeEdit,
                               QHBoxLayout, QDateEdit, QTimeEdit)
from PySide6.QtCore import Qt, QDateTime, QDate, QTime
from ui.widgets.base_list_widget import BaseListWidget
from modules.reservations import reservation_manager
from modules.clients import client_manager
from modules.doctors import doctor_manager
from modules.rooms import room_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)
from datetime import datetime


class AppointmentDialog(QDialog):
    """Dialog for creating/editing appointments."""
    
    def __init__(self, appointment_data=None, parent=None):
        super().__init__(parent)
        self.appointment_data = appointment_data
        self.setWindowTitle(tr("appointments.edit_appointment") if appointment_data else tr("appointments.add_appointment"))
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setup_ui()
        
        if appointment_data:
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
        form.addRow(tr("appointments.client"), self.client_combo)
        
        # Doctor selection
        self.doctor_combo = QComboBox()
        self._populate_doctors()
        self._apply_input_style(self.doctor_combo)
        form.addRow(tr("appointments.doctor"), self.doctor_combo)
        
        # Room selection
        self.room_combo = QComboBox()
        self._populate_rooms()
        self._apply_input_style(self.room_combo)
        form.addRow(tr("appointments.room"), self.room_combo)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.date_input)
        form.addRow(tr("appointments.date"), self.date_input)
        
        # Start time
        self.start_time_input = QTimeEdit()
        self.start_time_input.setTime(QTime.currentTime())
        self._apply_input_style(self.start_time_input)
        form.addRow(tr("appointments.start_time"), self.start_time_input)
        
        # End time
        self.end_time_input = QTimeEdit()
        self.end_time_input.setTime(QTime.currentTime().addSecs(3600))  # Default 1 hour later
        self._apply_input_style(self.end_time_input)
        form.addRow(tr("appointments.end_time"), self.end_time_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'])
        self._apply_input_style(self.status_combo)
        form.addRow(tr("appointments.status"), self.status_combo)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self._apply_input_style(self.notes_input)
        form.addRow(tr("appointments.notes"), self.notes_input)
        
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
        for widget in [self.client_combo, self.doctor_combo, self.room_combo, 
                      self.date_input, self.start_time_input, self.end_time_input,
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
                # Get user info if available
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
        """Load appointment data into form."""
        if self.appointment_data:
            # Set client
            client_id = self.appointment_data.get('client_id')
            if client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == client_id:
                        self.client_combo.setCurrentIndex(i)
                        break
            
            # Set doctor
            doctor_id = self.appointment_data.get('doctor_id')
            if doctor_id:
                for i in range(self.doctor_combo.count()):
                    if self.doctor_combo.itemData(i) == doctor_id:
                        self.doctor_combo.setCurrentIndex(i)
                        break
            
            # Set room
            room_id = self.appointment_data.get('room_id')
            if room_id:
                for i in range(self.room_combo.count()):
                    if self.room_combo.itemData(i) == room_id:
                        self.room_combo.setCurrentIndex(i)
                        break
            
            # Set date
            date_str = self.appointment_data.get('reservation_date')
            if date_str:
                try:
                    date = QDate.fromString(date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.date_input.setDate(date)
                except:
                    pass
            
            # Set start time
            start_time_str = self.appointment_data.get('start_time_utc')
            if start_time_str:
                try:
                    dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    time = QTime(dt.hour, dt.minute)
                    self.start_time_input.setTime(time)
                except:
                    pass
            
            # Set end time
            end_time_str = self.appointment_data.get('end_time_utc')
            if end_time_str:
                try:
                    dt = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    time = QTime(dt.hour, dt.minute)
                    self.end_time_input.setTime(time)
                except:
                    pass
            
            # Set status
            status = self.appointment_data.get('status', 'scheduled')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            # Set notes
            self.notes_input.setPlainText(self.appointment_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        # Get selected IDs
        client_id = self.client_combo.currentData()
        doctor_id = self.doctor_combo.currentData()
        room_id = self.room_combo.currentData()
        
        if not client_id:
            QMessageBox.warning(self, tr("common.error"), "Client is required")
            return
        
        # Build date/time strings
        date = self.date_input.date().toString(Qt.DateFormat.ISODate)
        start_time = self.start_time_input.time()
        end_time = self.end_time_input.time()
        
        # Combine date and time for UTC strings
        start_dt = datetime.combine(
            self.date_input.date().toPython(),
            start_time.toPython()
        )
        end_dt = datetime.combine(
            self.date_input.date().toPython(),
            end_time.toPython()
        )
        
        start_time_utc = start_dt.isoformat() + 'Z'
        end_time_utc = end_dt.isoformat() + 'Z'
        
        data = {
            'client_id': client_id,
            'doctor_id': doctor_id,
            'room_id': room_id,
            'reservation_date': date,
            'start_time_utc': start_time_utc,
            'end_time_utc': end_time_utc,
            'status': self.status_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip(),
            'created_by': user_id,
            'last_modified_by': user_id
        }
        
        try:
            if self.appointment_data:
                # Update
                success, error = reservation_manager.update(self.appointment_data['id'], data)
            else:
                # Create
                success, item_id, error = reservation_manager.create(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save appointment")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class AppointmentsWidget(QWidget):
    """Appointments management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('reservation_date', 'Date'),
            ('start_time_utc', 'Start Time'),
            ('end_time_utc', 'End Time'),
            ('client_id', 'Client'),
            ('doctor_id', 'Doctor'),
            ('room_id', 'Room'),
            ('status', 'Status'),
        ]
        
        self.list_widget = BaseListWidget(
            tr("appointments.title"),
            reservation_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = AppointmentDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, appointment_data: dict):
        """Handle edit."""
        dialog = AppointmentDialog(appointment_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

