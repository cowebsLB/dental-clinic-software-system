import uuid
from datetime import datetime, UTC

from src_v2.application.policy import assert_permission
from src_v2.application.ports import PatientRepository
from src_v2.domain.models import Patient
from src_v2.domain.rules import require_non_empty
from src_v2.shared.result import Result


class PatientService:
    def __init__(self, patients: PatientRepository):
        self._patients = patients

    def create_patient(
        self,
        actor_role: str,
        first_name: str,
        last_name: str,
        phone: str = "",
        email: str = "",
    ) -> Result[Patient]:
        try:
            assert_permission(actor_role, "patients:write")
            require_non_empty(first_name, "first_name")
            require_non_empty(last_name, "last_name")
            now = datetime.now(UTC)
            patient = Patient(
                id=str(uuid.uuid4()),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                phone=phone.strip(),
                email=email.strip(),
                created_at=now,
                updated_at=now,
            )
            self._patients.create(patient)
            return Result.success(patient)
        except Exception as exc:  # Keep service boundary stable.
            return Result.failure(str(exc))
