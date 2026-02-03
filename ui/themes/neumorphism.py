"""Neumorphism utility functions for generating shadow effects and styles."""

import json
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor
from typing import Optional, Tuple
from ui.themes.theme_manager import theme_manager

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


def create_neumorphic_shadow(widget: QWidget, inset: bool = False, 
                             intensity: float = 1.0) -> Tuple[QGraphicsDropShadowEffect, QGraphicsDropShadowEffect]:
    """Create dual shadows for neumorphic effect.
    
    Args:
        widget: Widget to apply shadows to
        inset: If True, create inset effect (reversed shadows)
        intensity: Shadow intensity multiplier (0.0 to 1.0)
        
    Returns:
        Tuple of (light_shadow, dark_shadow) effects
    """
    palette = theme_manager.get_palette()
    
    # Shadow parameters
    blur_radius = int(12 * intensity)
    offset = int(4 * intensity)
    
    if inset:
        # Inset: dark shadow top-left, light shadow bottom-right
        light_shadow = QGraphicsDropShadowEffect()
        light_shadow.setColor(QColor(palette.light_shadow))
        light_shadow.setBlurRadius(blur_radius)
        light_shadow.setOffset(QPointF(offset, offset))
        
        dark_shadow = QGraphicsDropShadowEffect()
        dark_shadow.setColor(QColor(palette.dark_shadow))
        dark_shadow.setBlurRadius(blur_radius)
        dark_shadow.setOffset(QPointF(-offset, -offset))
    else:
        # Outset: light shadow top-left, dark shadow bottom-right
        light_shadow = QGraphicsDropShadowEffect()
        light_shadow.setColor(QColor(palette.light_shadow))
        light_shadow.setBlurRadius(blur_radius)
        light_shadow.setOffset(QPointF(-offset, -offset))
        
        dark_shadow = QGraphicsDropShadowEffect()
        dark_shadow.setColor(QColor(palette.dark_shadow))
        dark_shadow.setBlurRadius(blur_radius)
        dark_shadow.setOffset(QPointF(offset, offset))
    
    return light_shadow, dark_shadow


def apply_neumorphic_effect(widget: QWidget, inset: bool = False, intensity: float = 1.0):
    """Apply neumorphic shadow effect to a widget.
    
    Note: Qt only supports one QGraphicsDropShadowEffect per widget.
    This function applies the dark shadow (primary effect). For true dual shadows,
    you may need to use CSS box-shadow or composite widgets.
    
    Args:
        widget: Widget to apply effect to
        inset: If True, create inset effect
        intensity: Shadow intensity multiplier
    """
    # #region agent log
    _debug_log("neumorphism.py:73", "apply_neumorphic_effect entry", {"widget_exists": widget is not None, "inset": inset, "intensity": intensity}, "H4")
    # #endregion
    if not widget:
        # #region agent log
        _debug_log("neumorphism.py:88", "apply_neumorphic_effect: widget is None", {}, "H4")
        # #endregion
        return
    try:
        # #region agent log
        _debug_log("neumorphism.py:92", "Before create_neumorphic_shadow", {}, "H4")
        # #endregion
        _, dark_shadow = create_neumorphic_shadow(widget, inset, intensity)
        # #region agent log
        _debug_log("neumorphism.py:94", "After create_neumorphic_shadow", {"shadow_exists": dark_shadow is not None}, "H4")
        # #endregion
        widget.setGraphicsEffect(dark_shadow)
        # #region agent log
        _debug_log("neumorphism.py:96", "After setGraphicsEffect", {}, "H4")
        # #endregion
    except Exception as e:
        # #region agent log
        _debug_log("neumorphism.py:98", "Exception in apply_neumorphic_effect", {"error": str(e), "type": type(e).__name__}, "H4")
        # #endregion
        raise


