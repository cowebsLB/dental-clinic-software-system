from dataclasses import dataclass

from src_v2.application.policy import assert_permission
from src_v2.application.ports import AppointmentRepository, InvoiceRepository, PatientRepository
from src_v2.domain.models import Appointment, Invoice, Patient
from src_v2.shared.result import Result


@dataclass(frozen=True)
class DashboardMetrics:
    patients_total: int
    appointments_total: int
    invoices_total: int
    invoices_outstanding_total: float


class QueryService:
    def __init__(
        self,
        patients: PatientRepository,
        appointments: AppointmentRepository,
        invoices: InvoiceRepository,
    ):
        self._patients = patients
        self._appointments = appointments
        self._invoices = invoices

    def list_patients(self, actor_role: str, limit: int = 100) -> Result[list[Patient]]:
        try:
            assert_permission(actor_role, "patients:read")
            return Result.success(self._patients.list_all(limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def list_appointments(self, actor_role: str, limit: int = 100) -> Result[list[Appointment]]:
        try:
            assert_permission(actor_role, "appointments:read")
            return Result.success(self._appointments.list_all(limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def list_invoices(self, actor_role: str, limit: int = 100) -> Result[list[Invoice]]:
        try:
            assert_permission(actor_role, "billing:read")
            return Result.success(self._invoices.list_all(limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def dashboard_metrics(self, actor_role: str) -> Result[DashboardMetrics]:
        try:
            assert_permission(actor_role, "patients:read")
            assert_permission(actor_role, "appointments:read")
            assert_permission(actor_role, "billing:read")
            invoices = self._invoices.list_all(limit=5000)
            outstanding = sum(i.amount for i in invoices if i.status in {"unpaid", "pending", "overdue"})
            metrics = DashboardMetrics(
                patients_total=self._patients.count_all(),
                appointments_total=self._appointments.count_all(),
                invoices_total=self._invoices.count_all(),
                invoices_outstanding_total=outstanding,
            )
            return Result.success(metrics)
        except Exception as exc:
            return Result.failure(str(exc))
