import os
import tempfile
import unittest

from src_v2.infrastructure.container import build_services


class V2SecondaryQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "v2_secondary.db")
        self.services = build_services(self.db_path)
        login = self.services.auth_service.login("admin", "admin")
        assert login.ok
        self.session = login.value
        patient = self.services.patient_service.create_patient(
            actor_role=self.session.role,
            first_name="Lina",
            last_name="Park",
            phone="888",
            email="lina@example.com",
        )
        assert patient.ok
        self.patient_id = patient.value.id

    def tearDown(self) -> None:
        self.services.close()
        self.tmp_dir.cleanup()

    def test_secondary_list_queries(self) -> None:
        doctor = self.services.operations_service.create_doctor(
            actor_role=self.session.role,
            name="Dr Lee",
            specialization="General",
        )
        self.assertTrue(doctor.ok, doctor.error)
        room = self.services.operations_service.create_room(
            actor_role=self.session.role,
            room_number="A-01",
            room_type="Exam",
        )
        self.assertTrue(room.ok, room.error)
        equipment = self.services.operations_service.create_equipment(
            actor_role=self.session.role,
            name="Scaler",
            equipment_type="Cleaning",
        )
        self.assertTrue(equipment.ok, equipment.error)

        prescription = self.services.clinical_service.create_prescription(
            actor_role=self.session.role,
            patient_id=self.patient_id,
            doctor_id=doctor.value.id,
            medication="Amoxicillin",
            dosage="500mg",
            instructions="Twice daily",
        )
        self.assertTrue(prescription.ok, prescription.error)
        note = self.services.clinical_service.create_clinical_note(
            actor_role=self.session.role,
            patient_id=self.patient_id,
            doctor_id=doctor.value.id,
            note="Stable vitals.",
        )
        self.assertTrue(note.ok, note.error)
        claim = self.services.insurance_service.create_claim(
            actor_role=self.session.role,
            patient_id=self.patient_id,
            provider_name="CarePlus",
            claim_number="CP-99",
            amount=90.0,
        )
        self.assertTrue(claim.ok, claim.error)

        doctors = self.services.operations_service.list_doctors(actor_role=self.session.role)
        self.assertTrue(doctors.ok, doctors.error)
        self.assertGreaterEqual(len(doctors.value), 1)
        rooms = self.services.operations_service.list_rooms(actor_role=self.session.role)
        self.assertTrue(rooms.ok, rooms.error)
        self.assertGreaterEqual(len(rooms.value), 1)
        equipment_list = self.services.operations_service.list_equipment(actor_role=self.session.role)
        self.assertTrue(equipment_list.ok, equipment_list.error)
        self.assertGreaterEqual(len(equipment_list.value), 1)

        prescriptions = self.services.clinical_service.list_prescriptions_for_patient(
            actor_role=self.session.role,
            patient_id=self.patient_id,
        )
        self.assertTrue(prescriptions.ok, prescriptions.error)
        self.assertGreaterEqual(len(prescriptions.value), 1)
        notes = self.services.clinical_service.list_clinical_notes_for_patient(
            actor_role=self.session.role,
            patient_id=self.patient_id,
        )
        self.assertTrue(notes.ok, notes.error)
        self.assertGreaterEqual(len(notes.value), 1)
        claims = self.services.insurance_service.list_claims_for_patient(
            actor_role=self.session.role,
            patient_id=self.patient_id,
        )
        self.assertTrue(claims.ok, claims.error)
        self.assertGreaterEqual(len(claims.value), 1)


if __name__ == "__main__":
    unittest.main()
