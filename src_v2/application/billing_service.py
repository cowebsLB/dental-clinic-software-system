import uuid
from datetime import UTC, datetime

from src_v2.application.policy import assert_permission
from src_v2.application.ports import AppointmentRepository, InvoiceRepository, PatientRepository
from src_v2.domain.models import Invoice
from src_v2.domain.rules import require_non_negative
from src_v2.shared.result import Result


class BillingService:
    def __init__(
        self,
        invoices: InvoiceRepository,
        patients: PatientRepository,
        appointments: AppointmentRepository,
    ):
        self._invoices = invoices
        self._patients = patients
        self._appointments = appointments

    def create_invoice(
        self,
        actor_role: str,
        patient_id: str,
        appointment_id: str,
        amount: float,
    ) -> Result[Invoice]:
        try:
            assert_permission(actor_role, "billing:write")
            require_non_negative(amount, "amount")
            if not self._patients.get(patient_id):
                return Result.failure("Patient not found")
            if not self._appointments.get(appointment_id):
                return Result.failure("Appointment not found")
            now = datetime.now(UTC)
            invoice = Invoice(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                appointment_id=appointment_id,
                amount=amount,
                status="unpaid",
                created_at=now,
                updated_at=now,
            )
            self._invoices.create(invoice)
            return Result.success(invoice)
        except Exception as exc:
            return Result.failure(str(exc))
