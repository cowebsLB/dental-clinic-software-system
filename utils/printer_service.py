"""Print service integration."""

import logging
from typing import Optional
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QTextDocument

logger = logging.getLogger(__name__)


class PrinterService:
    """Manages printing operations."""
    
    def print_text(self, text: str, title: str = "Print") -> bool:
        """Print text content."""
        try:
            printer = QPrinter()
            dialog = QPrintDialog(printer)
            
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                doc = QTextDocument()
                doc.setPlainText(text)
                doc.print_(printer)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error printing: {e}")
            return False
    
    def print_html(self, html: str, title: str = "Print") -> bool:
        """Print HTML content."""
        try:
            printer = QPrinter()
            dialog = QPrintDialog(printer)
            
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                doc = QTextDocument()
                doc.setHtml(html)
                doc.print_(printer)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error printing HTML: {e}")
            return False


# Global instance
printer_service = PrinterService()

