import os
import tempfile
import unittest
from datetime import UTC, datetime

from src_v2.infrastructure.container import build_services


class V2ClinicalInsuranceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "v2_ci.db")
        self.services = build_services(self.db_path)
        login = self.services.auth_service.login("admin", "admin")
        assert login.ok
        self.session = login.value
        patient_result = self.services.patient_service.create_patient(
            actor_role=self.session.role,
            first_name="Sam",
            last_name="Lee",
            phone="555-555",
            email="sam@example.com",
        )
        assert patient_result.ok
        self.patient = patient_result.value
        appointment_result = self.services.appointment_service.create_appointment(
            actor_role=self.session.role,
            patient_id=self.patient.id,
            doctor_id="doc-1",
            appointment_at=datetime.now(UTC),
        )
        assert appointment_result.ok

    def tearDown(self) -> None:
        self.services.close()
        self.tmp_dir.cleanup()

    def test_create_prescription_note_and_claim(self) -> None:
        prescription = self.services.clinical_service.create_prescription(
            actor_role=self.session.role,
            patient_id=self.patient.id,
            doctor_id="doc-1",
            medication="Ibuprofen",
            dosage="200mg",
            instructions="Take after meals",
        )
        self.assertTrue(prescription.ok, prescription.error)

        note = self.services.clinical_service.create_clinical_note(
            actor_role=self.session.role,
            patient_id=self.patient.id,
            doctor_id="doc-1",
            note="Patient improving.",
        )
        self.assertTrue(note.ok, note.error)

        claim = self.services.insurance_service.create_claim(
            actor_role=self.session.role,
            patient_id=self.patient.id,
            provider_name="Acme Insurance",
            claim_number="CLM-001",
            amount=120.0,
        )
        self.assertTrue(claim.ok, claim.error)


if __name__ == "__main__":
    unittest.main()
