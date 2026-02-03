"""Animation utilities for smooth transitions."""

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PySide6.QtWidgets import QWidget
from typing import Optional, Callable


def create_fade_animation(widget: QWidget, start_opacity: float = 0.0, 
                         end_opacity: float = 1.0, duration: int = 300) -> QPropertyAnimation:
    """Create a fade animation for a widget.
    
    Args:
        widget: Widget to animate
        start_opacity: Starting opacity (0.0 to 1.0)
        end_opacity: Ending opacity (0.0 to 1.0)
        duration: Animation duration in milliseconds
        
    Returns:
        QPropertyAnimation instance
    """
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(start_opacity)
    animation.setEndValue(end_opacity)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    return animation


def create_theme_transition_animation(widget: QWidget, duration: int = 400) -> QPropertyAnimation:
    """Create a smooth theme transition animation.
    
    Args:
        widget: Widget to animate
        duration: Animation duration in milliseconds
        
    Returns:
        QPropertyAnimation instance
    """
    return create_fade_animation(widget, 1.0, 0.3, duration // 2)


def animate_shadow_intensity(widget: QWidget, start_intensity: float, 
                            end_intensity: float, duration: int = 200) -> Optional[QPropertyAnimation]:
    """Animate shadow intensity change (for hover effects).
    
    Note: This is a placeholder. Actual shadow intensity animation would require
    custom properties or re-applying shadow effects.
    
    Args:
        widget: Widget to animate
        start_intensity: Starting intensity (0.0 to 1.0)
        end_intensity: Ending intensity (0.0 to 1.0)
        duration: Animation duration in milliseconds
        
    Returns:
        None (placeholder for future implementation)
    """
    # TODO: Implement shadow intensity animation
    # This would require custom properties or effect re-application
    return None


def create_button_press_animation(widget: QWidget, duration: int = 100) -> QPropertyAnimation:
    """Create a quick press animation for buttons.
    
    Args:
        widget: Button widget to animate
        duration: Animation duration in milliseconds
        
    Returns:
        QPropertyAnimation instance
    """
    # Animate opacity for quick feedback
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.7)
    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    # Auto-reverse for press effect
    def on_finished():
        reverse = QPropertyAnimation(widget, b"windowOpacity")
        reverse.setDuration(duration)
        reverse.setStartValue(0.7)
        reverse.setEndValue(1.0)
        reverse.setEasingCurve(QEasingCurve.Type.InOutQuad)
        reverse.start()
    
    animation.finished.connect(on_finished)
    return animation


def create_slide_animation(widget: QWidget, start_x: int, end_x: int, 
                          duration: int = 300) -> QPropertyAnimation:
    """Create a slide animation.
    
    Args:
        widget: Widget to animate
        start_x: Starting X position
        end_x: Ending X position
        duration: Animation duration in milliseconds
        
    Returns:
        QPropertyAnimation instance
    """
    animation = QPropertyAnimation(widget, b"geometry")
    animation.setDuration(duration)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    # Note: Actual geometry animation requires setting start/end QRect
    return animation


class AnimationGroup:
    """Helper class for managing multiple animations."""
    
    def __init__(self):
        self.animations = []
    
    def add(self, animation: QAbstractAnimation):
        """Add an animation to the group."""
        self.animations.append(animation)
    
    def start(self):
        """Start all animations."""
        for animation in self.animations:
            animation.start()
    
    def stop(self):
        """Stop all animations."""
        for animation in self.animations:
            animation.stop()

