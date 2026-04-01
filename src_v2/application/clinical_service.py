import uuid
from datetime import UTC, datetime

from src_v2.application.policy import assert_permission
from src_v2.application.ports import ClinicalNoteRepository, PatientRepository, PrescriptionRepository
from src_v2.domain.models import ClinicalNote, Prescription
from src_v2.domain.rules import require_non_empty
from src_v2.shared.result import Result


class ClinicalService:
    def __init__(
        self,
        prescriptions: PrescriptionRepository,
        notes: ClinicalNoteRepository,
        patients: PatientRepository,
    ):
        self._prescriptions = prescriptions
        self._notes = notes
        self._patients = patients

    def create_prescription(
        self,
        actor_role: str,
        patient_id: str,
        doctor_id: str,
        medication: str,
        dosage: str,
        instructions: str = "",
    ) -> Result[Prescription]:
        try:
            assert_permission(actor_role, "appointments:write")
            require_non_empty(patient_id, "patient_id")
            require_non_empty(doctor_id, "doctor_id")
            require_non_empty(medication, "medication")
            if not self._patients.get(patient_id):
                return Result.failure("Patient not found")
            now = datetime.now(UTC)
            prescription = Prescription(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                doctor_id=doctor_id,
                medication=medication.strip(),
                dosage=dosage.strip(),
                instructions=instructions.strip(),
                created_at=now,
                updated_at=now,
            )
            self._prescriptions.create(prescription)
            return Result.success(prescription)
        except Exception as exc:
            return Result.failure(str(exc))

    def create_clinical_note(
        self,
        actor_role: str,
        patient_id: str,
        doctor_id: str,
        note: str,
    ) -> Result[ClinicalNote]:
        try:
            assert_permission(actor_role, "appointments:write")
            require_non_empty(note, "note")
            if not self._patients.get(patient_id):
                return Result.failure("Patient not found")
            now = datetime.now(UTC)
            clinical_note = ClinicalNote(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                doctor_id=doctor_id,
                note=note.strip(),
                created_at=now,
                updated_at=now,
            )
            self._notes.create(clinical_note)
            return Result.success(clinical_note)
        except Exception as exc:
            return Result.failure(str(exc))
