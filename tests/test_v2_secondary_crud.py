import os
import tempfile
import unittest

from src_v2.infrastructure.container import build_services


class V2SecondaryCrudTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "v2_secondary_crud.db")
        self.services = build_services(self.db_path)
        login = self.services.auth_service.login("admin", "admin")
        assert login.ok
        self.session = login.value
        patient = self.services.patient_service.create_patient(
            actor_role=self.session.role,
            first_name="Ivy",
            last_name="Chen",
            phone="999",
            email="ivy@example.com",
        )
        assert patient.ok
        self.patient_id = patient.value.id

    def tearDown(self) -> None:
        self.services.close()
        self.tmp_dir.cleanup()

    def test_secondary_update_delete_flows(self) -> None:
        doctor = self.services.operations_service.create_doctor(self.session.role, "Dr Ivy", "Oral Surgery")
        room = self.services.operations_service.create_room(self.session.role, "B-01", "Surgery")
        equipment = self.services.operations_service.create_equipment(self.session.role, "Light", "Operatory")
        self.assertTrue(doctor.ok and room.ok and equipment.ok)

        deactivate_doctor = self.services.operations_service.set_doctor_active(
            self.session.role,
            doctor.value.id,
            False,
        )
        self.assertTrue(deactivate_doctor.ok and deactivate_doctor.value)

        mark_room_busy = self.services.operations_service.set_room_availability(
            self.session.role,
            room.value.id,
            False,
        )
        self.assertTrue(mark_room_busy.ok and mark_room_busy.value)

        mark_equipment_repair = self.services.operations_service.set_equipment_status(
            self.session.role,
            equipment.value.id,
            "maintenance",
        )
        self.assertTrue(mark_equipment_repair.ok and mark_equipment_repair.value)

        prescription = self.services.clinical_service.create_prescription(
            self.session.role,
            self.patient_id,
            doctor.value.id,
            "Metronidazole",
            "250mg",
            "After meals",
        )
        note = self.services.clinical_service.create_clinical_note(
            self.session.role,
            self.patient_id,
            doctor.value.id,
            "Post-op check required.",
        )
        claim = self.services.insurance_service.create_claim(
            self.session.role,
            self.patient_id,
            "PrimeCare",
            "PC-100",
            110.0,
        )
        self.assertTrue(prescription.ok and note.ok and claim.ok)

        claim_paid = self.services.insurance_service.set_claim_status(self.session.role, claim.value.id, "paid")
        self.assertTrue(claim_paid.ok and claim_paid.value)

        delete_note = self.services.clinical_service.delete_clinical_note(self.session.role, note.value.id)
        delete_prescription = self.services.clinical_service.delete_prescription(self.session.role, prescription.value.id)
        delete_claim = self.services.insurance_service.delete_claim(self.session.role, claim.value.id)
        delete_doctor = self.services.operations_service.delete_doctor(self.session.role, doctor.value.id)
        delete_room = self.services.operations_service.delete_room(self.session.role, room.value.id)
        delete_equipment = self.services.operations_service.delete_equipment(self.session.role, equipment.value.id)

        self.assertTrue(delete_note.ok and delete_note.value)
        self.assertTrue(delete_prescription.ok and delete_prescription.value)
        self.assertTrue(delete_claim.ok and delete_claim.value)
        self.assertTrue(delete_doctor.ok and delete_doctor.value)
        self.assertTrue(delete_room.ok and delete_room.value)
        self.assertTrue(delete_equipment.ok and delete_equipment.value)


if __name__ == "__main__":
    unittest.main()
