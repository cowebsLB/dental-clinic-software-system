"""Medical Records management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QDateTimeEdit,
                               QTextEdit, QHBoxLayout)
from PySide6.QtCore import Qt, QDateTime, QDate, QTime
from ui.widgets.base_list_widget import BaseListWidget
from modules.medical_records import medical_records_manager
from modules.clients import client_manager
from modules.doctors import doctor_manager
from modules.reservations import reservation_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)
from datetime import datetime


class ClinicalNoteDialog(QDialog):
    """Dialog for creating/editing clinical notes."""
    
    def __init__(self, note_data=None, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.setWindowTitle("Edit Clinical Note" if note_data else "Add Clinical Note")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setup_ui()
        
        if note_data:
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
        
        # Reservation selection (optional)
        self.reservation_combo = QComboBox()
        self.reservation_combo.addItem("", None)
        self._apply_input_style(self.reservation_combo)
        form.addRow("Reservation (Optional)", self.reservation_combo)
        
        # Doctor selection
        self.doctor_combo = QComboBox()
        self._populate_doctors()
        self._apply_input_style(self.doctor_combo)
        form.addRow("Doctor", self.doctor_combo)
        
        # Visit date
        self.visit_date_input = QDateTimeEdit()
        self.visit_date_input.setCalendarPopup(True)
        self.visit_date_input.setDateTime(QDateTime.currentDateTime())
        self._apply_input_style(self.visit_date_input)
        form.addRow("Visit Date", self.visit_date_input)
        
        # Chief complaint
        self.chief_complaint_input = QTextEdit()
        self.chief_complaint_input.setMaximumHeight(80)
        self._apply_input_style(self.chief_complaint_input)
        form.addRow("Chief Complaint", self.chief_complaint_input)
        
        # Examination
        self.examination_input = QTextEdit()
        self.examination_input.setMaximumHeight(100)
        self._apply_input_style(self.examination_input)
        form.addRow("Examination", self.examination_input)
        
        # Diagnosis
        self.diagnosis_input = QTextEdit()
        self.diagnosis_input.setMaximumHeight(100)
        self._apply_input_style(self.diagnosis_input)
        form.addRow("Diagnosis", self.diagnosis_input)
        
        # Treatment rendered
        self.treatment_rendered_input = QTextEdit()
        self.treatment_rendered_input.setMaximumHeight(100)
        self._apply_input_style(self.treatment_rendered_input)
        form.addRow("Treatment Rendered", self.treatment_rendered_input)
        
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
        for widget in [self.client_combo, self.reservation_combo, self.doctor_combo,
                      self.visit_date_input, self.chief_complaint_input, self.examination_input,
                      self.diagnosis_input, self.treatment_rendered_input, self.notes_input]:
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
    
    def _populate_reservations(self, client_id=None):
        """Populate reservation dropdown for a client."""
        self.reservation_combo.clear()
        self.reservation_combo.addItem("", None)
        if client_id:
            try:
                reservations = reservation_manager.list_all()
                for reservation in reservations:
                    if reservation.get('client_id') == client_id:
                        date_str = reservation.get('reservation_date', 'Unknown')
                        self.reservation_combo.addItem(date_str, reservation.get('id'))
            except Exception as e:
                print(f"Error loading reservations: {e}")
    
    def load_data(self):
        """Load clinical note data into form."""
        if self.note_data:
            # Set client
            client_id = self.note_data.get('client_id')
            if client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == client_id:
                        self.client_combo.setCurrentIndex(i)
                        self._populate_reservations(client_id)
                        break
            
            # Set reservation
            reservation_id = self.note_data.get('reservation_id')
            if reservation_id:
                for i in range(self.reservation_combo.count()):
                    if self.reservation_combo.itemData(i) == reservation_id:
                        self.reservation_combo.setCurrentIndex(i)
                        break
            
            # Set doctor
            doctor_id = self.note_data.get('doctor_id')
            if doctor_id:
                for i in range(self.doctor_combo.count()):
                    if self.doctor_combo.itemData(i) == doctor_id:
                        self.doctor_combo.setCurrentIndex(i)
                        break
            
            # Set visit date
            visit_date_str = self.note_data.get('visit_date_utc')
            if visit_date_str:
                try:
                    dt = datetime.fromisoformat(visit_date_str.replace('Z', '+00:00'))
                    qdt = QDateTime(QDate(dt.year, dt.month, dt.day), QTime(dt.hour, dt.minute))
                    self.visit_date_input.setDateTime(qdt)
                except:
                    pass
            
            # Set text fields
            self.chief_complaint_input.setPlainText(self.note_data.get('chief_complaint', ''))
            self.examination_input.setPlainText(self.note_data.get('examination', ''))
            self.diagnosis_input.setPlainText(self.note_data.get('diagnosis', ''))
            self.treatment_rendered_input.setPlainText(self.note_data.get('treatment_rendered', ''))
            self.notes_input.setPlainText(self.note_data.get('notes', ''))
    
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
        qdt = self.visit_date_input.dateTime()
        dt = datetime.combine(
            qdt.date().toPython(),
            qdt.time().toPython()
        )
        visit_date_utc = dt.isoformat() + 'Z'
        
        data = {
            'client_id': client_id,
            'reservation_id': self.reservation_combo.currentData(),
            'doctor_id': doctor_id,
            'visit_date_utc': visit_date_utc,
            'chief_complaint': self.chief_complaint_input.toPlainText().strip(),
            'examination': self.examination_input.toPlainText().strip(),
            'diagnosis': self.diagnosis_input.toPlainText().strip(),
            'treatment_rendered': self.treatment_rendered_input.toPlainText().strip(),
            'notes': self.notes_input.toPlainText().strip()
        }
        
        try:
            if self.note_data:
                # Update
                success, error = medical_records_manager.update(self.note_data['id'], data)
            else:
                # Create
                success, item_id, error = medical_records_manager.create_clinical_note(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save clinical note")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class MedicalRecordsWidget(QWidget):
    """Medical Records management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('client_id', 'Client'),
            ('visit_date_utc', 'Visit Date'),
            ('doctor_id', 'Doctor'),
            ('chief_complaint', 'Chief Complaint'),
            ('diagnosis', 'Diagnosis'),
        ]
        
        self.list_widget = BaseListWidget(
            "Medical Records",
            medical_records_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = ClinicalNoteDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, note_data: dict):
        """Handle edit."""
        dialog = ClinicalNoteDialog(note_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

