"""Theme manager for handling light/dark/auto theme switching."""

import json
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QGuiApplication
from typing import Literal
from pathlib import Path
from ui.themes.colors import get_palette, ColorPalette
from config.settings import Settings

# #region agent log
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

ThemeMode = Literal['light', 'dark', 'auto']


class ThemeManager(QObject):
    """Manages application theme (light/dark/auto) with neumorphism support."""
    
    theme_changed = Signal(str)  # Emits 'light' or 'dark' when theme changes
    
    _instance = None
    
    def __init__(self):
        # #region agent log
        _debug_log("theme_manager.py:21", "ThemeManager.__init__ entry", {}, "H1,H2")
        # #endregion
        super().__init__()
        # #region agent log
        _debug_log("theme_manager.py:24", "After super().__init__", {}, "H1")
        # #endregion
        self.settings = Settings()
        # #region agent log
        _debug_log("theme_manager.py:26", "Settings loaded", {}, "H1")
        # #endregion
        self._mode: ThemeMode = self._load_theme_mode()
        # #region agent log
        _debug_log("theme_manager.py:27", "Theme mode loaded", {"mode": self._mode}, "H1")
        # #endregion
        self._high_contrast = self._load_high_contrast()
        self._current_theme = self._determine_theme()
        # #region agent log
        _debug_log("theme_manager.py:29", "Theme determined", {"current_theme": self._current_theme}, "H1")
        # #endregion
        
        # Connect to system theme changes if in auto mode
        if self._mode == 'auto':
            # #region agent log
            _debug_log("theme_manager.py:32", "Before QGuiApplication.instance()", {}, "H1")
            # #endregion
            app = QGuiApplication.instance()
            # #region agent log
            _debug_log("theme_manager.py:34", "After QGuiApplication.instance()", {"app_exists": app is not None}, "H1")
            # #endregion
            if app:
                try:
                    hints = app.styleHints()
                    # #region agent log
                    _debug_log("theme_manager.py:37", "Got styleHints", {"has_colorSchemeChanged": hasattr(hints, 'colorSchemeChanged')}, "H1")
                    # #endregion
                    if hasattr(hints, 'colorSchemeChanged'):
                        hints.colorSchemeChanged.connect(self._on_system_theme_changed)
                        # #region agent log
                        _debug_log("theme_manager.py:40", "Connected colorSchemeChanged", {}, "H1")
                        # #endregion
                except (AttributeError, TypeError) as e:
                    # #region agent log
                    _debug_log("theme_manager.py:42", "Exception in theme connection", {"error": str(e)}, "H1")
                    # #endregion
                    # colorSchemeChanged signal may not be available
                    pass
        # #region agent log
        _debug_log("theme_manager.py:45", "ThemeManager.__init__ complete", {}, "H1,H2")
        # #endregion
    
    @classmethod
    def instance(cls):
        """Get singleton instance of ThemeManager."""
        # #region agent log
        _debug_log("theme_manager.py:48", "ThemeManager.instance() called", {"_instance_exists": cls._instance is not None}, "H2")
        # #endregion
        if cls._instance is None:
            # #region agent log
            _debug_log("theme_manager.py:50", "Creating new ThemeManager instance", {}, "H2")
            # #endregion
            cls._instance = cls()
        # #region agent log
        _debug_log("theme_manager.py:53", "Returning ThemeManager instance", {}, "H2")
        # #endregion
        return cls._instance
    
    def _load_theme_mode(self) -> ThemeMode:
        """Load theme mode from settings."""
        mode = self.settings.get('theme_mode', 'auto')
        if mode in ['light', 'dark', 'auto']:
            return mode
        return 'auto'
    
    def _load_high_contrast(self) -> bool:
        """Load high contrast setting."""
        return self.settings.get('high_contrast', False)
    
    def _save_theme_mode(self):
        """Save theme mode to settings."""
        self.settings.set('theme_mode', self._mode)
        self.settings.set('high_contrast', self._high_contrast)
    
    def _determine_theme(self) -> str:
        """Determine current theme based on mode."""
        if self._mode == 'auto':
            return self._get_system_theme()
        return self._mode
    
    def _get_system_theme(self) -> str:
        """Get system theme preference."""
        app = QGuiApplication.instance()
        if app:
            try:
                hints = app.styleHints()
                if hasattr(hints, 'colorScheme'):
                    scheme = hints.colorScheme()
                    # Check enum values directly from the hints object
                    # Dark = 2, Light = 1 (Qt enum values)
                    if scheme == 2:  # Dark
                        return 'dark'
                    elif scheme == 1:  # Light
                        return 'light'
            except (AttributeError, TypeError):
                # Fallback if colorScheme is not available
                pass
        # Default to light theme if detection fails
        return 'light'
    
    def _on_system_theme_changed(self):
        """Handle system theme change."""
        if self._mode == 'auto':
            old_theme = self._current_theme
            self._current_theme = self._get_system_theme()
            if old_theme != self._current_theme:
                self.theme_changed.emit(self._current_theme)
    
    def get_mode(self) -> ThemeMode:
        """Get current theme mode."""
        return self._mode
    
    def set_mode(self, mode: ThemeMode):
        """Set theme mode."""
        if mode not in ['light', 'dark', 'auto']:
            raise ValueError(f"Invalid theme mode: {mode}")
        
        self._mode = mode
        old_theme = self._current_theme
        self._current_theme = self._determine_theme()
        self._save_theme_mode()
        
        if old_theme != self._current_theme:
            self.theme_changed.emit(self._current_theme)
    
    def get_theme(self) -> str:
        """Get current theme ('light' or 'dark')."""
        return self._current_theme
    
    def is_high_contrast(self) -> bool:
        """Check if high contrast mode is enabled."""
        return self._high_contrast
    
    def set_high_contrast(self, enabled: bool):
        """Enable or disable high contrast mode."""
        if self._high_contrast != enabled:
            self._high_contrast = enabled
            self._save_theme_mode()
            self.theme_changed.emit(self._current_theme)
    
    def get_palette(self) -> ColorPalette:
        """Get current color palette."""
        # #region agent log
        _debug_log("theme_manager.py:133", "get_palette() called", {"theme": self._current_theme, "high_contrast": self._high_contrast}, "H4")
        # #endregion
        palette = get_palette(self._current_theme, self._high_contrast)
        # #region agent log
        _debug_log("theme_manager.py:136", "get_palette() returning", {"base_color": palette.base}, "H4")
        # #endregion
        return palette
    
    def get_base_color(self) -> str:
        """Get base color for current theme."""
        return self.get_palette().base
    
    def get_light_shadow(self) -> str:
        """Get light shadow color."""
        return self.get_palette().light_shadow
    
    def get_dark_shadow(self) -> str:
        """Get dark shadow color."""
        return self.get_palette().dark_shadow
    
    def get_text_color(self, variant: str = 'primary') -> str:
        """Get text color.
        
        Args:
            variant: 'primary', 'secondary', or 'disabled'
        """
        palette = self.get_palette()
        if variant == 'primary':
            return palette.text_primary
        elif variant == 'secondary':
            return palette.text_secondary
        elif variant == 'disabled':
            return palette.text_disabled
        return palette.text_primary
    
    def get_accent_color(self, state: str = 'normal') -> str:
        """Get accent color.
        
        Args:
            state: 'normal', 'hover', or 'pressed'
        """
        palette = self.get_palette()
        if state == 'hover':
            return palette.accent_hover
        elif state == 'pressed':
            return palette.accent_pressed
        return palette.accent
    
    def get_status_color(self, status: str) -> str:
        """Get status color.
        
        Args:
            status: 'error', 'warning', 'success', or 'info'
        """
        palette = self.get_palette()
        if status == 'error':
            return palette.error
        elif status == 'warning':
            return palette.warning
        elif status == 'success':
            return palette.success
        elif status == 'info':
            return palette.info
        return palette.accent


# Global instance
# #region agent log
try:
    _debug_log("theme_manager.py:193", "Creating global theme_manager", {}, "H2")
except:
    pass
# #endregion
try:
    # #region agent log
    _debug_log("theme_manager.py:199", "Before ThemeManager.instance() call", {}, "H2")
    # #endregion
    theme_manager = ThemeManager.instance()
    # #region agent log
    _debug_log("theme_manager.py:202", "After ThemeManager.instance() call", {"theme_manager_exists": theme_manager is not None}, "H2")
    # #endregion
    # #region agent log
    try:
        theme = theme_manager.get_theme()
        _debug_log("theme_manager.py:206", "Global theme_manager created", {"theme": theme}, "H2")
    except Exception as e:
        _debug_log("theme_manager.py:208", "Error getting theme from theme_manager", {"error": str(e)}, "H2")
    # #endregion
except Exception as e:
    # #region agent log
    _debug_log("theme_manager.py:211", "Exception creating global theme_manager", {"error": str(e), "type": type(e).__name__, "traceback": __import__('traceback').format_exc()}, "H2")
    # #endregion
    raise

