"""Insurance management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QDateEdit,
                               QTextEdit, QHBoxLayout, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate
from ui.widgets.base_list_widget import BaseListWidget
from modules.insurance import insurance_manager
from modules.clients import client_manager
from database.local_cache import local_cache
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)


class InsuranceClaimDialog(QDialog):
    """Dialog for creating/editing insurance claims."""
    
    def __init__(self, claim_data=None, parent=None):
        super().__init__(parent)
        self.claim_data = claim_data
        self.setWindowTitle("Edit Insurance Claim" if claim_data else "Add Insurance Claim")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if claim_data:
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
        
        # Insurance company selection
        self.insurance_company_combo = QComboBox()
        self._populate_insurance_companies()
        self._apply_input_style(self.insurance_company_combo)
        form.addRow("Insurance Company", self.insurance_company_combo)
        
        # Submission date
        self.submission_date_input = QDateEdit()
        self.submission_date_input.setCalendarPopup(True)
        self.submission_date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.submission_date_input)
        form.addRow("Submission Date", self.submission_date_input)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimum(0.0)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$ ")
        self._apply_input_style(self.amount_input)
        form.addRow("Amount", self.amount_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['pending', 'submitted', 'approved', 'rejected', 'paid'])
        self._apply_input_style(self.status_combo)
        form.addRow("Status", self.status_combo)
        
        # Response date (optional)
        self.response_date_input = QDateEdit()
        self.response_date_input.setCalendarPopup(True)
        self.response_date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.response_date_input)
        form.addRow("Response Date (Optional)", self.response_date_input)
        
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
        for widget in [self.client_combo, self.insurance_company_combo, self.submission_date_input,
                      self.amount_input, self.status_combo, self.response_date_input,
                      self.notes_input]:
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
    
    def _populate_insurance_companies(self):
        """Populate insurance company dropdown."""
        self.insurance_company_combo.clear()
        self.insurance_company_combo.addItem("", None)
        try:
            companies = local_cache.query('insurance_companies', limit=100)
            for company in companies:
                name = company.get('company_name', 'Unknown')
                self.insurance_company_combo.addItem(name, company.get('id'))
        except Exception as e:
            print(f"Error loading insurance companies: {e}")
    
    def load_data(self):
        """Load insurance claim data into form."""
        if self.claim_data:
            # Set client
            client_id = self.claim_data.get('client_id')
            if client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == client_id:
                        self.client_combo.setCurrentIndex(i)
                        break
            
            # Set insurance company
            company_id = self.claim_data.get('insurance_company_id')
            if company_id:
                for i in range(self.insurance_company_combo.count()):
                    if self.insurance_company_combo.itemData(i) == company_id:
                        self.insurance_company_combo.setCurrentIndex(i)
                        break
            
            # Set submission date
            submission_date_str = self.claim_data.get('submission_date')
            if submission_date_str:
                try:
                    date = QDate.fromString(submission_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.submission_date_input.setDate(date)
                except:
                    pass
            
            # Set amount
            self.amount_input.setValue(self.claim_data.get('amount', 0.0))
            
            # Set status
            status = self.claim_data.get('status', 'pending')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            # Set response date
            response_date_str = self.claim_data.get('response_date')
            if response_date_str:
                try:
                    date = QDate.fromString(response_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.response_date_input.setDate(date)
                except:
                    pass
            
            # Set notes
            self.notes_input.setPlainText(self.claim_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        client_id = self.client_combo.currentData()
        if not client_id:
            QMessageBox.warning(self, tr("common.error"), "Client is required")
            return
        
        company_id = self.insurance_company_combo.currentData()
        if not company_id:
            QMessageBox.warning(self, tr("common.error"), "Insurance company is required")
            return
        
        data = {
            'client_id': client_id,
            'insurance_company_id': company_id,
            'submission_date': self.submission_date_input.date().toString(Qt.DateFormat.ISODate),
            'amount': self.amount_input.value(),
            'status': self.status_combo.currentText(),
            'response_date': self.response_date_input.date().toString(Qt.DateFormat.ISODate) if self.response_date_input.date().isValid() else None,
            'notes': self.notes_input.toPlainText().strip(),
            'created_by': user_id
        }
        
        try:
            if self.claim_data:
                # Update
                success, error = insurance_manager.update(self.claim_data['id'], data)
            else:
                # Create
                success, item_id, error = insurance_manager.create_claim(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save insurance claim")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class InsuranceWidget(QWidget):
    """Insurance management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('claim_number', 'Claim Number'),
            ('client_id', 'Client'),
            ('insurance_company_id', 'Insurance Company'),
            ('submission_date', 'Submission Date'),
            ('amount', 'Amount'),
            ('status', 'Status'),
        ]
        
        self.list_widget = BaseListWidget(
            "Insurance Claims",
            insurance_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = InsuranceClaimDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, claim_data: dict):
        """Handle edit."""
        dialog = InsuranceClaimDialog(claim_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()
