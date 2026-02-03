"""Billing management widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QFormLayout, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QDateEdit,
                               QTextEdit, QHBoxLayout, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate
from ui.widgets.base_list_widget import BaseListWidget
from modules.billing import billing_manager
from modules.clients import client_manager
from modules.treatment_plans import treatment_plan_manager
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect)


class InvoiceDialog(QDialog):
    """Dialog for creating/editing invoices."""
    
    def __init__(self, invoice_data=None, parent=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.setWindowTitle("Edit Invoice" if invoice_data else "Add Invoice")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setup_ui()
        
        if invoice_data:
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
        
        # Treatment plan (optional)
        self.treatment_plan_combo = QComboBox()
        self.treatment_plan_combo.addItem("", None)
        self._populate_treatment_plans()
        self._apply_input_style(self.treatment_plan_combo)
        form.addRow("Treatment Plan (Optional)", self.treatment_plan_combo)
        
        # Issue date
        self.issue_date_input = QDateEdit()
        self.issue_date_input.setCalendarPopup(True)
        self.issue_date_input.setDate(QDate.currentDate())
        self._apply_input_style(self.issue_date_input)
        form.addRow("Issue Date", self.issue_date_input)
        
        # Due date
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate().addDays(30))
        self._apply_input_style(self.due_date_input)
        form.addRow("Due Date", self.due_date_input)
        
        # Tax rate
        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setMinimum(0.0)
        self.tax_rate_input.setMaximum(100.0)
        self.tax_rate_input.setDecimals(2)
        self.tax_rate_input.setSuffix(" %")
        self.tax_rate_input.setValue(0.0)
        self._apply_input_style(self.tax_rate_input)
        form.addRow("Tax Rate", self.tax_rate_input)
        
        # Discount
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0.0)
        self.discount_input.setMaximum(999999.99)
        self.discount_input.setDecimals(2)
        self.discount_input.setPrefix("$ ")
        self.discount_input.setValue(0.0)
        self._apply_input_style(self.discount_input)
        form.addRow("Discount", self.discount_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['pending', 'paid', 'overdue', 'cancelled'])
        self._apply_input_style(self.status_combo)
        form.addRow("Status", self.status_combo)
        
        # Items (simplified - single line for now)
        self.items_input = QTextEdit()
        self.items_input.setPlaceholderText("Invoice items (one per line: Description, Quantity, Unit Price)")
        self.items_input.setMaximumHeight(100)
        self._apply_input_style(self.items_input)
        form.addRow("Items", self.items_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
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
        for widget in [self.client_combo, self.treatment_plan_combo, self.issue_date_input,
                      self.due_date_input, self.tax_rate_input, self.discount_input,
                      self.status_combo, self.items_input, self.notes_input]:
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
    
    def _populate_treatment_plans(self):
        """Populate treatment plan dropdown."""
        try:
            plans = treatment_plan_manager.list_all()
            for plan in plans:
                plan_name = plan.get('plan_name', 'Unknown')
                self.treatment_plan_combo.addItem(plan_name, plan.get('id'))
        except Exception as e:
            print(f"Error loading treatment plans: {e}")
    
    def load_data(self):
        """Load invoice data into form."""
        if self.invoice_data:
            # Set client
            client_id = self.invoice_data.get('client_id')
            if client_id:
                for i in range(self.client_combo.count()):
                    if self.client_combo.itemData(i) == client_id:
                        self.client_combo.setCurrentIndex(i)
                        break
            
            # Set treatment plan
            plan_id = self.invoice_data.get('treatment_plan_id')
            if plan_id:
                for i in range(self.treatment_plan_combo.count()):
                    if self.treatment_plan_combo.itemData(i) == plan_id:
                        self.treatment_plan_combo.setCurrentIndex(i)
                        break
            
            # Set dates
            issue_date_str = self.invoice_data.get('issue_date')
            if issue_date_str:
                try:
                    date = QDate.fromString(issue_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.issue_date_input.setDate(date)
                except:
                    pass
            
            due_date_str = self.invoice_data.get('due_date')
            if due_date_str:
                try:
                    date = QDate.fromString(due_date_str, Qt.DateFormat.ISODate)
                    if date.isValid():
                        self.due_date_input.setDate(date)
                except:
                    pass
            
            # Set tax rate and discount
            self.tax_rate_input.setValue(self.invoice_data.get('tax_rate', 0.0))
            self.discount_input.setValue(self.invoice_data.get('discount', 0.0))
            
            # Set status
            status = self.invoice_data.get('status', 'pending')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
            # Set notes
            self.notes_input.setPlainText(self.invoice_data.get('notes', ''))
    
    def on_save(self):
        """Handle save."""
        user = auth_manager.get_current_user()
        user_id = user.get('id', '') if user else ''
        
        client_id = self.client_combo.currentData()
        if not client_id:
            QMessageBox.warning(self, tr("common.error"), "Client is required")
            return
        
        # Parse items (simplified)
        items_text = self.items_input.toPlainText().strip()
        items = []
        if items_text:
            for line in items_text.split('\n'):
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            quantity = float(parts[1].strip())
                            unit_price = float(parts[2].strip())
                            items.append({
                                'description': parts[0].strip(),
                                'quantity': quantity,
                                'unit_price': unit_price,
                                'total': quantity * unit_price
                            })
                        except:
                            pass
        
        data = {
            'client_id': client_id,
            'treatment_plan_id': self.treatment_plan_combo.currentData(),
            'issue_date': self.issue_date_input.date().toString(Qt.DateFormat.ISODate),
            'due_date': self.due_date_input.date().toString(Qt.DateFormat.ISODate),
            'tax_rate': self.tax_rate_input.value(),
            'discount': self.discount_input.value(),
            'status': self.status_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip(),
            'items': items,
            'created_by': user_id
        }
        
        try:
            if self.invoice_data:
                # Update
                success, error = billing_manager.update(self.invoice_data['id'], data)
            else:
                # Create
                success, item_id, error = billing_manager.create_invoice(data)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, tr("common.error"), error or "Failed to save invoice")
        except Exception as e:
            QMessageBox.warning(self, tr("common.error"), f"Error: {e}")


class BillingWidget(QWidget):
    """Billing management widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        columns = [
            ('invoice_number', 'Invoice Number'),
            ('client_id', 'Client'),
            ('issue_date', 'Issue Date'),
            ('total', 'Total'),
            ('status', 'Status'),
        ]
        
        self.list_widget = BaseListWidget(
            "Billing & Invoicing",
            billing_manager,
            columns,
            self
        )
        self.list_widget.add_requested.connect(self.on_add)
        self.list_widget.edit_requested.connect(self.on_edit)
        
        layout.addWidget(self.list_widget)
    
    def on_add(self):
        """Handle add."""
        dialog = InvoiceDialog(parent=self)
        if dialog.exec():
            self.list_widget.refresh()
    
    def on_edit(self, invoice_data: dict):
        """Handle edit."""
        dialog = InvoiceDialog(invoice_data, parent=self)
        if dialog.exec():
            self.list_widget.refresh()
