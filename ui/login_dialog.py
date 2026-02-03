"""Login dialog for Supabase Auth."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from auth.auth_manager import auth_manager
from config.i18n import tr
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import (get_neumorphic_input_style, get_neumorphic_button_style,
                                   get_neumorphic_card_style, apply_neumorphic_effect)

class LoginDialog(QDialog):
    """Login dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("auth.login"))
        self.setModal(True)
        self.setFixedWidth(350)
        self._logging_in = False  # Guard to prevent duplicate login attempts
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        # Apply neumorphic theme to dialog
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {palette.background};
            }}
        """)
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        self.title_label = QLabel(tr("app.title"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_title_style()
        layout.addWidget(self.title_label)
        
        # Username field
        self.username_label = QLabel(tr("auth.username"))
        self._update_label_style(self.username_label)
        layout.addWidget(self.username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self._update_input_style(self.username_input)
        apply_neumorphic_effect(self.username_input, inset=True, intensity=0.8)
        layout.addWidget(self.username_input)
        
        # Password field
        self.password_label = QLabel(tr("auth.password"))
        self._update_label_style(self.password_label)
        layout.addWidget(self.password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self._update_input_style(self.password_input)
        apply_neumorphic_effect(self.password_input, inset=True, intensity=0.8)
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_button = QPushButton(tr("auth.login"))
        self.login_button.setDefault(True)
        self._update_button_style(self.login_button)
        apply_neumorphic_effect(self.login_button, inset=False, intensity=1.0)
        self.login_button.clicked.connect(self.on_login)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton(tr("common.cancel"))
        self._update_button_style(self.cancel_button)
        apply_neumorphic_effect(self.cancel_button, inset=False, intensity=1.0)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _update_title_style(self):
        """Update title style."""
        palette = theme_manager.get_palette()
        self.title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {palette.text_primary};
            background: transparent;
            margin-bottom: 10px;
        """)
    
    def _update_label_style(self, label: QLabel):
        """Update label style."""
        palette = theme_manager.get_palette()
        label.setStyleSheet(f"""
            color: {palette.text_primary};
            font-size: 14px;
            font-weight: 500;
            background: transparent;
        """)
    
    def _update_input_style(self, input_widget: QLineEdit):
        """Update input style."""
        input_widget.setStyleSheet(get_neumorphic_input_style())
    
    def _update_button_style(self, button: QPushButton):
        """Update button style."""
        button.setStyleSheet(get_neumorphic_button_style())
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        palette = theme_manager.get_palette()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {palette.background};
            }}
        """)
        self._update_title_style()
        self._update_label_style(self.username_label)
        self._update_label_style(self.password_label)
        self._update_input_style(self.username_input)
        self._update_input_style(self.password_input)
        self._update_button_style(self.login_button)
        self._update_button_style(self.cancel_button)
        
        # Note: Enter key is handled by the default button (login_button.setDefault(True))
        # No need to connect returnPressed separately to avoid duplicate calls
    
    def on_login(self):
        """Handle login."""
        # Prevent duplicate calls
        if self._logging_in:
            return
        
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, tr("common.error"), "Please enter username and password")
            return
        
        self._logging_in = True
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        
        success, error = auth_manager.login(username, password)
        
        self._logging_in = False  # Reset guard
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, tr("common.error"), error or tr("auth.invalid_credentials"))
            self.login_button.setEnabled(True)
            self.login_button.setText(tr("auth.login"))

