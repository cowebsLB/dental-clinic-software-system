"""Color palette definitions for light and dark themes."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorPalette:
    """Color palette for a theme."""
    # Base colors
    base: str
    surface: str
    background: str
    
    # Shadow colors for neumorphism
    light_shadow: str
    dark_shadow: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str
    
    # Accent colors
    accent: str
    accent_hover: str
    accent_pressed: str
    
    # Status colors
    error: str
    warning: str
    success: str
    info: str
    
    # Border colors
    border: str
    border_light: str
    border_dark: str


# Light theme palette
LIGHT_PALETTE = ColorPalette(
    base="#E0E5EC",
    surface="#F5F7FA",
    background="#FFFFFF",
    light_shadow="#FFFFFF",
    dark_shadow="#A3B1C6",
    text_primary="#2C3E50",
    text_secondary="#5A6C7D",
    text_disabled="#95A5A6",
    accent="#4A90E2",
    accent_hover="#357ABD",
    accent_pressed="#2E6DA4",
    error="#E74C3C",
    warning="#F39C12",
    success="#27AE60",
    info="#3498DB",
    border="#D1D9E0",
    border_light="#E8ECF0",
    border_dark="#B8C4D0"
)

# Dark theme palette
DARK_PALETTE = ColorPalette(
    base="#2B2B2B",
    surface="#353535",
    background="#1F1F1F",
    light_shadow="#3A3A3A",
    dark_shadow="#1F1F1F",
    text_primary="#ECF0F1",
    text_secondary="#BDC3C7",
    text_disabled="#7F8C8D",
    accent="#5DADE2",
    accent_hover="#4A9BC7",
    accent_pressed="#3D8BB3",
    error="#E74C3C",
    warning="#F39C12",
    success="#2ECC71",
    info="#3498DB",
    border="#404040",
    border_light="#4A4A4A",
    border_dark="#2A2A2A"
)

# High contrast light theme
HIGH_CONTRAST_LIGHT_PALETTE = ColorPalette(
    base="#E0E5EC",
    surface="#FFFFFF",
    background="#FFFFFF",
    light_shadow="#FFFFFF",
    dark_shadow="#8B9DC3",
    text_primary="#000000",
    text_secondary="#333333",
    text_disabled="#666666",
    accent="#0066CC",
    accent_hover="#0052A3",
    accent_pressed="#003D7A",
    error="#CC0000",
    warning="#FF6600",
    success="#006600",
    info="#0066CC",
    border="#000000",
    border_light="#333333",
    border_dark="#000000"
)

# High contrast dark theme
HIGH_CONTRAST_DARK_PALETTE = ColorPalette(
    base="#1A1A1A",
    surface="#2A2A2A",
    background="#0F0F0F",
    light_shadow="#4A4A4A",
    dark_shadow="#000000",
    text_primary="#FFFFFF",
    text_secondary="#E0E0E0",
    text_disabled="#A0A0A0",
    accent="#66B3FF",
    accent_hover="#4DA3FF",
    accent_pressed="#3399FF",
    error="#FF3333",
    warning="#FF9900",
    success="#00CC66",
    info="#3399FF",
    border="#FFFFFF",
    border_light="#CCCCCC",
    border_dark="#FFFFFF"
)


def get_palette(theme: str, high_contrast: bool = False) -> ColorPalette:
    """Get color palette for a theme.
    
    Args:
        theme: 'light' or 'dark'
        high_contrast: Whether to use high contrast variant
        
    Returns:
        ColorPalette instance
    """
    if high_contrast:
        if theme == 'light':
            return HIGH_CONTRAST_LIGHT_PALETTE
        else:
            return HIGH_CONTRAST_DARK_PALETTE
    else:
        if theme == 'light':
            return LIGHT_PALETTE
        else:
            return DARK_PALETTE

