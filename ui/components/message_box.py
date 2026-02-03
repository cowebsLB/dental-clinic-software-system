"""Custom neumorphic message box wrapper."""

from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import Qt
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import get_neumorphic_button_style, apply_neumorphic_effect


def show_message(title: str, message: str, icon=QMessageBox.Icon.Information, 
                 buttons=QMessageBox.StandardButton.Ok, parent=None) -> int:
    """Show a neumorphic styled message box.
    
    Args:
        title: Dialog title
        message: Message text
        icon: Message box icon
        buttons: Standard buttons to show
        parent: Parent widget
        
    Returns:
        Button that was clicked
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(icon)
    msg.setStandardButtons(buttons)
    
    # Apply neumorphic styling
    _apply_neumorphic_style(msg)
    
    return msg.exec()


def show_error(title: str, message: str, parent=None) -> int:
    """Show error message box."""
    return show_message(title, message, QMessageBox.Icon.Critical, 
                       QMessageBox.StandardButton.Ok, parent)


def show_warning(title: str, message: str, parent=None) -> int:
    """Show warning message box."""
    return show_message(title, message, QMessageBox.Icon.Warning,
                       QMessageBox.StandardButton.Ok, parent)


def show_info(title: str, message: str, parent=None) -> int:
    """Show info message box."""
    return show_message(title, message, QMessageBox.Icon.Information,
                       QMessageBox.StandardButton.Ok, parent)


def show_success(title: str, message: str, parent=None) -> int:
    """Show success message box."""
    return show_message(title, message, QMessageBox.Icon.Information,
                       QMessageBox.StandardButton.Ok, parent)


def show_question(title: str, message: str, parent=None) -> QMessageBox.StandardButton:
    """Show question message box.
    
    Returns:
        Button that was clicked
    """
    return show_message(title, message, QMessageBox.Icon.Question,
                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, parent)


def _apply_neumorphic_style(msg: QMessageBox):
    """Apply neumorphic styling to message box."""
    palette = theme_manager.get_palette()
    
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: {palette.background};
        }}
        QMessageBox QLabel {{
            color: {palette.text_primary};
            font-size: 14px;
        }}
        QMessageBox QPushButton {{
            {get_neumorphic_button_style()}
        }}
    """)
    
    # Apply neumorphic effect to buttons
    for button in msg.findChildren(QMessageBox):
        if isinstance(button, QMessageBox):
            for btn in button.findChildren(type(msg).__bases__[0] if msg.__class__.__bases__ else []):
                if hasattr(btn, 'setStyleSheet'):
                    apply_neumorphic_effect(btn, inset=False, intensity=1.0)

