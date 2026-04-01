import os
import tempfile
import unittest
from datetime import UTC, datetime

from src_v2.infrastructure.container import build_services


class V2QueryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "v2_query.db")
        self.services = build_services(self.db_path)
        login = self.services.auth_service.login("admin", "admin")
        assert login.ok
        self.session = login.value

    def tearDown(self) -> None:
        self.services.close()
        self.tmp_dir.cleanup()

    def test_lists_and_dashboard_metrics(self) -> None:
        patient = self.services.patient_service.create_patient(
            actor_role=self.session.role,
            first_name="Nora",
            last_name="Kim",
            phone="777",
            email="nora@example.com",
        )
        self.assertTrue(patient.ok, patient.error)

        appointment = self.services.appointment_service.create_appointment(
            actor_role=self.session.role,
            patient_id=patient.value.id,
            doctor_id="doctor-7",
            appointment_at=datetime.now(UTC),
            notes="Follow-up",
        )
        self.assertTrue(appointment.ok, appointment.error)

        invoice = self.services.billing_service.create_invoice(
            actor_role=self.session.role,
            patient_id=patient.value.id,
            appointment_id=appointment.value.id,
            amount=220.0,
        )
        self.assertTrue(invoice.ok, invoice.error)

        patients = self.services.query_service.list_patients(actor_role=self.session.role, limit=10)
        self.assertTrue(patients.ok, patients.error)
        self.assertGreaterEqual(len(patients.value), 1)

        appointments = self.services.query_service.list_appointments(actor_role=self.session.role, limit=10)
        self.assertTrue(appointments.ok, appointments.error)
        self.assertGreaterEqual(len(appointments.value), 1)

        invoices = self.services.query_service.list_invoices(actor_role=self.session.role, limit=10)
        self.assertTrue(invoices.ok, invoices.error)
        self.assertGreaterEqual(len(invoices.value), 1)

        metrics = self.services.query_service.dashboard_metrics(actor_role=self.session.role)
        self.assertTrue(metrics.ok, metrics.error)
        self.assertGreaterEqual(metrics.value.patients_total, 1)
        self.assertGreaterEqual(metrics.value.appointments_total, 1)
        self.assertGreaterEqual(metrics.value.invoices_total, 1)
        self.assertGreaterEqual(metrics.value.invoices_outstanding_total, 220.0)


if __name__ == "__main__":
    unittest.main()
