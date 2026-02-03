"""Main entry point for Dental Clinic Management System."""

import sys
import json
import os
from pathlib import Path

# #region agent log - EARLY LOGGING
DEBUG_LOG_PATH = r"c:\Users\COWebs.lb\Desktop\my files\01-Projects\dental clinic software system\.cursor\debug.log"
def _debug_log(location, message, data=None, hypothesis_id=None):
    try:
        os.makedirs(os.path.dirname(DEBUG_LOG_PATH), exist_ok=True)
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
    except Exception as e:
        try:
            with open(DEBUG_LOG_PATH + '.error', 'a', encoding='utf-8') as f:
                f.write(f"Log error: {str(e)}\n")
        except: pass
# #endregion

# #region agent log
_debug_log("main.py:1", "Script started", {"python_version": sys.version}, "H1,H2")
# #endregion

try:
    # #region agent log
    _debug_log("main.py:30", "Before PySide6 imports", {}, "H1")
    # #endregion
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    # #region agent log
    _debug_log("main.py:33", "PySide6 imports successful", {}, "H1")
    # #endregion
except Exception as e:
    # #region agent log
    _debug_log("main.py:35", "PySide6 import failed", {"error": str(e), "type": type(e).__name__}, "H1")
    # #endregion
    raise

try:
    # #region agent log
    _debug_log("main.py:40", "Before config.settings import", {}, "H1")
    # #endregion
    from config.settings import settings
    # #region agent log
    _debug_log("main.py:42", "config.settings import successful", {}, "H1")
    # #endregion
except Exception as e:
    # #region agent log
    _debug_log("main.py:44", "config.settings import failed", {"error": str(e), "type": type(e).__name__}, "H1")
    # #endregion
    raise

try:
    # #region agent log
    _debug_log("main.py:48", "Before ui.main_window import", {}, "H1,H2")
    # #endregion
    from ui.main_window import MainWindow
    # #region agent log
    _debug_log("main.py:50", "ui.main_window import successful", {}, "H1,H2")
    # #endregion
except Exception as e:
    # #region agent log
    _debug_log("main.py:52", "ui.main_window import failed", {"error": str(e), "type": type(e).__name__, "traceback": __import__('traceback').format_exc()}, "H1,H2")
    # #endregion
    raise


def main():
    """Main application entry point."""
    # #region agent log
    _debug_log("main.py:11", "main() entry", {"argv": sys.argv}, "H1")
    # #endregion
    
    # Create application first (needed for message boxes)
    app = QApplication(sys.argv)
    # #region agent log
    _debug_log("main.py:15", "QApplication created", {"app_exists": app is not None}, "H1")
    # #endregion
    
    app.setApplicationName("Dental Clinic Management System")
    app.setOrganizationName("Dental Clinic")
    app.setStyle('Fusion')
    
    # Validate required settings
    # #region agent log
    _debug_log("main.py:20", "Before validate_required_settings", {}, "H1")
    # #endregion
    is_valid, errors = settings.validate_required_settings()
    # #region agent log
    _debug_log("main.py:21", "After validate_required_settings", {"is_valid": is_valid, "errors": errors}, "H1")
    # #endregion
    if not is_valid:
        error_msg = "Configuration errors:\n\n"
        for error in errors:
            error_msg += f"  • {error}\n"
        error_msg += "\nPlease configure your .env file with required settings.\n\n"
        
        if settings.auth_mode == 'supabase':
            error_msg += "Required settings for Supabase mode:\n"
            error_msg += "  • SUPABASE_URL\n"
            error_msg += "  • SUPABASE_ANON_KEY\n"
        else:
            error_msg += "Note: Using SQLite mode (AUTH_MODE=sqlite)\n"
            error_msg += "No Supabase configuration needed.\n"
        
        QMessageBox.critical(
            None,
            "Configuration Error",
            error_msg
        )
        return 1
    
    # Create and show main window
    try:
        # #region agent log
        _debug_log("main.py:43", "Before MainWindow creation", {}, "H2,H3")
        # #endregion
        window = MainWindow()
        # #region agent log
        _debug_log("main.py:45", "After MainWindow creation", {"window_exists": window is not None}, "H2,H3")
        # #endregion
        window.show()
        # #region agent log
        _debug_log("main.py:47", "Before app.exec()", {}, "H1")
        # #endregion
        return app.exec()
    except Exception as e:
        # #region agent log
        _debug_log("main.py:48", "Exception in main", {"error": str(e), "type": type(e).__name__}, "H2,H3")
        # #endregion
        QMessageBox.critical(
            None,
            "Application Error",
            f"Failed to start application:\n\n{str(e)}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
