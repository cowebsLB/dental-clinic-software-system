import uuid
from datetime import UTC, datetime

from src_v2.application.policy import assert_permission
from src_v2.application.ports import AppointmentRepository, PatientRepository
from src_v2.domain.models import Appointment
from src_v2.domain.rules import require_non_empty
from src_v2.shared.result import Result


class AppointmentService:
    def __init__(self, appointments: AppointmentRepository, patients: PatientRepository):
        self._appointments = appointments
        self._patients = patients

    def create_appointment(
        self,
        actor_role: str,
        patient_id: str,
        doctor_id: str,
        appointment_at: datetime,
        notes: str = "",
    ) -> Result[Appointment]:
        try:
            assert_permission(actor_role, "appointments:write")
            require_non_empty(patient_id, "patient_id")
            require_non_empty(doctor_id, "doctor_id")
            patient = self._patients.get(patient_id)
            if not patient:
                return Result.failure("Patient not found")
            now = datetime.now(UTC)
            appointment = Appointment(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_at=appointment_at,
                status="scheduled",
                notes=notes.strip(),
                created_at=now,
                updated_at=now,
            )
            self._appointments.create(appointment)
            return Result.success(appointment)
        except Exception as exc:
            return Result.failure(str(exc))
