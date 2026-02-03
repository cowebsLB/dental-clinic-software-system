"""Financial reports."""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
from database.local_cache import local_cache

logger = logging.getLogger(__name__)


class FinancialReports:
    """Generates financial reports."""
    
    def get_revenue_report(self, start_date: str, end_date: str) -> Dict:
        """Get revenue report for date range."""
        try:
            # Get payments in date range
            all_payments = local_cache.query('payments')
            
            filtered_payments = [
                p for p in all_payments
                if start_date <= p.get('payment_date_utc', '')[:10] <= end_date
                and p.get('status') == 'completed'
            ]
            
            total_revenue = sum(p.get('amount', 0) for p in filtered_payments)
            
            # Group by payment method
            by_method = {}
            for payment in filtered_payments:
                method = payment.get('payment_method', 'unknown')
                by_method[method] = by_method.get(method, 0) + payment.get('amount', 0)
            
            return {
                'total_revenue': total_revenue,
                'payment_count': len(filtered_payments),
                'by_method': by_method,
                'start_date': start_date,
                'end_date': end_date
            }
        except Exception as e:
            logger.error(f"Error generating revenue report: {e}")
            return {}
    
    def get_outstanding_receivables(self) -> Dict:
        """Get outstanding receivables."""
        try:
            invoices = local_cache.query('invoices')
            outstanding = [
                inv for inv in invoices
                if inv.get('status') in ['pending', 'overdue']
            ]
            
            total_outstanding = sum(inv.get('total', 0) for inv in outstanding)
            
            # Aging analysis
            now = datetime.now()
            aging = {
                '0-30': 0,
                '31-60': 0,
                '61-90': 0,
                '90+': 0
            }
            
            for inv in outstanding:
                due_date_str = inv.get('due_date', '')
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str)
                        days_past = (now - due_date).days
                        
                        if days_past <= 30:
                            aging['0-30'] += inv.get('total', 0)
                        elif days_past <= 60:
                            aging['31-60'] += inv.get('total', 0)
                        elif days_past <= 90:
                            aging['61-90'] += inv.get('total', 0)
                        else:
                            aging['90+'] += inv.get('total', 0)
                    except:
                        pass
            
            return {
                'total_outstanding': total_outstanding,
                'invoice_count': len(outstanding),
                'aging': aging
            }
        except Exception as e:
            logger.error(f"Error getting outstanding receivables: {e}")
            return {}


# Global instance
financial_reports = FinancialReports()