def get_neumorphic_button_style(inset: bool = False, hover: bool = False, 
                                pressed: bool = False) -> str:
    """Generate QSS style for neumorphic button.
    
    Args:
        inset: If True, button appears pressed in
        hover: If True, button is in hover state
        pressed: If True, button is in pressed state
        
    Returns:
        QSS style string
    """
    palette = theme_manager.get_palette()
    base_color = palette.base
    
    if pressed or inset:
        # Inset effect: dark top-left, light bottom-right
        shadow_color_1 = palette.dark_shadow
        shadow_color_2 = palette.light_shadow
        offset_1 = "2px 2px"
        offset_2 = "-2px -2px"
    else:
        # Outset effect: light top-left, dark bottom-right
        shadow_color_1 = palette.light_shadow
        shadow_color_2 = palette.dark_shadow
        offset_1 = "-2px -2px"
        offset_2 = "2px 2px"
    
    if hover and not pressed:
        blur = "15px"
    else:
        blur = "12px"
    
    # Note: Qt QSS doesn't support dual box-shadows directly
    # We'll use a single shadow that approximates the effect
    shadow = f"{offset_2} {blur} {shadow_color_2}"
    
    return f"""
        QPushButton {{
            background-color: {base_color};
            border: 1px solid {palette.border};
            border-radius: 12px;
            padding: 10px 20px;
            color: {palette.text_primary};
        }}
        QPushButton:hover {{
            background-color: {base_color};
        }}
        QPushButton:pressed {{
            background-color: {base_color};
        }}
    """


def get_neumorphic_input_style(focused: bool = False, error: bool = False) -> str:
    """Generate QSS style for neumorphic input field (always inset).
    
    Args:
        focused: If True, input is focused
        error: If True, show error state
        
    Returns:
        QSS style string
    """
    palette = theme_manager.get_palette()
    base_color = palette.base
    
    border_color = palette.accent if focused else palette.border
    if error:
        border_color = palette.error
    
    return f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {base_color};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 10px 15px;
            color: {palette.text_primary};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {palette.accent};
        }}
    """


def get_neumorphic_card_style() -> str:
    """Generate QSS style for neumorphic card (outset effect).
    
    Returns:
        QSS style string
    """
    palette = theme_manager.get_palette()
    base_color = palette.base
    
    return f"""
        QWidget {{
            background-color: {base_color};
            border: 1px solid {palette.border};
            border-radius: 20px;
        }}
    """


def get_neumorphic_table_style() -> str:
    """Generate QSS style for neumorphic table.
    
    Returns:
        QSS style string
    """
    palette = theme_manager.get_palette()
    base_color = palette.base
    
    return f"""
        QTableWidget {{
            background-color: {base_color};
            border: 1px solid {palette.border};
            border-radius: 15px;
            color: {palette.text_primary};
            gridline-color: {palette.border_light};
        }}
        QTableWidget::item {{
            padding: 8px;
        }}
        QTableWidget::item:selected {{
            background-color: {palette.accent};
            color: {palette.text_primary};
        }}
        QHeaderView::section {{
            background-color: {palette.surface};
            color: {palette.text_primary};
            padding: 10px;
            border: none;
            font-weight: 600;
        }}
    """


# Shadow cache for performance
_shadow_cache = {}


def get_cached_shadow(key: str, inset: bool, intensity: float) -> Optional[QGraphicsDropShadowEffect]:
    """Get cached shadow effect or create new one.
    
    Args:
        key: Cache key
        inset: Whether shadow is inset
        intensity: Shadow intensity
        
    Returns:
        Cached or new shadow effect
    """
    cache_key = f"{key}_{inset}_{intensity}"
    if cache_key not in _shadow_cache:
        # Create a dummy widget for shadow creation
        from PySide6.QtWidgets import QWidget
        dummy = QWidget()
        _, shadow = create_neumorphic_shadow(dummy, inset, intensity)
        _shadow_cache[cache_key] = shadow
    return _shadow_cache.get(cache_key)

