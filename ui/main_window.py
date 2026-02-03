"""Main application window."""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QMenuBar, QStatusBar, QMenu, QStackedWidget, QDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from auth.auth_manager import auth_manager
from ui.login_dialog import LoginDialog
from ui.components.sync_status import SyncStatusWidget
from ui.components.sidebar import Sidebar
from ui.dashboard.dashboard_widget import DashboardWidget
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import get_neumorphic_card_style
from ui.dialogs.settings_dialog import SettingsDialog

# #region agent log
import json
DEBUG_LOG_PATH = r"c:\Users\COWebs.lb\Desktop\my files\01-Projects\dental clinic software system\.cursor\debug.log"
def _debug_log(location, message, data=None, hypothesis_id=None):
    try:
        with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
            log_entry = {
                "location": location,
                "message": message,
                "data": data or {},
                "timestamp": __import__('time').time() * 1000,
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": hypothesis_id
            }
            f.write(json.dumps(log_entry) + '\n')
    except: pass
# #endregion
from ui.views.clients_widget import ClientsWidget
from ui.views.appointments_widget import AppointmentsWidget
from ui.views.staff_widget import StaffWidget
from ui.views.doctors_widget import DoctorsWidget
from ui.views.rooms_widget import RoomsWidget
from ui.views.equipment_widget import EquipmentWidget
from ui.views.payments_widget import PaymentsWidget
from ui.views.treatment_plans_widget import TreatmentPlansWidget
from ui.views.medical_records_widget import MedicalRecordsWidget
from ui.views.prescriptions_widget import PrescriptionsWidget
from ui.views.billing_widget import BillingWidget
from ui.views.insurance_widget import InsuranceWidget
from ui.views.reports_widget import ReportsWidget
from ui.widgets.calendar_widget import CalendarWidget
from config.i18n import tr

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        # #region agent log
        _debug_log("main_window.py:34", "MainWindow.__init__ entry", {}, "H2,H3")
        # #endregion
        super().__init__()
        # #region agent log
        _debug_log("main_window.py:37", "After super().__init__", {}, "H3")
        # #endregion
        self.setWindowTitle(tr("app.title"))
        self.setMinimumSize(1200, 800)
        
        # Initialize widgets dictionary
        self.widgets = {}
        
        # Connect to theme changes
        # #region agent log
        _debug_log("main_window.py:45", "Before theme_manager connection", {"theme_manager_exists": theme_manager is not None}, "H5")
        # #endregion
        theme_manager.theme_changed.connect(self._on_theme_changed)
        # #region agent log
        _debug_log("main_window.py:47", "After theme_manager connection", {}, "H5")
        # #endregion
        
        # Apply neumorphic theme
        # #region agent log
        _debug_log("main_window.py:50", "Before _apply_theme", {}, "H4")
        # #endregion
        self._apply_theme()
        # #region agent log
        _debug_log("main_window.py:52", "After _apply_theme", {}, "H4")
        # #endregion
        
        # Check authentication
        if not auth_manager.is_authenticated():
            # #region agent log
            _debug_log("main_window.py:55", "Not authenticated, showing login", {}, "H3")
            # #endregion
            self.show_login()
            if not auth_manager.is_authenticated():
                # #region agent log
                _debug_log("main_window.py:58", "Login cancelled", {}, "H3")
                # #endregion
                return  # User cancelled login
        
        # #region agent log
        _debug_log("main_window.py:61", "Before setup_ui", {}, "H3")
        # #endregion
        self.setup_ui()
        # #region agent log
        _debug_log("main_window.py:63", "After setup_ui", {}, "H3")
        # #endregion
        self.setup_menu()
        self.setup_status_bar()
        # #region agent log
        _debug_log("main_window.py:66", "MainWindow.__init__ complete", {}, "H2,H3")
        # #endregion
    
    def _apply_theme(self):
        """Apply neumorphic theme to main window."""
        # #region agent log
        _debug_log("main_window.py:69", "_apply_theme entry", {}, "H4")
        # #endregion
        try:
            palette = theme_manager.get_palette()
            # #region agent log
            _debug_log("main_window.py:72", "Got palette", {"background": palette.background}, "H4")
            # #endregion
            stylesheet = f"""
            QMainWindow {{
                background-color: {palette.background};
            }}
        """
            # #region agent log
            _debug_log("main_window.py:79", "Before setStyleSheet", {"stylesheet_length": len(stylesheet)}, "H4")
            # #endregion
            self.setStyleSheet(stylesheet)
            # #region agent log
            _debug_log("main_window.py:81", "After setStyleSheet", {}, "H4")
            # #endregion
        except Exception as e:
            # #region agent log
            _debug_log("main_window.py:83", "Exception in _apply_theme", {"error": str(e), "type": type(e).__name__}, "H4")
            # #endregion
            raise
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._apply_theme()
        # Update menu and status bar
        self.setup_menu()
        self.setup_status_bar()
    
    def setup_ui(self):
        """Setup main UI."""
        # #region agent log
        _debug_log("main_window.py:88", "setup_ui entry", {}, "H3")
        # #endregion
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # #region agent log
        _debug_log("main_window.py:91", "Central widget set", {}, "H3")
        # #endregion
        
        # Main horizontal layout: sidebar + content
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        # #region agent log
        _debug_log("main_window.py:162", "Before Sidebar creation", {}, "H3")
        # #endregion
        try:
            self.sidebar = Sidebar()
            # #region agent log
            _debug_log("main_window.py:166", "Sidebar created successfully", {}, "H3")
            # #endregion
        except Exception as e:
            # #region agent log
            _debug_log("main_window.py:169", "Exception creating Sidebar", {"error": str(e), "type": type(e).__name__, "traceback": __import__('traceback').format_exc()}, "H3")
            # #endregion
            raise
        self.sidebar.item_selected.connect(self.on_navigation_item_selected)
        main_layout.addWidget(self.sidebar)
        
        # Content area with neumorphic background
        content_widget = QWidget()
        palette = theme_manager.get_palette()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.background};
            }}
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # Add dashboard widget (always loaded) - check if already exists
        # #region agent log
        _debug_log("main_window.py:115", "Before dashboard widget creation", {"dashboard_exists": 'dashboard' in self.widgets}, "H3")
        # #endregion
        try:
            if 'dashboard' not in self.widgets:
                # #region agent log
                _debug_log("main_window.py:118", "Creating DashboardWidget", {}, "H3")
                # #endregion
                self.dashboard_widget = DashboardWidget()
                # #region agent log
                _debug_log("main_window.py:121", "DashboardWidget created", {"widget_exists": self.dashboard_widget is not None}, "H3")
                # #endregion
                self.stacked_widget.addWidget(self.dashboard_widget)
                self.widgets['dashboard'] = self.dashboard_widget
            else:
                self.dashboard_widget = self.widgets['dashboard']
            
            # Show dashboard by default
            # #region agent log
            _debug_log("main_window.py:130", "Before setCurrentWidget", {}, "H3")
            # #endregion
            self.stacked_widget.setCurrentWidget(self.dashboard_widget)
            # #region agent log
            _debug_log("main_window.py:132", "After setCurrentWidget", {}, "H3")
            # #endregion
        except Exception as e:
            # #region agent log
            _debug_log("main_window.py:135", "Exception in dashboard setup", {"error": str(e), "type": type(e).__name__, "traceback": __import__('traceback').format_exc()}, "H3")
            # #endregion
            raise
        # #region agent log
        _debug_log("main_window.py:138", "setup_ui complete", {}, "H3")
        # #endregion
    
    def get_or_create_widget(self, widget_id: str, widget_class):
        """Get existing widget or create new one."""
        # Check if widget still exists and is valid
        if widget_id in self.widgets:
            widget = self.widgets[widget_id]
            # Check if widget is still valid (not deleted)
            try:
                # Try to access a property to see if widget is still valid
                _ = widget.isVisible()
                # Check if it's still in the stacked widget
                if self.stacked_widget.indexOf(widget) == -1:
                    self.stacked_widget.addWidget(widget)
                return widget
            except RuntimeError:
                # Widget was deleted, remove from dict and recreate
                del self.widgets[widget_id]
        
        # Create new widget
        widget = widget_class(parent=self)
        self.widgets[widget_id] = widget
        self.stacked_widget.addWidget(widget)
        return widget
    
    def setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # Clear existing menus to prevent duplication
        menubar.clear()
        
        # Apply neumorphic styling to menu bar
        palette = theme_manager.get_palette()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border-bottom: 1px solid {palette.border};
                padding: 6px;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QMenuBar::item:selected {{
                background-color: {palette.base};
            }}
            QMenu {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 12px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 10px 32px 10px 16px;
                border-radius: 8px;
            }}
            QMenu::item:selected {{
                background-color: {palette.base};
            }}
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.on_logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(self.show_dashboard)
        view_menu.addAction(dashboard_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Apply neumorphic styling
        palette = theme_manager.get_palette()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border-top: 1px solid {palette.border};
                padding: 4px;
            }}
        """)
        
        # Sync status widget
        sync_status = SyncStatusWidget()
        sync_status.sync_requested.connect(self.on_sync_requested)
        status_bar.addPermanentWidget(sync_status)
        
        # User info
        user = auth_manager.get_current_user()
        if user:
            username = user.get('username') or user.get('email', 'User')
            status_bar.showMessage(f"Logged in as {username}")
    
    def show_login(self):
        """Show login dialog."""
        # #region agent log
        _debug_log("main_window.py:353", "show_login entry", {}, "H3")
        # #endregion
        dialog = LoginDialog(self)
        # #region agent log
        _debug_log("main_window.py:356", "Before dialog.exec()", {}, "H3")
        # #endregion
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # #region agent log
            _debug_log("main_window.py:358", "Login accepted, before clear_ui", {}, "H3")
            # #endregion
            # Clear existing UI to prevent duplication
            try:
                self.clear_ui()
                # #region agent log
                _debug_log("main_window.py:362", "After clear_ui, before setup_ui", {}, "H3")
                # #endregion
                # Reinitialize UI
                self.setup_ui()
                # #region agent log
                _debug_log("main_window.py:365", "After setup_ui, before setup_menu", {}, "H3")
                # #endregion
                self.setup_menu()
                # #region agent log
                _debug_log("main_window.py:367", "After setup_menu, before setup_status_bar", {}, "H3")
                # #endregion
                self.setup_status_bar()
                # #region agent log
                _debug_log("main_window.py:369", "After setup_status_bar, before show()", {}, "H3")
                # #endregion
                self.show()  # Show window after successful login
                # #region agent log
                _debug_log("main_window.py:371", "show_login complete", {}, "H3")
                # #endregion
            except Exception as e:
                # #region agent log
                _debug_log("main_window.py:373", "Exception in show_login after acceptance", {"error": str(e), "type": type(e).__name__, "traceback": __import__('traceback').format_exc()}, "H3")
                # #endregion
                raise
        else:
            # #region agent log
            _debug_log("main_window.py:376", "Login rejected/cancelled", {}, "H3")
            # #endregion
            self.close()
    
    def clear_ui(self):
        """Clear all UI widgets to prevent duplication."""
        # #region agent log
        _debug_log("main_window.py:400", "clear_ui entry", {}, "H3")
        # #endregion
        try:
            # Clear stacked widget
            if hasattr(self, 'stacked_widget'):
                # #region agent log
                _debug_log("main_window.py:404", "Clearing stacked_widget", {"count": self.stacked_widget.count()}, "H3")
                # #endregion
                while self.stacked_widget.count() > 0:
                    widget = self.stacked_widget.widget(0)
                    self.stacked_widget.removeWidget(widget)
                    if widget:
                        widget.deleteLater()
            
            # Clear widgets dictionary and references
            # #region agent log
            _debug_log("main_window.py:413", "Clearing widgets dictionary", {"widget_count": len(self.widgets)}, "H3")
            # #endregion
            self.widgets.clear()
            
            # Clear dashboard widget reference
            if hasattr(self, 'dashboard_widget'):
                # #region agent log
                _debug_log("main_window.py:418", "Clearing dashboard_widget reference", {}, "H3")
                # #endregion
                delattr(self, 'dashboard_widget')
            
            # Remove sidebar if it exists
            if hasattr(self, 'sidebar'):
                # #region agent log
                _debug_log("main_window.py:424", "Removing sidebar", {}, "H3")
                # #endregion
                self.sidebar.deleteLater()
                delattr(self, 'sidebar')
            
            # Clear central widget
            # #region agent log
            _debug_log("main_window.py:430", "clear_ui complete", {}, "H3")
            # #endregion
        except Exception as e:
            # #region agent log
            _debug_log("main_window.py:432", "Exception in clear_ui", {"error": str(e), "type": type(e).__name__, "traceback": __import__('traceback').format_exc()}, "H3")
            # #endregion
            raise
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()
            self.setCentralWidget(None)
        
        # Clear stacked widget reference
        if hasattr(self, 'stacked_widget'):
            delattr(self, 'stacked_widget')
    
    def on_logout(self):
        """Handle logout."""
        auth_manager.logout()
        # Close the main window and show login
        self.hide()  # Hide main window first
        self.show_login()
        # If login is cancelled, close the app
        if not auth_manager.is_authenticated():
            self.close()
    
    def on_navigation_item_selected(self, item_id: str):
        """Handle navigation item selection."""
        if item_id == "dashboard":
            self.show_dashboard()
        elif item_id == "clients":
            self.show_clients()
        elif item_id == "appointments":
            self.show_appointments()
        elif item_id == "treatment_plans":
            self.show_treatment_plans()
        elif item_id == "medical_records":
            self.show_medical_records()
        elif item_id == "prescriptions":
            self.show_prescriptions()
        elif item_id == "billing":
            self.show_billing()
        elif item_id == "payments":
            self.show_payments()
        elif item_id == "insurance":
            self.show_insurance()
        elif item_id == "staff":
            self.show_staff()
        elif item_id == "doctors":
            self.show_doctors()
        elif item_id == "rooms":
            self.show_rooms()
        elif item_id == "equipment":
            self.show_equipment()
        elif item_id == "reports":
            self.show_reports()
        elif item_id == "calendar":
            self.show_calendar()
        # TODO: Implement other views
    
    def show_dashboard(self):
        """Show dashboard."""
        # Ensure dashboard widget exists and is valid
        if not hasattr(self, 'dashboard_widget') or 'dashboard' not in self.widgets:
            # Recreate dashboard widget if it doesn't exist
            self.dashboard_widget = DashboardWidget()
            self.stacked_widget.addWidget(self.dashboard_widget)
            self.widgets['dashboard'] = self.dashboard_widget
        else:
            # Check if widget is still valid (not deleted)
            try:
                _ = self.dashboard_widget.isVisible()
                # Make sure it's in the stacked widget
                if self.stacked_widget.indexOf(self.dashboard_widget) == -1:
                    self.stacked_widget.addWidget(self.dashboard_widget)
            except RuntimeError:
                # Widget was deleted, recreate it
                self.dashboard_widget = DashboardWidget()
                self.stacked_widget.addWidget(self.dashboard_widget)
                self.widgets['dashboard'] = self.dashboard_widget
        
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        if hasattr(self, 'sidebar'):
            self.sidebar.select_item("dashboard", emit_signal=False)
    
    def show_clients(self):
        """Show clients view."""
        widget = self.get_or_create_widget('clients', ClientsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("clients", emit_signal=False)
    
    def show_appointments(self):
        """Show appointments view."""
        widget = self.get_or_create_widget('appointments', AppointmentsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("appointments", emit_signal=False)
    
    def show_treatment_plans(self):
        """Show treatment plans view."""
        widget = self.get_or_create_widget('treatment_plans', TreatmentPlansWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("treatment_plans", emit_signal=False)
    
    def show_medical_records(self):
        """Show medical records view."""
        widget = self.get_or_create_widget('medical_records', MedicalRecordsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("medical_records", emit_signal=False)
    
    def show_prescriptions(self):
        """Show prescriptions view."""
        widget = self.get_or_create_widget('prescriptions', PrescriptionsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("prescriptions", emit_signal=False)
    
    def show_billing(self):
        """Show billing view."""
        widget = self.get_or_create_widget('billing', BillingWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("billing", emit_signal=False)
    
    def show_payments(self):
        """Show payments view."""
        widget = self.get_or_create_widget('payments', PaymentsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("payments", emit_signal=False)
    
    def show_insurance(self):
        """Show insurance view."""
        widget = self.get_or_create_widget('insurance', InsuranceWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("insurance", emit_signal=False)
    
    def show_staff(self):
        """Show staff view."""
        widget = self.get_or_create_widget('staff', StaffWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("staff", emit_signal=False)
    
    def show_doctors(self):
        """Show doctors view."""
        widget = self.get_or_create_widget('doctors', DoctorsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("doctors", emit_signal=False)
    
    def show_rooms(self):
        """Show rooms view."""
        widget = self.get_or_create_widget('rooms', RoomsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("rooms", emit_signal=False)
    
    def show_equipment(self):
        """Show equipment view."""
        widget = self.get_or_create_widget('equipment', EquipmentWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("equipment", emit_signal=False)
    
    def show_reports(self):
        """Show reports view."""
        widget = self.get_or_create_widget('reports', ReportsWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("reports", emit_signal=False)
    
    def show_calendar(self):
        """Show calendar view."""
        widget = self.get_or_create_widget('calendar', CalendarWidget)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.select_item("calendar", emit_signal=False)
    
    def on_sync_requested(self):
        """Handle sync request."""
        # TODO: Trigger sync
        pass
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Settings were saved, theme may have changed
            # Theme manager will emit signals automatically
            pass
    
    def show_about(self):
        """Show about dialog."""
        # TODO: Implement about dialog
        pass

