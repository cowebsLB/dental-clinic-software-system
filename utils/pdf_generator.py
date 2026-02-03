"""PDF generation for invoices and reports."""

import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generates PDF documents."""
    
    def generate_invoice(self, invoice_data: dict, output_path: str) -> bool:
        """Generate invoice PDF."""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("Invoice", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Invoice details
            invoice_number = invoice_data.get('invoice_number', 'N/A')
            issue_date = invoice_data.get('issue_date', 'N/A')
            
            details = [
                ['Invoice Number:', invoice_number],
                ['Issue Date:', issue_date],
                ['Status:', invoice_data.get('status', 'N/A')]
            ]
            
            details_table = Table(details, colWidths=[150, 200])
            details_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ]))
            story.append(details_table)
            story.append(Spacer(1, 12))
            
            # Invoice items
            items = invoice_data.get('items', [])
            if items:
                item_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
                for item in items:
                    item_data.append([
                        item.get('description', ''),
                        str(item.get('quantity', 0)),
                        f"${item.get('unit_price', 0):.2f}",
                        f"${item.get('total', 0):.2f}"
                    ])
                
                items_table = Table(item_data)
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(items_table)
            
            # Totals
            story.append(Spacer(1, 12))
            totals = [
                ['Subtotal:', f"${invoice_data.get('subtotal', 0):.2f}"],
                ['Tax:', f"${invoice_data.get('tax', 0):.2f}"],
                ['Discount:', f"${invoice_data.get('discount', 0):.2f}"],
                ['Total:', f"${invoice_data.get('total', 0):.2f}"]
            ]
            
            totals_table = Table(totals, colWidths=[150, 100])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            story.append(totals_table)
            
            # Build PDF
            doc.build(story)
            return True
        
        except Exception as e:
            logger.error(f"Error generating invoice PDF: {e}")
            return False


# Global instance
pdf_generator = PDFGenerator()

