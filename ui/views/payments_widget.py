"""Payments management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QDoubleSpinBox,
                               QDateTimeEdit, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Qt, QDateTime, QDate, QTime
from ui.widgets.base_list_widget import BaseListWidget
from modules.payments import payment_manager
from modules.clients import client_manager
from modules.billing import billing_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)
from datetime import datetime


class PaymentDialog(QDialog):
    """Dialog for creating/editing payments."""
    
    def __init__(self, payment_data=None, parent=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.setWindowTitle("Edit Payment" if payment_data else "Add Payment")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if payment_data:
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
        
        # Invoice selection (optional)
        self.invoice_combo = QComboBox()
        self.invoice_combo.addItem("", None)
        self._apply_input_style(self.invoice_combo)
        form.addRow("Invoice (Optional)", self.invoice_combo)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimum(0.0)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$ ")
        self._apply_input_style(self.amount_input)
        form.addRow("Amount", self.amount_input)
        
        # Payment method
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(['cash', 'credit_card', 'debit_card', 'check', 'bank_transfer', 'other'])
        self._apply_input_style(self.payment_method_combo)
        form.addRow("Payment Method", self.payment_method_combo)
        
        # Payment date
        self.payment_date_input = QDateTimeEdit()
        self.payment_date_input.setCalendarPopup(True)
        self.payment_date_input.setDateTime(QDateTime.currentDateTime())
        self._apply_input_style(self.payment_date_input)
        form.addRow("Payment Date", self.payment_date_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['pending', 'completed', 'failed', 'refunded'])
        self._apply_input_style(self.status_combo)
        form.addRow("Status", self.status_combo)
        
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
        for widget in [self.client_combo, self.invoice_combo, self.amount_input,
                      self.payment_method_combo, self.payment_date_input, self.status_combo,
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
    
    def _populate_invoices(self, client_id=None):
        """Populate invoice dropdown for a client."""
        self.invoice_combo.clear()
        self.invoice_combo.addItem("", None)
        if client_id:
            try:
                invoices = billing_manager.list_all()
                for invoice in invoices:
                    if invoice.get('client_id') == client_id:
                        invoice_num = invoice.get('invoice_number', 'Unknown')
                        self.invoice_combo.addItem(invoice_num, invoice.get('id'))
            except Exception as e:
                print(f"Error loading invoices: {e}")
    
    def load_data(self):
        """Load payment data into form."""
        if self.payment_data:
            # Set client
            client_id = self.payment_data.get('client_id')
            if client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == client_id:
                        self.client_combo.setCurrentIndex(i)
                        self._populate_invoices(client_id)
                        break
            
            # Set invoice
            invoice_id = self.payment_data.get('invoice_id') or self.payment_data.get('reservation_id')
            if invoice_id:
                for i in range(self.invoice_combo.count()):
                    if self.invoice_combo.itemData(i) == invoice_id:
                        self.invoice_combo.setCurrentIndex(i)
                        break
            
            # Set amount
            self.amount_input.setValue(self.payment_data.get('amount', 0.0))
            
            # Set payment method
            method = self.payment_data.get('payment_method', 'cash')
            index = self.payment_method_combo.findText(method)
            if index >= 0:
                self.payment_method_combo.setCurrentIndex(index)
            
            # Set payment date
            payment_date_str = self.payment_data.get('payment_date_utc')
            if payment_date_str:
                try:
                    dt = datetime.fromisoformat(payment_date_str.replace('Z', '+00:00'))
                    qdt = QDateTime(QDate(dt.year, dt.month, dt.day), QTime(dt.hour, dt.minute))
                    self.payment_date_input.setDateTime(qdt)
                except:
                    pass
            
            # Set status
            status = self.payment_data.get('status', 'pending')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            # Set notes
            self.notes_input.setPlainText(self.payment_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        client_id = self.client_combo.currentData()
        if not client_id:
            QMessageBox.warning(self, tr("common.error"), "Client is required")
            return
        
        # Build UTC datetime string
        qdt = self.payment_date_input.dateTime()
        dt = datetime.combine(
            qdt.date().toPython(),
            qdt.time().toPython()
        )
        payment_date_utc = dt.isoformat() + 'Z'
        
        data = {
            'client_id': client_id,
            'reservation_id': self.invoice_combo.currentData(),  # Using reservation_id field for invoice_id
            'amount': self.amount_input.value(),
            'payment_method': self.payment_method_combo.currentText(),
            'payment_date_utc': payment_date_utc,
            'status': self.status_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip(),
            'processed_by': user_id,
            'last_modified_by': user_id
        }
        
        try:
            if self.payment_data:
                # Update
                success, error = payment_manager.update(self.payment_data['id'], data)
            else:
                # Create
                success, item_id, error = payment_manager.create(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save payment")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class PaymentsWidget(QWidget):
    """Payments management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('client_id', 'Client'),
            ('amount', 'Amount'),
            ('payment_method', 'Method'),
            ('payment_date_utc', 'Date'),
            ('status', 'Status'),
        ]
        
        self.list_widget = BaseListWidget(
            "Payments",
            payment_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = PaymentDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, payment_data: dict):
        """Handle edit."""
        dialog = PaymentDialog(payment_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()

