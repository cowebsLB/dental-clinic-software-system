import os
import tempfile
import unittest
from datetime import UTC, datetime

from src_v2.infrastructure.container import build_services


class V2BackendFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "v2_test.db")
        self.services = build_services(self.db_path)

    def tearDown(self) -> None:
        self.services.close()
        self.tmp_dir.cleanup()

    def test_admin_login_and_core_flow(self) -> None:
        login = self.services.auth_service.login("admin", "admin")
        self.assertTrue(login.ok, login.error)
        session = login.value
        self.assertIsNotNone(session)

        created_patient = self.services.patient_service.create_patient(
            actor_role=session.role,
            first_name="Jane",
            last_name="Doe",
            phone="12345",
            email="jane@example.com",
        )
        self.assertTrue(created_patient.ok, created_patient.error)
        patient = created_patient.value
        self.assertIsNotNone(patient)

        created_appointment = self.services.appointment_service.create_appointment(
            actor_role=session.role,
            patient_id=patient.id,
            doctor_id="doctor-1",
            appointment_at=datetime.now(UTC),
            notes="Initial consultation",
        )
        self.assertTrue(created_appointment.ok, created_appointment.error)
        appointment = created_appointment.value
        self.assertIsNotNone(appointment)

        created_invoice = self.services.billing_service.create_invoice(
            actor_role=session.role,
            patient_id=patient.id,
            appointment_id=appointment.id,
            amount=350.0,
        )
        self.assertTrue(created_invoice.ok, created_invoice.error)


if __name__ == "__main__":
    unittest.main()
