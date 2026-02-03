"""Calendar widget with day/week/month views."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QCalendarWidget)
from PySide6.QtCore import Qt, QDate
from typing import Optional, List, Dict
from datetime import datetime
from ui.themes.theme_manager import theme_manager
from ui.themes.neumorphism import get_neumorphic_button_style, apply_neumorphic_effect

class CalendarWidget(QWidget):
    """Calendar widget for appointments."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_view = 'month'  # month, week, day
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # View selector
        view_layout = QHBoxLayout()
        view_layout.setSpacing(10)
        
        self.month_button = QPushButton("Month")
        self.month_button.setCheckable(True)
        self.month_button.setChecked(True)
        self.month_button.clicked.connect(lambda: self.set_view('month'))
        self._update_button_style(self.month_button)
        apply_neumorphic_effect(self.month_button, inset=False, intensity=1.0)
        view_layout.addWidget(self.month_button)
        
        self.week_button = QPushButton("Week")
        self.week_button.setCheckable(True)
        self.week_button.clicked.connect(lambda: self.set_view('week'))
        self._update_button_style(self.week_button)
        apply_neumorphic_effect(self.week_button, inset=False, intensity=1.0)
        view_layout.addWidget(self.week_button)
        
        self.day_button = QPushButton("Day")
        self.day_button.setCheckable(True)
        self.day_button.clicked.connect(lambda: self.set_view('day'))
        self._update_button_style(self.day_button)
        apply_neumorphic_effect(self.day_button, inset=False, intensity=1.0)
        view_layout.addWidget(self.day_button)
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        view_layout.addStretch()
        layout.addLayout(view_layout)
        
        # Calendar widget with neumorphic theme
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Set navigation bar to be visible
        self.calendar.setNavigationBarVisible(True)
        # Set to only show dates from the current month
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        # Hide dates from other months
        self.calendar.setDateEditEnabled(True)
        self._update_calendar_style()
        apply_neumorphic_effect(self.calendar, inset=False, intensity=0.9)
        layout.addWidget(self.calendar)
        
        # Hide dates from other months
        self._hide_other_month_dates()
        
        # Connect to month changed signal to update when month changes
        self.calendar.currentPageChanged.connect(self._hide_other_month_dates)
        
        # TODO: Add appointment display for selected date
    
    def _update_button_style(self, button: QPushButton):
        """Update button style with neumorphic theme."""
        palette = theme_manager.get_palette()
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {palette.base};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {palette.surface};
            }}
            QPushButton:checked {{
                background-color: {palette.accent};
                color: {palette.text_primary};
                font-weight: 600;
            }}
        """)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self._update_button_style(self.month_button)
        self._update_button_style(self.week_button)
        self._update_button_style(self.day_button)
        self._update_calendar_style()
    
    def _update_calendar_style(self):
        """Update calendar style with neumorphic theme."""
        palette = theme_manager.get_palette()
        self.calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background-color: {palette.base};
                border: 1px solid {palette.border};
                border-radius: 20px;
                color: {palette.text_primary};
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background: transparent;
                color: {palette.text_primary};
                selection-background-color: {palette.accent};
                selection-color: {palette.text_primary};
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {palette.text_disabled};
            }}
            QCalendarWidget QTableView {{
                background: transparent;
                alternate-background-color: {palette.base};
                selection-background-color: {palette.accent};
                color: {palette.text_primary};
                border: none;
                gridline-color: {palette.border_light};
            }}
            QCalendarWidget QTableView::item {{
                border: none;
                padding: 8px;
                color: {palette.text_primary};
            }}
            QCalendarWidget QTableView::item:selected {{
                background-color: {palette.accent};
                border-radius: 4px;
                color: {palette.text_primary};
            }}
            QCalendarWidget QTableView::item:hover {{
                background-color: {palette.surface};
            }}
            QCalendarWidget QHeaderView::section {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                padding: 10px;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }}
            QCalendarWidget QComboBox {{
                background-color: {palette.base};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 100px;
            }}
            QCalendarWidget QComboBox:hover {{
                border-color: {palette.accent};
            }}
            QCalendarWidget QComboBox::drop-down {{
                border: none;
                width: 20px;
                background: transparent;
            }}
            QCalendarWidget QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {palette.text_primary};
                width: 0;
                height: 0;
                margin-right: 5px;
            }}
            QCalendarWidget QComboBox QAbstractItemView {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 4px;
                selection-background-color: {palette.accent};
                selection-color: {palette.text_primary};
                padding: 4px;
            }}
            QCalendarWidget QComboBox QAbstractItemView::item {{
                padding: 5px 10px;
                border-radius: 2px;
            }}
            QCalendarWidget QComboBox QAbstractItemView::item:hover {{
                background-color: {palette.base};
            }}
            QCalendarWidget QComboBox QAbstractItemView::item:selected {{
                background-color: {palette.accent};
            }}
            QCalendarWidget QSpinBox {{
                background-color: {palette.base};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }}
            QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {{
                background-color: {palette.surface};
                border: none;
                width: 20px;
            }}
            QCalendarWidget QSpinBox::up-button:hover, QCalendarWidget QSpinBox::down-button:hover {{
                background-color: {palette.accent};
            }}
            QCalendarWidget QToolButton {{
                background-color: {palette.base};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 4px;
                padding: 5px;
                min-width: 30px;
                min-height: 30px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {palette.surface};
            }}
            QCalendarWidget QToolButton:pressed {{
                background-color: {palette.accent};
            }}
        """)
    
    def _hide_other_month_dates(self):
        """Hide or make dates from other months nearly invisible."""
        from PySide6.QtGui import QTextCharFormat, QColor
        
        # Get current month and year from the calendar's displayed month
        year_shown = self.calendar.yearShown()
        month_shown = self.calendar.monthShown()
        
        # Create format for dates from other months (nearly invisible)
        other_month_format = QTextCharFormat()
        other_month_format.setForeground(QColor(255, 255, 255, 20))  # Very transparent
        
        # Get the date range for the displayed month
        first_day = QDate(year_shown, month_shown, 1)
        last_day = first_day.addMonths(1).addDays(-1)
        
        # Get the first day of the week for the first day of the month
        # This tells us which day of the week the month starts on
        first_weekday = first_day.dayOfWeek()
        
        # Format dates from previous month (up to 6 days before the 1st)
        for i in range(1, first_weekday + 1):
            prev_date = first_day.addDays(-i)
            if prev_date.month() != month_shown:
                self.calendar.setDateTextFormat(prev_date, other_month_format)
        
        # Format dates from next month (after the last day, up to fill the week)
        days_after = 7 - last_day.dayOfWeek()
        for i in range(1, days_after + 1):
            next_date = last_day.addDays(i)
            if next_date.month() != month_shown:
                self.calendar.setDateTextFormat(next_date, other_month_format)
    
    def set_view(self, view: str):
        """Set calendar view."""
        self.current_view = view
        # Update button states
        for button in self.findChildren(QPushButton):
            if button.text() in ["Month", "Week", "Day"]:
                button.setChecked(button.text().lower() == view)
        # TODO: Implement view switching
    
    def set_appointments(self, appointments: List[Dict]):
        """Set appointments to display."""
        # TODO: Display appointments on calendar
        pass
    
    def get_selected_date(self) -> QDate:
        """Get selected date."""
        return self.calendar.selectedDate()

