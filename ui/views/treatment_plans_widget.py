"""Treatment Plans management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QDoubleSpinBox,
                               QDateEdit, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Qt, QDate
from ui.widgets.base_list_widget import BaseListWidget
from modules.treatment_plans import treatment_plan_manager
from modules.clients import client_manager
from modules.doctors import doctor_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)


class TreatmentPlanDialog(QDialog):
    """Dialog for creating/editing treatment plans."""
    
    def __init__(self, plan_data=None, parent=None):
        super().__init__(parent)
        self.plan_data = plan_data
        self.setWindowTitle("Edit Treatment Plan" if plan_data else "Add Treatment Plan")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if plan_data:
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
        
        # Doctor selection (optional)
        self.doctor_combo = QComboBox()
        self.doctor_combo.addItem("", None)
        self._populate_doctors()
        self._apply_input_style(self.doctor_combo)
        form.addRow("Doctor (Optional)", self.doctor_combo)
        
        # Plan name
        self.plan_name_input = QLineEdit()
        self._apply_input_style(self.plan_name_input)
        form.addRow("Plan Name", self.plan_name_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['planned', 'in_progress', 'completed', 'cancelled'])
        self._apply_input_style(self.status_combo)
        form.addRow("Status", self.status_combo)
        
        # Total cost
        self.total_cost_input = QDoubleSpinBox()
        self.total_cost_input.setMinimum(0.0)
        self.total_cost_input.setMaximum(999999.99)
        self.total_cost_input.setDecimals(2)
        self.total_cost_input.setPrefix("$ ")
        self._apply_input_style(self.total_cost_input)
        form.addRow("Total Cost", self.total_cost_input)
        
        # Start date
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.start_date_input)
        form.addRow("Start Date", self.start_date_input)
        
        # Completion date (optional)
        self.completion_date_input = QDateEdit()
        self.completion_date_input.setCalendarPopup(True)
        self.completion_date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.completion_date_input)
        form.addRow("Completion Date (Optional)", self.completion_date_input)
        
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
        for widget in [self.client_combo, self.doctor_combo, self.plan_name_input,
                      self.status_combo, self.total_cost_input, self.start_date_input,
                      self.completion_date_input, self.notes_input]:
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
        """Load treatment plan data into form."""
        if self.plan_data:
            # Set client
            client_id = self.plan_data.get('client_id')
            if client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == client_id:
                        self.client_combo.setCurrentIndex(i)
                        break
            
            # Set doctor
            doctor_id = self.plan_data.get('doctor_id')
            if doctor_id:
                for i in range(self.doctor_combo.count()):
                    if self.doctor_combo.itemData(i) == doctor_id:
                        self.doctor_combo.setCurrentIndex(i)
                        break
            
            # Set plan name
            self.plan_name_input.setText(self.plan_data.get('plan_name', ''))
            
            # Set status
            status = self.plan_data.get('status', 'planned')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            # Set total cost
            self.total_cost_input.setValue(self.plan_data.get('total_cost', 0.0))
            
            # Set start date
            start_date_str = self.plan_data.get('start_date')
            if start_date_str:
                try:
                    date = QDate.fromString(start_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.start_date_input.setDate(date)
                except:
                    pass
            
            # Set completion date
            completion_date_str = self.plan_data.get('completion_date')
            if completion_date_str:
                try:
                    date = QDate.fromString(completion_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.completion_date_input.setDate(date)
                except:
                    pass
            
            # Set notes
            self.notes_input.setPlainText(self.plan_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        client_id = self.client_combo.currentData()
        if not client_id:
            QMessageBox.warning(self, tr("common.error"), "Client is required")
            return
        
        data = {
            'client_id': client_id,
            'doctor_id': self.doctor_combo.currentData(),
            'plan_name': self.plan_name_input.text().strip(),
            'status': self.status_combo.currentText(),
            'total_cost': self.total_cost_input.value(),
            'start_date': self.start_date_input.date().toString(Qt.DateFormat.ISODate),
            'completion_date': self.completion_date_input.date().toString(Qt.DateFormat.ISODate) if self.completion_date_input.date().isValid() else None,
            'notes': self.notes_input.toPlainText().strip(),
            'created_by': user_id,
            'last_modified_by': user_id
        }
        
        if not data['plan_name']:
            QMessageBox.warning(self, tr("common.error"), "Plan name is required")
            return
        
        try:
            if self.plan_data:
                # Update
                success, error = treatment_plan_manager.update(self.plan_data['id'], data)
            else:
                # Create
                success, item_id, error = treatment_plan_manager.create_treatment_plan(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save treatment plan")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class TreatmentPlansWidget(QWidget):
    """Treatment Plans management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('client_id', 'Client'),
            ('plan_name', 'Plan Name'),
            ('status', 'Status'),
            ('total_cost', 'Total Cost'),
        ]
        
        self.list_widget = BaseListWidget(
            "Treatment Plans",
            treatment_plan_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = TreatmentPlanDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, plan_data: dict):
        """Handle edit."""
        dialog = TreatmentPlanDialog(plan_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

