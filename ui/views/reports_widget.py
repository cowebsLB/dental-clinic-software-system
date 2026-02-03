"""Reports widget."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTabWidget, QDateEdit, QComboBox, QTextEdit, QScrollArea)
from PySide6.QtCore import Qt, QDate
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   apply_neumorphic_effect, get_neumorphic_card_style)
from modules.clients import client_manager
from modules.payments import payment_manager
from modules.reservations import reservation_manager
from modules.billing import billing_manager
from datetime import datetime, timedelta


class ReportsWidget(QWidget):
    """Reports widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        self.setStyleSheet("background: transparent;")
        
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        palette = theme_manager.get_palette()
        title_label = QLabel("Reports & Analytics")
        title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 300;
            color: {palette.text_primary};
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        # Tabs
        self.tabs = QTabWidget()
        self._apply_tab_style()
        
        # Financial Reports Tab
        financial_tab = self._create_financial_tab()
        self.tabs.addTab(financial_tab, "Financial Reports")
        
        # Appointment Statistics Tab
        appointments_tab = self._create_appointments_tab()
        self.tabs.addTab(appointments_tab, "Appointment Statistics")
        
        # Patient Reports Tab
        patients_tab = self._create_patients_tab()
        self.tabs.addTab(patients_tab, "Patient Reports")
        
        # Doctor Performance Tab
        doctors_tab = self._create_doctors_tab()
        self.tabs.addTab(doctors_tab, "Doctor Performance")
        
        layout.addWidget(self.tabs)
    
    def _apply_tab_style(self):
        """Apply neumorphic styling to tabs."""
        palette = theme_manager.get_palette()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {palette.base};
                border: 1px solid {palette.border};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background-color: {palette.surface};
                color: {palette.text_secondary};
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {palette.base};
                color: {palette.text_primary};
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._apply_tab_style()
    
    def _create_financial_tab(self):
        """Create financial reports tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Date range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        from_date = QDateEdit()
        from_date.setDate(QDate.currentDate().addMonths(-1))
        from_date.setCalendarPopup(True)
        from_date.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(from_date, inset=True, intensity=0.8)
        date_layout.addWidget(from_date)
        
        date_layout.addWidget(QLabel("To:"))
        to_date = QDateEdit()
        to_date.setDate(QDate.currentDate())
        to_date.setCalendarPopup(True)
        to_date.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(to_date, inset=True, intensity=0.8)
        date_layout.addWidget(to_date)
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.setStyleSheet(get_neumorphic_button_style())
        apply_neumorphic_effect(generate_btn, inset=False, intensity=1.0)
        generate_btn.clicked.connect(lambda: self._generate_financial_report(from_date.date(), to_date.date()))
        date_layout.addWidget(generate_btn)
        date_layout.addStretch()
        
        layout.addLayout(date_layout)
        
        # Report display
        self.financial_report = QTextEdit()
        self.financial_report.setReadOnly(True)
        self.financial_report.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(self.financial_report, inset=True, intensity=0.8)
        layout.addWidget(self.financial_report)
        
        return widget
    
    def _create_appointments_tab(self):
        """Create appointment statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.appointments_report = QTextEdit()
        self.appointments_report.setReadOnly(True)
        self.appointments_report.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(self.appointments_report, inset=True, intensity=0.8)
        layout.addWidget(self.appointments_report)
        
        # Generate initial report
        self._generate_appointments_report()
        
        return widget
    
    def _create_patients_tab(self):
        """Create patient reports tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.patients_report = QTextEdit()
        self.patients_report.setReadOnly(True)
        self.patients_report.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(self.patients_report, inset=True, intensity=0.8)
        layout.addWidget(self.patients_report)
        
        # Generate initial report
        self._generate_patients_report()
        
        return widget
    
    def _create_doctors_tab(self):
        """Create doctor performance tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.doctors_report = QTextEdit()
        self.doctors_report.setReadOnly(True)
        self.doctors_report.setStyleSheet(get_neumorphic_input_style())
        apply_neumorphic_effect(self.doctors_report, inset=True, intensity=0.8)
        layout.addWidget(self.doctors_report)
        
        # Generate initial report
        self._generate_doctors_report()
        
        return widget
    
    def _generate_financial_report(self, from_date, to_date):
        """Generate financial report."""
        try:
            # Get payments and invoices
            payments = payment_manager.list_all()
            invoices = billing_manager.list_all()
            
            total_revenue = sum(p.get('amount', 0) for p in payments if p.get('status') == 'completed')
            total_outstanding = sum(i.get('total', 0) for i in invoices if i.get('status') in ['pending', 'overdue'])
            
            report = f"""
Financial Report
Period: {from_date.toString(Qt.DateFormat.ISODate)} to {to_date.toString(Qt.DateFormat.ISODate)}

Total Revenue: ${total_revenue:,.2f}
Total Outstanding: ${total_outstanding:,.2f}

Payments: {len(payments)}
Invoices: {len(invoices)}
"""
            self.financial_report.setPlainText(report)
        except Exception as e:
            self.financial_report.setPlainText(f"Error generating report: {e}")
    
    def _generate_appointments_report(self):
        """Generate appointment statistics."""
        try:
            appointments = reservation_manager.list_all()
            total = len(appointments)
            scheduled = len([a for a in appointments if a.get('status') == 'scheduled'])
            completed = len([a for a in appointments if a.get('status') == 'completed'])
            cancelled = len([a for a in appointments if a.get('status') == 'cancelled'])
            
            report = f"""
Appointment Statistics

Total Appointments: {total}
Scheduled: {scheduled}
Completed: {completed}
Cancelled: {cancelled}
"""
            self.appointments_report.setPlainText(report)
        except Exception as e:
            self.appointments_report.setPlainText(f"Error generating report: {e}")
    
    def _generate_patients_report(self):
        """Generate patient reports."""
        try:
            clients = client_manager.list_all()
            total = len(clients)
            
            report = f"""
Patient Reports

Total Patients: {total}

Recent patients loaded from database.
"""
            self.patients_report.setPlainText(report)
        except Exception as e:
            self.patients_report.setPlainText(f"Error generating report: {e}")
    
    def _generate_doctors_report(self):
        """Generate doctor performance report."""
        try:
            from modules.doctors import doctor_manager
            doctors = doctor_manager.list_all()
            total = len(doctors)
            active = len([d for d in doctors if d.get('is_active', True)])
            
            report = f"""
Doctor Performance

Total Doctors: {total}
Active Doctors: {active}

Performance metrics can be expanded with appointment and treatment data.
"""
            self.doctors_report.setPlainText(report)
        except Exception as e:
            self.doctors_report.setPlainText(f"Error generating report: {e}")
